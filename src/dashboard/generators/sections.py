"""
Модуль для генерации секций отчета HPI.
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..parsers import ProData, HistoricalReport
from ..normalizers import MetricNormalizer, SphereNormalizer
from .recommendations import Recommendation


@dataclass
class MetricProgress:
    """Прогресс по метрике."""
    name: str
    current_value: float
    previous_value: Optional[float]
    target_value: float
    change_percent: float
    status: str  # "improved", "declined", "stable"


@dataclass
class SphereSection:
    """Секция отчета для конкретной сферы."""
    name: str
    emoji: str
    current_score: float
    previous_score: Optional[float]
    change_percent: float
    status: str  # "improved", "declined", "stable"
    metrics: List[MetricProgress]
    problems: List[str]
    goals: List[str]
    blockers: List[str]
    recommendation: Optional[Recommendation]


class SectionGenerator:
    """Генератор секций отчета."""

    def __init__(self):
        """Инициализация генератора."""
        self.sphere_normalizer = SphereNormalizer()
        self.metric_normalizer = MetricNormalizer()
        self.logger = logging.getLogger(__name__)

    def _calculate_change_percent(
        self,
        current: float,
        previous: Optional[float]
    ) -> float:
        """
        Вычисляет процент изменения между значениями.
        
        Args:
            current: Текущее значение
            previous: Предыдущее значение
            
        Returns:
            Процент изменения
        """
        if not previous:
            return 0.0
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / abs(previous)) * 100

    def _determine_status(
        self,
        change_percent: float,
        threshold: float = 5.0
    ) -> str:
        """
        Определяет статус на основе процента изменения.
        
        Args:
            change_percent: Процент изменения
            threshold: Порог для определения статуса
            
        Returns:
            Статус изменения
        """
        if abs(change_percent) < threshold:
            return "stable"
        return "improved" if change_percent > 0 else "declined"

    def _generate_metric_progress(
        self,
        metric_name: str,
        current_data: ProData,
        previous_report: Optional[HistoricalReport]
    ) -> MetricProgress:
        """
        Генерирует прогресс по метрике.
        
        Args:
            metric_name: Название метрики
            current_data: Текущие PRO-данные
            previous_report: Предыдущий отчет
            
        Returns:
            Объект MetricProgress
        """
        # Получаем текущие значения
        current_metric = next(
            (m for m in current_data.metrics if m.name == metric_name),
            None
        )
        if not current_metric:
            raise ValueError(f"Метрика {metric_name} не найдена в текущих данных")
            
        # Получаем предыдущие значения
        previous_value = None
        if previous_report and previous_report.metrics:
            prev_metric = next(
                (m for m in previous_report.metrics if m.name == metric_name),
                None
            )
            if prev_metric:
                previous_value = prev_metric.value
                
        # Вычисляем изменения
        change_percent = self._calculate_change_percent(
            current_metric.current_value,
            previous_value
        )
        
        return MetricProgress(
            name=metric_name,
            current_value=current_metric.current_value,
            previous_value=previous_value,
            target_value=current_metric.target_value,
            change_percent=change_percent,
            status=self._determine_status(change_percent)
        )

    def generate(
        self,
        pro_data: ProData,
        history: List[HistoricalReport],
        recommendations: Dict[str, Recommendation]
    ) -> Dict[str, SphereSection]:
        """
        Генерирует секции для всех сфер.
        
        Args:
            pro_data: PRO-данные пользователя
            history: История отчетов
            recommendations: Рекомендации по сферам
            
        Returns:
            Словарь {сфера: секция}
        """
        sections = {}
        previous_report = history[-1] if history else None
        
        # Получаем все уникальные сферы
        spheres = set()
        for metric in pro_data.metrics:
            spheres.add(metric.sphere)
        for sphere in pro_data.problems:
            spheres.add(sphere)
        for sphere in pro_data.goals:
            spheres.add(sphere)
        for sphere in pro_data.blockers:
            spheres.add(sphere)
        
        # Генерируем секции для каждой сферы
        for sphere in spheres:
            # Получаем нормализованное имя и эмодзи
            normalized = self.sphere_normalizer.normalize(sphere)
            
            # Получаем текущую оценку
            current_score = 0.0
            if pro_data.scores and sphere in pro_data.scores:
                current_score = pro_data.scores[sphere]
                
            # Получаем предыдущую оценку
            previous_score = None
            if previous_report and sphere in previous_report.scores:
                previous_score = previous_report.scores[sphere]
                
            # Вычисляем изменения
            change_percent = self._calculate_change_percent(
                current_score,
                previous_score
            )
            
            # Получаем метрики сферы
            sphere_metrics = []
            for metric in pro_data.metrics:
                if metric.sphere == sphere:
                    progress = self._generate_metric_progress(
                        metric.name,
                        pro_data,
                        previous_report
                    )
                    sphere_metrics.append(progress)
                    
            # Создаем секцию
            sections[sphere] = SphereSection(
                name=normalized,
                emoji=self.sphere_normalizer.get_emoji(sphere),
                current_score=current_score,
                previous_score=previous_score,
                change_percent=change_percent,
                status=self._determine_status(change_percent),
                metrics=sphere_metrics,
                problems=pro_data.problems.get(sphere, []),
                goals=pro_data.goals.get(sphere, []),
                blockers=pro_data.blockers.get(sphere, []),
                recommendation=recommendations.get(sphere)
            )
            
        return sections 