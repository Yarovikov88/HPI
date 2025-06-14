"""
Модуль для генерации AI-рекомендаций с использованием OpenAI GPT-3.5 Turbo.
"""
import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from ..parsers import ProData, HistoricalReport
from ..generators import Recommendation, ActionStep, Evidence

# Загружаем переменные окружения
load_dotenv()

# Настраиваем OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class SphereContext:
    """Контекст сферы для генерации рекомендаций."""
    name: str
    current_score: float
    previous_score: Optional[float]
    change_percent: float
    metrics: List[Dict]
    problems: List[str]
    goals: List[str]
    blockers: List[str]
    historical_data: List[Dict]


class AIRecommendationEngine:
    """Движок для генерации AI-рекомендаций."""

    def __init__(self):
        """Инициализация движка."""
        self.logger = logging.getLogger(__name__)
        self.model = "gpt-3.5-turbo"  # Используем GPT-3.5 Turbo
        
        # Оптимизированный системный промпт для GPT-3.5
        self.system_prompt = """Ты - эксперт по развитию человеческого потенциала в системе HPI (Human Potential Index).
Твоя задача - анализировать данные о сферах жизни человека и давать конкретные рекомендации для улучшения.

Правила для рекомендаций:
1. Конкретность: Каждый шаг должен быть четким и выполнимым
2. Измеримость: Должна быть возможность отследить прогресс
3. Реалистичность: Шаги должны быть выполнимы в указанные сроки
4. Основа на данных: Используй предоставленные метрики и историю

Структура рекомендации (строго в формате JSON):
{
    "title": "Краткое название (до 5 слов)",
    "description": "Одно предложение, описывающее суть",
    "action_steps": [
        {
            "description": "Конкретное действие",
            "expected_impact": 0.8,  // Число от 0 до 1
            "estimated_time": "2 недели",  // Реалистичная оценка
            "dependencies": []  // Список необходимых условий
        }
    ],
    "evidence": {
        "data_points": ["Факт 1", "Факт 2"],  // 2-3 ключевых наблюдения
        "correlations": ["Связь 1", "Связь 2"],  // 1-2 важные связи
        "historical_success": 0.85  // Число от 0 до 1
    }
}

ВАЖНО: Отвечай ТОЛЬКО в формате JSON. Не добавляй пояснений или дополнительного текста."""

    def _prepare_sphere_context(
        self,
        sphere: str,
        pro_data: ProData,
        history: List[HistoricalReport]
    ) -> SphereContext:
        """
        Подготавливает контекст сферы для AI.
        
        Args:
            sphere: Название сферы
            pro_data: PRO-данные
            history: История отчетов
            
        Returns:
            Объект контекста сферы
        """
        # Получаем текущую оценку
        current_score = pro_data.scores.get(sphere, 0.0)
        
        # Получаем предыдущую оценку
        previous_score = None
        if history:
            previous_score = history[-1].scores.get(sphere)
            
        # Вычисляем изменение
        change_percent = 0.0
        if previous_score and previous_score != 0:
            change_percent = ((current_score - previous_score) / abs(previous_score)) * 100
            
        # Собираем метрики
        metrics = []
        for metric in pro_data.metrics:
            if metric.sphere == sphere:
                metrics.append({
                    "name": metric.name,
                    "current": metric.current_value,
                    "target": metric.target_value,
                    "description": metric.description
                })
                
        # Собираем историю (только последние 3 записи для экономии токенов)
        historical_data = []
        for report in history[-3:]:
            if sphere in report.scores:
                historical_data.append({
                    "date": report.date.strftime("%Y-%m-%d"),
                    "score": report.scores[sphere],
                    "metrics": [
                        {"name": m.name, "value": m.current_value}
                        for m in report.metrics
                        if m.sphere == sphere
                    ]
                })
                
        return SphereContext(
            name=sphere,
            current_score=current_score,
            previous_score=previous_score,
            change_percent=change_percent,
            metrics=metrics,
            problems=pro_data.problems.get(sphere, []),
            goals=pro_data.goals.get(sphere, []),
            blockers=pro_data.blockers.get(sphere, []),
            historical_data=historical_data
        )

    def _format_prompt(
        self,
        context: SphereContext
    ) -> str:
        """
        Форматирует промпт для модели.
        
        Args:
            context: Контекст сферы
            
        Returns:
            Строка с промптом
        """
        # Оптимизированный промпт для GPT-3.5
        return f"""Создай рекомендацию для сферы "{context.name}" на основе данных:

ТЕКУЩЕЕ СОСТОЯНИЕ:
Оценка: {context.current_score:.1f} ({context.change_percent:+.1f}%)
Метрики: {json.dumps(context.metrics, ensure_ascii=False)}

ПРОБЛЕМЫ: {', '.join(context.problems) if context.problems else 'нет'}
ЦЕЛИ: {', '.join(context.goals) if context.goals else 'нет'}
БЛОКЕРЫ: {', '.join(context.blockers) if context.blockers else 'нет'}

ИСТОРИЯ (последние записи):
{json.dumps(context.historical_data, ensure_ascii=False)}

Создай рекомендацию в формате JSON с учетом этих данных. Рекомендация должна быть конкретной и реалистичной."""

    def _parse_ai_response(
        self,
        response: str
    ) -> Dict:
        """
        Парсит ответ модели в структуру рекомендации.
        
        Args:
            response: JSON-ответ от модели
            
        Returns:
            Словарь с данными рекомендации
        """
        try:
            # Находим JSON в ответе
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("JSON не найден в ответе")
                
            json_str = response[start:end]
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга ответа AI: {e}")
            self.logger.debug(f"Ответ AI: {response}")
            return None

    def generate_recommendation(
        self,
        sphere: str,
        pro_data: ProData,
        history: List[HistoricalReport]
    ) -> Optional[Recommendation]:
        """
        Генерирует AI-рекомендацию для сферы.
        
        Args:
            sphere: Название сферы
            pro_data: PRO-данные
            history: История отчетов
            
        Returns:
            Объект рекомендации или None в случае ошибки
        """
        try:
            # Подготавливаем контекст
            context = self._prepare_sphere_context(sphere, pro_data, history)
            
            # Генерируем промпт
            prompt = self._format_prompt(context)
            
            # Делаем запрос к API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,  # Уменьшаем для экономии
                presence_penalty=0.3,  # Поощряем разнообразие
                frequency_penalty=0.3   # Избегаем повторений
            )
            
            # Парсим ответ
            result = self._parse_ai_response(response.choices[0].message.content)
            if not result:
                return None
                
            # Создаем объект рекомендации
            action_steps = [
                ActionStep(
                    description=step["description"],
                    expected_impact=step["expected_impact"],
                    estimated_time=step["estimated_time"],
                    dependencies=step.get("dependencies", [])
                )
                for step in result["action_steps"]
            ]
            
            evidence = Evidence(
                data_points=result["evidence"]["data_points"],
                correlations=result["evidence"]["correlations"],
                historical_success=result["evidence"]["historical_success"]
            )
            
            return Recommendation(
                sphere=sphere,
                priority=3,  # Средний приоритет по умолчанию
                title=result["title"],
                description=result["description"],
                action_steps=action_steps,
                evidence=evidence,
                related_spheres=[]  # Пока не используем
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации рекомендации: {e}", exc_info=True)
            return None 