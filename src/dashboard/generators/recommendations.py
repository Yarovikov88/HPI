"""
Модуль для генерации AI-рекомендаций в системе HPI.
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..parsers import ProData, HistoricalReport
from ..normalizers import SphereNormalizer


@dataclass
class ActionStep:
    """Шаг действия в рекомендации."""
    description: str
    expected_impact: float  # Ожидаемое влияние (0-1)
    estimated_time: str    # Например, "30 минут", "2 недели"
    dependencies: List[str]  # Зависимости для выполнения


@dataclass
class Evidence:
    """Доказательная база для рекомендации."""
    data_points: List[str]  # Конкретные метрики или наблюдения
    correlations: List[str]  # Связи с другими метриками/сферами
    historical_success: float  # Исторический успех рекомендации (0-1)


@dataclass
class Recommendation:
    """Рекомендация для конкретной сферы."""
    sphere: str
    priority: int  # 1-5, где 5 - наивысший приоритет
    title: str
    description: str
    action_steps: List[ActionStep]
    evidence: Evidence
    related_spheres: List[str]


class RecommendationGenerator:
    """Генератор рекомендаций на основе данных HPI."""

    def __init__(self):
        """Инициализация генератора."""
        self.sphere_normalizer = SphereNormalizer()
        self.logger = logging.getLogger(__name__)

        # Базовые шаблоны рекомендаций для каждой сферы
        self.base_recommendations = {
            "Отношения с любимыми": {
                "templates": [
                    {
                        "title": "Качественное время вместе",
                        "description": "Уделите время совместным активностям, глубокому общению и поддержке друг друга. Развивайте эмоциональную близость и совместные традиции.",
                        "actions": [
                            "Запланируйте еженедельное свидание или совместную прогулку",
                            "Создайте новую семейную традицию",
                            "Практикуйте активное слушание и поддержку",
                            "Обсудите совместные цели и мечты"
                        ]
                    }
                ]
            },
            "Отношения с родными": {
                "templates": [
                    {
                        "title": "Укрепление семейных связей",
                        "description": "Поддерживайте регулярный контакт и участие в жизни семьи. Создавайте позитивные воспоминания и поддерживайте друг друга в трудные моменты.",
                        "actions": [
                            "Организуйте семейный ужин или встречу",
                            "Звоните родителям и родственникам по расписанию",
                            "Участвуйте в семейных традициях и праздниках",
                            "Обсудите важные семейные вопросы открыто и с уважением"
                        ]
                    }
                ]
            },
            "Друзья": {
                "templates": [
                    {
                        "title": "Активное общение и поддержка",
                        "description": "Поддерживайте и развивайте дружеские связи, проявляйте инициативу в общении и совместных активностях.",
                        "actions": [
                            "Организуйте встречу или совместное мероприятие",
                            "Инициируйте новую групповую активность (игра, прогулка, проект)",
                            "Регулярно поддерживайте связь, интересуйтесь делами друзей",
                            "Помогайте друзьям в сложных ситуациях"
                        ]
                    }
                ]
            },
            "Карьера": {
                "templates": [
                    {
                        "title": "Профессиональное развитие",
                        "description": "Сфокусируйтесь на росте, новых навыках и расширении профессиональных возможностей.",
                        "actions": [
                            "Составьте план развития на ближайший квартал",
                            "Изучите новую технологию или навык",
                            "Расширьте профессиональную сеть (нетворкинг)",
                            "Поставьте конкретную карьерную цель и начните её реализовывать"
                        ]
                    }
                ]
            },
            "Физическое здоровье": {
                "templates": [
                    {
                        "title": "Здоровый образ жизни",
                        "description": "Улучшайте физическую форму, самочувствие и энергию через регулярные тренировки, питание и отдых.",
                        "actions": [
                            "Составьте индивидуальный план тренировок",
                            "Оптимизируйте режим сна и отдыха",
                            "Улучшите питание: добавьте больше овощей и белка",
                            "Поставьте цель по шагам или активности на неделю"
                        ]
                    }
                ]
            },
            "Ментальное здоровье": {
                "templates": [
                    {
                        "title": "Ментальный баланс и устойчивость",
                        "description": "Работайте над психологическим благополучием, стрессоустойчивостью и внутренней гармонией.",
                        "actions": [
                            "Практикуйте медитацию или дыхательные упражнения",
                            "Ведите дневник благодарности или настроения",
                            "Установите здоровые границы в общении и работе",
                            "Обратитесь к специалисту при необходимости"
                        ]
                    }
                ]
            },
            "Хобби и увлечения": {
                "templates": [
                    {
                        "title": "Творческая реализация и отдых",
                        "description": "Развивайте свои интересы, пробуйте новое и находите единомышленников для совместных занятий.",
                        "actions": [
                            "Попробуйте новое хобби или творческое занятие",
                            "Углубите существующие навыки (мастер-классы, курсы)",
                            "Найдите единомышленников для совместных проектов",
                            "Выделяйте время на отдых и восстановление"
                        ]
                    }
                ]
            },
            "Благосостояние": {
                "templates": [
                    {
                        "title": "Финансовая стабильность и рост",
                        "description": "Улучшайте финансовое положение, планируйте бюджет и изучайте новые возможности для дохода.",
                        "actions": [
                            "Создайте финансовый план на месяц",
                            "Оптимизируйте расходы и найдите возможности для экономии",
                            "Изучите основы инвестирования или дополнительного дохода",
                            "Поставьте финансовую цель и начните её реализовывать"
                        ]
                    }
                ]
            }
        }

    def _analyze_sphere_data(
        self,
        sphere: str,
        pro_data: ProData,
        history: List[HistoricalReport]
    ) -> Dict:
        """
        Анализирует данные сферы для генерации рекомендаций.
        
        Args:
            sphere: Название сферы
            pro_data: PRO-данные пользователя
            history: История отчетов
            
        Returns:
            Словарь с результатами анализа
        """
        analysis = {
            "current_score": None,
            "trend": "stable",
            "problems": [],
            "goals": [],
            "blockers": [],
            "metrics": []
        }
        
        # Получаем текущую оценку из истории
        if history:
            latest = history[-1]
            analysis["current_score"] = latest.scores.get(sphere)
            
            # Анализируем тренд
            if len(history) > 1:
                prev_score = history[-2].scores.get(sphere)
                if prev_score and analysis["current_score"]:
                    diff = analysis["current_score"] - prev_score
                    if diff > 0.5:
                        analysis["trend"] = "improving"
                    elif diff < -0.5:
                        analysis["trend"] = "declining"
        
        # Добавляем PRO-данные
        if sphere in pro_data.problems:
            analysis["problems"].append(pro_data.problems[sphere])
        if sphere in pro_data.goals:
            analysis["goals"].append(pro_data.goals[sphere])
        if sphere in pro_data.blockers:
            analysis["blockers"].append(pro_data.blockers[sphere])
            
        # Добавляем метрики
        for metric in pro_data.metrics:
            if metric.sphere == sphere:
                analysis["metrics"].append({
                    "name": metric.name,
                    "current": metric.current_value,
                    "target": metric.target_value
                })
                
        return analysis

    def _generate_action_steps(
        self,
        sphere: str,
        analysis: Dict
    ) -> List[ActionStep]:
        """
        Генерирует шаги действий на основе анализа.
        
        Args:
            sphere: Название сферы
            analysis: Результаты анализа
            
        Returns:
            Список шагов действий
        """
        steps = []
        base_actions = self.base_recommendations[sphere]["templates"][0]["actions"]
        
        # Добавляем базовые действия
        for action in base_actions:
            steps.append(
                ActionStep(
                    description=action,
                    expected_impact=0.7,
                    estimated_time="1 неделя",
                    dependencies=[]
                )
            )
            
        # Добавляем специфичные действия на основе анализа
        if analysis["problems"]:
            steps.append(
                ActionStep(
                    description=f"Решить проблему: {analysis['problems'][0]}",
                    expected_impact=0.8,
                    estimated_time="2 недели",
                    dependencies=[]
                )
            )
            
        if analysis["goals"]:
            steps.append(
                ActionStep(
                    description=f"Работать над целью: {analysis['goals'][0]}",
                    expected_impact=0.9,
                    estimated_time="1 месяц",
                    dependencies=[]
                )
            )
            
        return steps

    def _generate_evidence(
        self,
        sphere: str,
        analysis: Dict
    ) -> Evidence:
        """
        Генерирует доказательную базу для рекомендации.
        
        Args:
            sphere: Название сферы
            analysis: Результаты анализа
            
        Returns:
            Объект Evidence
        """
        data_points = []
        correlations = []
        
        # Добавляем текущую оценку
        if analysis["current_score"]:
            data_points.append(f"Текущая оценка сферы: {analysis['current_score']}")
            
        # Добавляем тренд
        data_points.append(f"Тренд: {analysis['trend']}")
        
        # Добавляем метрики
        for metric in analysis["metrics"]:
            data_points.append(
                f"Метрика '{metric['name']}': {metric['current']} -> {metric['target']}"
            )
            
        # Добавляем корреляции с другими сферами
        # TODO: Реализовать анализ корреляций
        
        return Evidence(
            data_points=data_points,
            correlations=correlations,
            historical_success=0.8  # TODO: Реализовать расчет исторического успеха
        )

    def generate(
        self,
        pro_data: ProData,
        history: List[HistoricalReport]
    ) -> Dict[str, Recommendation]:
        """
        Генерирует рекомендации для всех сфер.
        
        Args:
            pro_data: PRO-данные пользователя
            history: История отчетов
            
        Returns:
            Словарь {сфера: рекомендация}
        """
        recommendations = {}
        
        for sphere in self.base_recommendations:
            # Анализируем данные сферы
            analysis = self._analyze_sphere_data(sphere, pro_data, history)
            
            # Получаем базовый шаблон
            template = self.base_recommendations[sphere]["templates"][0]
            
            # Генерируем шаги действий
            action_steps = self._generate_action_steps(sphere, analysis)
            
            # Генерируем доказательную базу
            evidence = self._generate_evidence(sphere, analysis)
            
            # Определяем приоритет
            priority = 3  # По умолчанию средний
            if analysis["problems"]:
                priority = 4
            if analysis["trend"] == "declining":
                priority = 5
            
            # Создаем рекомендацию
            recommendations[sphere] = Recommendation(
                sphere=sphere,
                priority=priority,
                title=template["title"],
                description=template["description"],
                action_steps=action_steps,
                evidence=evidence,
                related_spheres=[]  # TODO: Реализовать поиск связанных сфер
            )
            
        return recommendations

    def generate_basic(self, context):
        """
        Возвращает базовые рекомендации для сферы.
        context: dict с ключами (например, 'sphere', 'score', 'problems', 'goals', ...)
        """
        sphere = context.get('sphere', 'Сфера')
        normalizer = SphereNormalizer()
        normalized = normalizer.normalize(sphere)
        base = self.base_recommendations.get(normalized)
        if not base:
            emoji = normalizer.get_emoji(normalized)
            emoji_part = f"{emoji} " if emoji else ""
            print(f"[DEBUG] Нет шаблона для сферы: '{sphere}' (нормализовано: '{normalized}'). Доступные: {list(self.base_recommendations.keys())}")
            return [f"{emoji_part}попробуйте поставить конкретную цель и сделать первый шаг."]
        templates = base.get('templates', [])
        recs = []
        for tpl in templates:
            recs.append(f"{tpl['title']}: {tpl['description']} (например: {', '.join(tpl['actions'])})")
        return recs 