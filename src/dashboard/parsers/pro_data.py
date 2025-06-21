"""
Модуль для парсинга PRO-секций из черновиков отчетов HPI.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict

from ..normalizers import MetricNormalizer, SphereNormalizer


class SectionContent(TypedDict):
    """Тип для содержимого секции."""

    title: str
    content: str


class TableRow(TypedDict):
    """Тип для строки таблицы."""

    cells: List[str]
    is_header: bool


@dataclass
class ProMetric:
    """Класс для хранения данных о PRO-метрике."""

    sphere: str
    name: str
    description: str
    normalized_name: str
    current_value: Optional[float]
    target_value: Optional[float]
    previous_value: Optional[float] = None
    unit: Optional[str] = ""


@dataclass
class ProData:
    """Данные из всех PRO-секций."""

    scores: Dict[str, float]  # {сфера: оценка}
    metrics: List[ProMetric]  # Список метрик
    problems: Dict[str, List[str]]  # {сфера: [проблема1, проблема2, ...]}
    goals: Dict[str, List[str]]  # {сфера: [цель1, цель2, ...]}
    blockers: Dict[str, List[str]]  # {сфера: [блокер1, блокер2, ...]}
    achievements: Dict[str, List[str]]  # {сфера: [достижение1, достижение2, ...]}
    general_notes: Dict[str, str]  # Новое поле для общих вопросов


class MetricData(TypedDict):
    """Структура данных для метрики из JSON."""

    name: str
    current_value: float
    target_value: float


class MetricsJson(TypedDict):
    """Структура данных для JSON с метриками."""

    metrics: Dict[str, List[MetricData]]


class ProDataParser:
    """Парсер PRO-секций из черновиков отчетов."""

    def __init__(self):
        """Инициализация парсера."""
        self.sphere_normalizer = SphereNormalizer()
        self.metric_normalizer = MetricNormalizer()
        self.logger = logging.getLogger(__name__)

        # Названия всех PRO-секций
        self.pro_sections: List[str] = [
            "🛑 Мои проблемы",
            "🎯 Мои цели",
            "🚧 Мои блокеры",
            "🏆 Мои достижения",
            "📊 Мои метрики",
            "📝 Общие вопросы",  # Новая секция
        ]

    def _find_section_content(self, content: str, section_title: str) -> Optional[str]:
        """
        Находит содержимое конкретной секции в тексте.

        Args:
            content: Весь текст документа
            section_title: Название искомой секции

        Returns:
            Содержимое секции или None, если секция не найдена
        """
        # Ищем секцию с двумя или тремя решетками
        pattern: str = (
            rf"(?:##|###)\s*{re.escape(section_title)}" r"(.*?)(?=(?:##|###)|$)"
        )
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _parse_table_rows(self, table_content: str) -> List[List[str]]:
        """
        Парсит строки таблицы в список списков значений.

        Args:
            table_content: Содержимое таблицы в формате Markdown

        Returns:
            Список списков значений из таблицы
        """
        rows: List[List[str]] = []
        if not table_content:
            return rows

        # Разбиваем на строки и фильтруем пустые
        lines: List[str] = [
            line.strip() for line in table_content.splitlines() if line.strip()
        ]

        for line in lines:
            if line.startswith("|"):
                # Разбиваем строку по | и убираем пустые значения
                cells: List[str] = [
                    cell.strip() for cell in line.split("|") if cell.strip()
                ]
                if cells and not any(
                    "---" in cell for cell in cells
                ):  # Пропускаем строку форматирования
                    rows.append(cells)

        return rows

    def _parse_metrics_section(self, content: str) -> List[ProMetric]:
        """
        Парсит секцию метрик.

        Args:
            content: Содержимое секции метрик

        Returns:
            Список объектов ProMetric
        """
        metrics: List[ProMetric] = []
        rows = self._parse_table_rows(content)
        for row in rows:
            if len(row) >= 4:
                sphere_candidate = row[0]
                metric_name = row[1]
                current_value = row[2]
                target_value = row[3]
                description = row[4] if len(row) > 4 else ""

                # Определяем сферу по эмодзи или названию
                current_sphere: Optional[str] = None
                for emoji, sphere in self.sphere_normalizer.get_all_emojis().items():
                    if emoji in sphere_candidate:
                        current_sphere = sphere
                        break

                if not current_sphere:
                    current_sphere = self.sphere_normalizer.normalize(sphere_candidate)

                # Всегда нормализуем!
                if current_sphere:
                    current_sphere = self.sphere_normalizer.normalize(current_sphere)
                    try:
                        current_float: Optional[float] = (
                            float(current_value) if current_value else None
                        )
                        target_float: Optional[float] = (
                            float(target_value) if target_value else None
                        )
                    except ValueError:
                        self.logger.warning(
                            f"Не удалось преобразовать значения метрики "
                            f"'{metric_name}' в числа"
                        )
                        current_float = None
                        target_float = None

                    if current_sphere:
                        metrics.append(
                            ProMetric(
                                sphere=current_sphere,
                                name=metric_name,
                                description=description,
                                normalized_name=self.metric_normalizer.normalize(
                                    metric_name
                                ),
                                current_value=current_float,
                                target_value=target_float,
                            )
                        )
        return metrics

    def _parse_regular_section(self, content: str) -> Dict[str, List[str]]:
        """
        Парсит обычную секцию (проблемы, цели, блокеры, достижения).

        Args:
            content: Содержимое секции

        Returns:
            Словарь {сфера: [значение1, значение2, ...]}
        """
        section_data: Dict[str, List[str]] = {}
        rows = self._parse_table_rows(content)
        for row in rows:
            if len(row) >= 2:
                sphere_candidate = row[0]
                value = row[1]

                # Определяем сферу
                current_sphere: Optional[str] = None
                for emoji, sphere in self.sphere_normalizer.get_all_emojis().items():
                    if emoji in sphere_candidate:
                        current_sphere = sphere
                        break

                if not current_sphere:
                    current_sphere = self.sphere_normalizer.normalize(sphere_candidate)

                # Всегда нормализуем!
                if current_sphere:
                    normalized_sphere = self.sphere_normalizer.normalize(current_sphere)
                    # Храним только одно значение для каждой сферы
                    section_data[normalized_sphere] = [value]

        return section_data

    def _parse_general_notes_section(self, content: str) -> Dict[str, str]:
        """
        Парсит секцию общих вопросов/заметок.

        Args:
            content: Содержимое секции

        Returns:
            Словарь {вопрос: ответ}
        """
        notes: Dict[str, str] = {}
        rows = self._parse_table_rows(content)
        for row in rows:
            if len(row) >= 2:
                question = row[0]
                answer = row[1]
                notes[question] = answer
        return notes

    def _parse_metrics_json(self, content: str) -> List[ProMetric]:
        """
        Парсит метрики из JSON-блока.

        Args:
            content: Содержимое документа

        Returns:
            Список объектов ProMetric
        """
        metrics: List[ProMetric] = []
        json_block_match = re.search(
            r"## 📊 Метрики и сравнение\n```json\n(.*?)\n```", content, re.DOTALL
        )
        if json_block_match:
            try:
                metrics_data: MetricsJson = json.loads(json_block_match.group(1))
                for sphere, sphere_metrics in metrics_data.get("metrics", {}).items():
                    for metric_data in sphere_metrics:
                        metrics.append(
                            ProMetric(
                                sphere=sphere,
                                name=metric_data["name"],
                                description="",  # Описание не хранится в JSON
                                normalized_name=self.metric_normalizer.normalize(
                                    metric_data["name"]
                                ),
                                current_value=metric_data["current_value"],
                                target_value=metric_data["target_value"],
                            )
                        )
            except Exception as e:
                self.logger.warning(f"Ошибка при парсинге JSON-блока метрик: {e}")
        return metrics

    def parse(self, content: str, scores: Optional[Dict[str, float]] = None) -> ProData:
        """
        Парсит все PRO-секции из текста.

        Args:
            content: Текст черновика
            scores: Словарь с оценками сфер (опционально)

        Returns:
            Объект ProData с данными всех секций
        """
        sections_data: Dict[str, Any] = {
            "problems": {},
            "goals": {},
            "blockers": {},
            "achievements": {},
            "metrics": [],
            "general_notes": {},
            "scores": scores or {},
        }

        # Парсим каждую секцию
        for section_title in self.pro_sections:
            section_content = self._find_section_content(content, section_title)
            if section_content:
                if "Метрики" in section_title:
                    sections_data["metrics"] = self._parse_metrics_section(
                        section_content
                    )
                elif "Проблемы" in section_title:
                    sections_data["problems"] = self._parse_regular_section(
                        section_content
                    )
                elif "Цели" in section_title:
                    sections_data["goals"] = self._parse_regular_section(
                        section_content
                    )
                elif "Блокеры" in section_title:
                    sections_data["blockers"] = self._parse_regular_section(
                        section_content
                    )
                elif "Достижения" in section_title:
                    sections_data["achievements"] = self._parse_regular_section(
                        section_content
                    )
                elif "Общие вопросы" in section_title:
                    sections_data["general_notes"] = self._parse_general_notes_section(
                        section_content
                    )

        # Приводим типы к ожидаемым для ProData
        return ProData(
            scores=sections_data.get("scores", {}),
            metrics=sections_data.get("metrics", []),
            problems=sections_data.get("problems", {}),
            goals=sections_data.get("goals", {}),
            blockers=sections_data.get("blockers", {}),
            achievements=sections_data.get("achievements", {}),
            general_notes=sections_data.get("general_notes", {}),
        )
