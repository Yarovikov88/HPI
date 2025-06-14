"""
Тестовые данные для проверки системы HPI.
"""
from datetime import datetime
from typing import Dict, List

from .parsers import ProData, ProMetric, HistoricalReport

def get_test_pro_data() -> ProData:
    """Возвращает тестовые PRO-данные."""
    return ProData(
        scores={
            "Карьера": 6.5,
            "Отношения с любимыми": 7.8,
            "Физическое здоровье": 6.2
        },
        metrics=[
            ProMetric(
                sphere="Карьера",
                name="Профессиональное развитие",
                current_value=6.0,
                target_value=8.0,
                description="Изучение новых технологий и навыков",
                normalized_name="professional_development"
            ),
            ProMetric(
                sphere="Карьера",
                name="Проектная активность",
                current_value=7.0,
                target_value=9.0,
                description="Участие в значимых проектах",
                normalized_name="project_activity"
            )
        ],
        problems={
            "Карьера": ["Не хватает времени на обучение", "Много рутинных задач"],
            "Физическое здоровье": ["Нерегулярные тренировки"]
        },
        goals={
            "Карьера": ["Повысить квалификацию", "Начать вести свой проект"],
            "Физическое здоровье": ["Регулярные тренировки 3 раза в неделю"]
        },
        blockers={
            "Карьера": ["Высокая загруженность текущими задачами"],
            "Физическое здоровье": ["Нет четкого расписания"]
        },
        achievements={
            "Карьера": ["Завершил важный проект"],
            "Физическое здоровье": ["Начал ходить в спортзал"]
        }
    )

def get_test_history() -> List[HistoricalReport]:
    """Возвращает тестовую историю отчетов."""
    return [
        HistoricalReport(
            date=datetime(2024, 1, 1),
            hpi=6.5,
            file_path="reports_final/2024-01-01_report.md",
            scores={
                "Карьера": 6.0,
                "Отношения с любимыми": 7.5,
                "Физическое здоровье": 6.0
            },
            metrics=[
                ProMetric(
                    sphere="Карьера",
                    name="Профессиональное развитие",
                    current_value=5.5,
                    target_value=8.0,
                    description="",
                    normalized_name="professional_development"
                ),
                ProMetric(
                    sphere="Карьера",
                    name="Проектная активность",
                    current_value=6.5,
                    target_value=9.0,
                    description="",
                    normalized_name="project_activity"
                )
            ]
        ),
        HistoricalReport(
            date=datetime(2024, 2, 1),
            hpi=6.6,
            file_path="reports_final/2024-02-01_report.md",
            scores={
                "Карьера": 6.2,
                "Отношения с любимыми": 7.6,
                "Физическое здоровье": 6.1
            },
            metrics=[
                ProMetric(
                    sphere="Карьера",
                    name="Профессиональное развитие",
                    current_value=5.8,
                    target_value=8.0,
                    description="",
                    normalized_name="professional_development"
                ),
                ProMetric(
                    sphere="Карьера",
                    name="Проектная активность",
                    current_value=6.8,
                    target_value=9.0,
                    description="",
                    normalized_name="project_activity"
                )
            ]
        )
    ] 