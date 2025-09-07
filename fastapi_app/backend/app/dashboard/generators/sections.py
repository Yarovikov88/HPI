"""
Модуль для генерации секций отчета HPI.
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..parsers import ProData, HistoricalReport, ProMetric
from ..normalizers import MetricNormalizer, SphereNormalizer
from .recommendations import Recommendation


@dataclass
class MetricProgress:
    """Прогресс по метрике."""
    name: str
    current_value: Optional[float]
    previous_value: Optional[float]
    target_value: Optional[float]
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
        self.logger = logging.getLogger('rich')

    def _calculate_change_percent(
        self,
        current: Optional[float],
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
        if current is None or previous is None:
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
        metric: ProMetric,
        previous_report: Optional[HistoricalReport]
    ) -> MetricProgress:
        """
        Генерирует прогресс по метрике.
        Args:
            metric: Объект ProMetric из текущих данных
            previous_report: Предыдущий отчет
        Returns:
            Объект MetricProgress
        """
        previous_value = None
        if previous_report and previous_report.metrics:
            for prev_metric in previous_report.metrics:
                self.logger.info(f"[COMPARE] now: {metric.normalized_name} ({metric.sphere}) = {metric.current_value}, prev: {prev_metric.normalized_name} ({prev_metric.sphere}) = {prev_metric.current_value}")
                if (
                    prev_metric.normalized_name == metric.normalized_name and
                    prev_metric.sphere == metric.sphere
                ):
                    previous_value = prev_metric.current_value
                    self.logger.info(f"[MATCH] Найдена предыдущая метрика: {prev_metric.normalized_name} ({prev_metric.sphere}) = {prev_metric.current_value}")
                    break
            if not previous_value:
                self.logger.warning(f"[NO MATCH] Для метрики {metric.normalized_name} ({metric.sphere}) не найдено соответствия в предыдущем отчете!")
        change_percent = self._calculate_change_percent(
            metric.current_value,
            previous_value
        )
        return MetricProgress(
            name=metric.name,
            current_value=metric.current_value if metric.current_value is not None else 0.0,
            previous_value=previous_value,
            target_value=metric.target_value if metric.target_value is not None else 0.0,
            change_percent=change_percent,
            status=self._determine_status(change_percent)
        )

    def generate(
        self,
        history: List[HistoricalReport],
        recommendations: Dict[str, Recommendation]
    ) -> Dict[str, SphereSection]:
        """
        Генерирует секции для всех сфер.
        Args:
            history: История финальных отчетов (отсортирована по дате)
            recommendations: Рекомендации по сферам
        Returns:
            Словарь {сфера: секция}
        """
        sections = {}
        if not history:
            self.logger.error("История финальных отчетов пуста!")
            return sections
        current_report = history[-1]
        previous_report = history[-2] if len(history) > 1 else None
        self.logger.info(f"[REPORT_COMPARE] Текущий отчет: {current_report.file_path}, дата: {current_report.date}")
        if previous_report:
            self.logger.info(f"[REPORT_COMPARE] Предыдущий отчет: {previous_report.file_path}, дата: {previous_report.date}")
        else:
            self.logger.warning("[REPORT_COMPARE] Предыдущий отчет не найден!")
        # Получаем master_order с нормализованными названиями сфер
        master_order = [
            self.sphere_normalizer.normalize('Отношения с любимыми'),
            self.sphere_normalizer.normalize('Отношения с родными'),
            self.sphere_normalizer.normalize('Друзья'),
            self.sphere_normalizer.normalize('Карьера'),
            self.sphere_normalizer.normalize('Физическое здоровье'),
            self.sphere_normalizer.normalize('Ментальное здоровье'),
            self.sphere_normalizer.normalize('Хобби и увлечения'),
            self.sphere_normalizer.normalize('Благосостояние')
        ]
        # DEBUG: выводим содержимое проблем/целей/блокеров
        self.logger.info('[DEBUG] current_report.problems: %s', getattr(current_report, 'problems', {}))
        self.logger.info('[DEBUG] current_report.goals: %s', getattr(current_report, 'goals', {}))
        self.logger.info('[DEBUG] current_report.blockers: %s', getattr(current_report, 'blockers', {}))
        if previous_report and previous_report.metrics:
            self.logger.info('[DEBUG] previous_report.metrics:')
            for m in previous_report.metrics:
                self.logger.info(f"  - {m.normalized_name} | {m.sphere} | {m.current_value}")
        # Генерируем секции для каждой сферы из master_order
        for sphere in master_order:
            normalized = self.sphere_normalizer.normalize(sphere)
            emoji = self.sphere_normalizer.get_emoji(normalized)
            current_score = 0.0
            if current_report.scores and normalized in current_report.scores:
                current_score = current_report.scores[normalized]
            previous_score = None
            if previous_report and normalized in previous_report.scores:
                previous_score = previous_report.scores[normalized]
            change_percent = self._calculate_change_percent(current_score, previous_score)
            # Метрики только по этой сфере
            sphere_metrics = []
            if current_report.metrics:
                for metric in current_report.metrics:
                    if metric.sphere == normalized:
                        self.logger.info(f"[DEBUG] Сопоставление метрики: {metric.normalized_name} | {metric.sphere} | {metric.current_value}")
                        sphere_metrics.append(self._generate_metric_progress(metric, previous_report))
            problems = getattr(current_report, 'problems', {}).get(normalized, [])
            goals = getattr(current_report, 'goals', {}).get(normalized, [])
            blockers = getattr(current_report, 'blockers', {}).get(normalized, [])
            sections[normalized] = SphereSection(
                name=normalized,
                emoji=emoji,
                current_score=current_score,
                previous_score=previous_score,
                change_percent=change_percent,
                status=self._determine_status(change_percent),
                metrics=sphere_metrics,
                problems=problems,
                goals=goals,
                blockers=blockers,
                recommendation=recommendations.get(sphere)
            )
        return sections 