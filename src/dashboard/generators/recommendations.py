"""
Модуль для генерации AI-рекомендаций в системе HPI.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict, Union

from ..normalizers import SphereNormalizer
from ..parsers import HistoricalReport, ProData


class AnalysisDict(TypedDict):
    """Тип для результатов анализа сферы."""

    current_score: Optional[float]
    trend: str
    problems: List[str]
    goals: List[str]
    blockers: List[str]
    metrics: List[Dict[str, Any]]


class RecommendationTemplate(TypedDict):
    """Тип для шаблона рекомендации."""

    title: str
    description: str
    actions: List[str]


class SphereRecommendations(TypedDict):
    """Тип для рекомендаций сферы."""

    templates: List[RecommendationTemplate]


@dataclass
class ActionStep:
    """Шаг действия в рекомендации."""

    description: str
    expected_impact: float  # Ожидаемое влияние (0-1)
    estimated_time: str  # Например, "30 минут", "2 недели"
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
        self.base_recommendations: Dict[str, SphereRecommendations] = {
            "Отношения с любимыми": {
                "templates": [
                    {
                        "title": "Качественное время вместе",
                        "description": (
                            "Уделите время совместным активностям, глубокому общению "
                            "и поддержке друг друга. Развивайте эмоциональную близость "
                            "и совместные традиции."
                        ),
                        "actions": [
                            "Запланируйте еженедельное свидание или совместную "
                            "прогулку",
                            "Создайте новую семейную традицию",
                            "Практикуйте активное слушание и поддержку",
                            "Обсудите совместные цели и мечты",
                        ],
                    }
                ]
            },
            "Отношения с родными": {
                "templates": [
                    {
                        "title": "Укрепление семейных связей",
                        "description": (
                            "Поддерживайте регулярный контакт и участие в жизни семьи. "
                            "Создавайте позитивные воспоминания и поддерживайте друг "
                            "друга в трудные моменты."
                        ),
                        "actions": [
                            "Организуйте семейный ужин или встречу",
                            "Звоните родителям и родственникам по расписанию",
                            "Участвуйте в семейных традициях и праздниках",
                            "Обсудите важные семейные вопросы открыто и с уважением",
                        ],
                    }
                ]
            },
            "Друзья": {
                "templates": [
                    {
                        "title": "Активное общение и поддержка",
                        "description": (
                            "Поддерживайте и развивайте дружеские связи, проявляйте "
                            "инициативу в общении и совместных активностях."
                        ),
                        "actions": [
                            "Организуйте встречу или совместное мероприятие",
                            "Инициируйте новую групповую активность (игра, прогулка, проект)",
                            "Регулярно поддерживайте связь, интересуйтесь делами друзей",
                            "Помогайте друзьям в сложных ситуациях",
                        ],
                    }
                ]
            },
            "Карьера": {
                "templates": [
                    {
                        "title": "Профессиональное развитие",
                        "description": (
                            "Сфокусируйтесь на росте, новых навыках и расширении "
                            "профессиональных возможностей."
                        ),
                        "actions": [
                            "Составьте план развития на ближайший квартал",
                            "Изучите новую технологию или навык",
                            "Расширьте профессиональную сеть (нетворкинг)",
                            "Поставьте конкретную карьерную цель и начните её реализовывать",
                        ],
                    }
                ]
            },
            "Физическое здоровье": {
                "templates": [
                    {
                        "title": "Здоровый образ жизни",
                        "description": (
                            "Улучшайте физическую форму, самочувствие и энергию через "
                            "регулярные тренировки, питание и отдых."
                        ),
                        "actions": [
                            "Составьте индивидуальный план тренировок",
                            "Оптимизируйте режим сна и отдыха",
                            "Улучшите питание: добавьте больше овощей и белка",
                            "Поставьте цель по шагам или активности на неделю",
                        ],
                    }
                ]
            },
            "Ментальное здоровье": {
                "templates": [
                    {
                        "title": "Ментальный баланс и устойчивость",
                        "description": (
                            "Работайте над психологическим благополучием, "
                            "стрессоустойчивостью и внутренней гармонией."
                        ),
                        "actions": [
                            "Практикуйте медитацию или дыхательные упражнения",
                            "Ведите дневник благодарности или настроения",
                            "Установите здоровые границы в общении и работе",
                            "Обратитесь к специалисту при необходимости",
                        ],
                    }
                ]
            },
            "Хобби и увлечения": {
                "templates": [
                    {
                        "title": "Творческая реализация и отдых",
                        "description": (
                            "Развивайте свои интересы, пробуйте новое и находите "
                            "единомышленников для совместных занятий."
                        ),
                        "actions": [
                            "Попробуйте новое хобби или творческое занятие",
                            "Углубите существующие навыки (мастер-классы, курсы)",
                            "Найдите единомышленников для совместных проектов",
                            "Выделяйте время на отдых и восстановление",
                        ],
                    }
                ]
            },
            "Благосостояние": {
                "templates": [
                    {
                        "title": "Финансовая стабильность и рост",
                        "description": (
                            "Улучшайте финансовое положение, планируйте бюджет и "
                            "изучайте новые возможности для дохода."
                        ),
                        "actions": [
                            "Создайте финансовый план на месяц",
                            "Оптимизируйте расходы и найдите возможности для экономии",
                            "Изучите основы инвестирования или дополнительного дохода",
                            "Поставьте финансовую цель и начните её реализовывать",
                        ],
                    }
                ]
            },
        }

    def _analyze_sphere_data(
        self, sphere: str, pro_data: ProData, history: List[HistoricalReport]
    ) -> AnalysisDict:
        """
        Анализирует данные сферы для генерации рекомендаций.

        Args:
            sphere: Название сферы
            pro_data: PRO-данные пользователя
            history: История отчетов

        Returns:
            Словарь с результатами анализа
        """
        analysis: AnalysisDict = {
            "current_score": None,
            "trend": "stable",
            "problems": [],
            "goals": [],
            "blockers": [],
            "metrics": [],
        }

        # Получаем текущую оценку из истории
        if history:
            latest = history[-1]
            analysis["current_score"] = latest.scores.get(sphere)

            # Анализируем тренд
            if len(history) > 1:
                prev_score = history[-2].scores.get(sphere)
                if prev_score and analysis["current_score"]:
                    if analysis["current_score"] > prev_score:
                        analysis["trend"] = "improved"
                    elif analysis["current_score"] < prev_score:
                        analysis["trend"] = "declined"

        # Добавляем проблемы, цели и блокеры
        analysis["problems"] = pro_data.problems.get(sphere, [])
        analysis["goals"] = pro_data.goals.get(sphere, [])
        analysis["blockers"] = pro_data.blockers.get(sphere, [])

        # Добавляем метрики
        for metric in pro_data.metrics:
            if metric.sphere == sphere:
                analysis["metrics"].append(
                    {
                        "name": metric.name,
                        "current": metric.current_value,
                        "target": metric.target_value,
                        "description": metric.description,
                    }
                )

        return analysis

    def _generate_action_steps(
        self, sphere: str, analysis: AnalysisDict
    ) -> List[ActionStep]:
        """
        Генерирует шаги действий на основе анализа.

        Args:
            sphere: Название сферы
            analysis: Результаты анализа сферы

        Returns:
            Список шагов действий
        """
        steps: List[ActionStep] = []
        base_actions = self.base_recommendations[sphere]["templates"][0]["actions"]

        # Добавляем базовые действия
        for action in base_actions:
            steps.append(
                ActionStep(
                    description=action,
                    expected_impact=0.7,
                    estimated_time="1 неделя",
                    dependencies=[],
                )
            )

        # Добавляем специфичные действия на основе анализа
        if analysis["problems"]:
            steps.append(
                ActionStep(
                    description=f"Решить проблему: {analysis['problems'][0]}",
                    expected_impact=0.8,
                    estimated_time="2 недели",
                    dependencies=[],
                )
            )

        if analysis["goals"]:
            steps.append(
                ActionStep(
                    description=f"Работать над целью: {analysis['goals'][0]}",
                    expected_impact=0.9,
                    estimated_time="1 месяц",
                    dependencies=[],
                )
            )

        return steps

    def _generate_evidence(self, sphere: str, analysis: AnalysisDict) -> Evidence:
        """
        Генерирует доказательную базу на основе анализа.

        Args:
            sphere: Название сферы
            analysis: Результаты анализа сферы

        Returns:
            Объект Evidence с доказательной базой
        """
        data_points = []
        if analysis["current_score"] is not None:
            data_points.append(f"Текущая оценка сферы: {analysis['current_score']:.1f}")
        if analysis["trend"] != "stable":
            trend_text = "улучшился" if analysis["trend"] == "improved" else "ухудшился"
            data_points.append(f"Тренд за последний период: {trend_text}")
        if analysis["problems"]:
            data_points.append(f"Ключевая проблема: {analysis['problems'][0]}")
        if analysis["goals"]:
            data_points.append(f"Основная цель: {analysis['goals'][0]}")

        return Evidence(
            data_points=data_points, correlations=[], historical_success=0.0
        )

    def _determine_priority(self, sphere: str, analysis: AnalysisDict) -> int:
        """
        Определяет приоритет рекомендации.

        Args:
            sphere: Название сферы
            analysis: Результаты анализа

        Returns:
            Приоритет от 1 до 5
        """
        priority = 3  # Средний приоритет по умолчанию

        if analysis["current_score"] is not None:
            if analysis["current_score"] < 5:
                priority += 1  # Низкая оценка повышает приоритет
            elif analysis["current_score"] > 8:
                priority -= 1  # Высокая оценка снижает приоритет

        if analysis["trend"] == "declined":
            priority += 1  # Отрицательный тренд повышает приоритет

        if analysis["problems"] or analysis["blockers"]:
            priority += 1  # Наличие проблем/блокеров повышает приоритет

        # Ограничиваем приоритет в диапазоне 1-5
        return max(1, min(5, priority))

    def generate(
        self, pro_data: ProData, history: List[HistoricalReport]
    ) -> Dict[str, Recommendation]:
        """
        Основной метод для генерации рекомендаций.
        """
        recommendations = {}
        for sphere in self.base_recommendations:
            analysis = self._analyze_sphere_data(sphere, pro_data, history)
            template = self.base_recommendations[sphere]["templates"][0]
            action_steps = self._generate_action_steps(sphere, analysis)
            evidence = self._generate_evidence(sphere, analysis)
            priority = self._determine_priority(sphere, analysis)

            recommendations[sphere] = Recommendation(
                sphere=sphere,
                priority=priority,
                title=template["title"],
                description=template["description"],
                action_steps=action_steps,
                evidence=evidence,
                related_spheres=[],
            )

        return recommendations

    def generate_basic(
        self, context: Dict[str, Any]
    ) -> Union[Recommendation, List[str]]:
        """
        Генерирует базовые рекомендации на основе контекста.
        """
        # TODO: Добавить логику генерации базовых рекомендаций.
        return ["Нет базовых рекомендаций"]
