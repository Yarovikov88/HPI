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
        metric: ProMetric,
        current_data: ProData,
        previous_report: Optional[HistoricalReport]
    ) -> MetricProgress:
        """
        Генерирует прогресс по метрике.
        Args:
            metric: Объект ProMetric из текущих данных
            current_data: Текущие PRO-данные
            previous_report: Предыдущий отчет
        Returns:
            Объект MetricProgress
        """
        # Получаем предыдущие значения по совпадению normalized_name и сферы
        previous_value = None
        if previous_report and previous_report.metrics:
            for prev_metric in previous_report.metrics:
                if (
                    prev_metric.normalized_name == metric.normalized_name and
                    prev_metric.sphere == metric.sphere
                ):
                    previous_value = prev_metric.current_value
                    break
        change_percent = self._calculate_change_percent(
            metric.current_value,
            previous_value
        )
        return MetricProgress(
            name=metric.name,
            current_value=metric.current_value,
            previous_value=previous_value,
            target_value=metric.target_value,
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

        # DEBUG: выводим содержимое pro_data.problems/goals/blockers
        self.logger.info('[DEBUG] pro_data.problems: %s', pro_data.problems)
        self.logger.info('[DEBUG] pro_data.goals: %s', pro_data.goals)
        self.logger.info('[DEBUG] pro_data.blockers: %s', pro_data.blockers)
        if previous_report and previous_report.metrics:
            self.logger.info('[DEBUG] previous_report.metrics:')
            for m in previous_report.metrics:
                self.logger.info(f"  - {m.normalized_name} | {m.sphere} | {m.current_value}")

        # Для каждой текущей метрики логируем попытку поиска предыдущего значения
        def find_prev_metric(cur_metric, cur_sphere):
            if not previous_report or not previous_report.metrics:
                return None
            for m in previous_report.metrics:
                self.logger.info(f"[DEBUG] Сравниваю: '{cur_metric.normalized_name}' ({cur_sphere}) <-> '{m.normalized_name}' ({m.sphere})")
                if m.normalized_name == cur_metric.normalized_name and m.sphere == cur_sphere:
                    self.logger.info(f"[DEBUG] Найдено совпадение для '{cur_metric.name}' в сфере '{cur_sphere}': {m.current_value}")
                    return m.current_value
            self.logger.info(f"[DEBUG] Не найдено совпадение для '{cur_metric.name}' в сфере '{cur_sphere}'")
            return None

        # Генерируем секции для каждой сферы из master_order
        for sphere in master_order:
            normalized = self.sphere_normalizer.normalize(sphere)
            emoji = self.sphere_normalizer.get_emoji(normalized)
            current_score = 0.0
            if pro_data.scores and normalized in pro_data.scores:
                current_score = pro_data.scores[normalized]
            previous_score = None
            if previous_report and normalized in previous_report.scores:
                previous_score = previous_report.scores[normalized]
            change_percent = self._calculate_change_percent(current_score, previous_score)
            # Метрики только по этой сфере
            sphere_metrics = []
            for metric in pro_data.metrics:
                if metric.sphere == normalized:
                    # DEBUG: что ищем
                    self.logger.info(f"[DEBUG] Сопоставление метрики: {metric.normalized_name} | {metric.sphere} | {metric.current_value}")
                    prev_val = find_prev_metric(metric, normalized)
                    self.logger.info(f"[DEBUG] Найдено предыдущее значение: {prev_val}")
                    sphere_metrics.append(self._generate_metric_progress(metric, pro_data, previous_report))
            problems = pro_data.problems.get(normalized, [])
            goals = pro_data.goals.get(normalized, [])
            blockers = pro_data.blockers.get(normalized, [])
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