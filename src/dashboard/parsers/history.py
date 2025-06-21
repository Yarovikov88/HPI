"""
Модуль для работы с историческими данными HPI.
"""

import json
import logging
import os
import re
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Union

from ..normalizers import SphereNormalizer
from .pro_data import ProMetric


class MetricsData(TypedDict):
    """Тип для данных метрик из JSON."""

    metrics: Dict[str, List[Dict[str, Union[str, float]]]]


class SectionData(TypedDict):
    """Тип для данных секции."""

    title: str
    content: str
    type: str  # "table" или "text"


@dataclass
class HistoricalScore:
    """Исторические данные по одной сфере."""

    sphere: str
    date: datetime
    score: float
    emoji: str


@dataclass
class HistoricalReport:
    """Данные одного исторического отчета."""

    date: datetime
    hpi: float  # Всегда должно быть float, не Optional
    scores: Dict[str, float]
    file_path: str
    metrics: Optional[List[ProMetric]] = None
    problems: Optional[Dict[str, list]] = None
    goals: Optional[Dict[str, list]] = None
    blockers: Optional[Dict[str, list]] = None
    achievements: Optional[Dict[str, list]] = None
    general_notes: Optional[Dict[str, str]] = None


class HistoryParser:
    """Парсер исторических данных."""

    def __init__(self, reports_dir: str):
        """
        Инициализация парсера.

        Args:
            reports_dir: Путь к директории с отчетами
        """
        self.reports_dir = reports_dir
        self.logger = logging.getLogger(__name__)
        self.sphere_normalizer = SphereNormalizer()

    def _extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """
        Извлекает дату из имени файла.

        Args:
            filename: Имя файла

        Returns:
            Объект datetime или None, если не удалось извлечь дату
        """
        try:
            # Ожидаем формат: YYYY-MM-DD_report.md
            date_str: str = filename.split("_")[0]
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (IndexError, ValueError):
            self.logger.warning(f"Не удалось извлечь дату из имени файла: {filename}")
            return None

    def _extract_hpi(self, content: str) -> Optional[float]:
        """
        Извлекает значение HPI из отчета.

        Args:
            content: Содержимое отчета

        Returns:
            Значение HPI или None, если не найдено
        """
        # Сначала пробуем найти в формате таблицы (новый формат)
        pattern: str = (
            r"\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*(\d+\.\d+)\*\*\s*\|\s*"
            r"[🟡🔵🔴🟢]\s*\|"
        )
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))

        # Если не нашли, ищем в старом формате таблицы
        pattern = (
            r"\|\s*\*\*Итоговый HPI\*\*\s*\|\s*(\d+\.\d+)\s*\|\s*" r"[🟡🔵🔴🟢]\s*\|"
        )
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))

        # Если не нашли, ищем в формате строки
        pattern = r"HPI:\s*(\d+\.\d+)\s*[🟡🔵🔴🟢]"
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))

        # Если не нашли, ищем в итоговой таблице
        pattern = (
            r"\|\s*\*\*Итоговый HPI\*\*\s*\|\s*(\d+\.\d+)\s*\|\s*" r"[🟡🔵🔴🟢]\s*\|"
        )
        match = re.search(pattern, content)
        return float(match.group(1)) if match else None

    def _extract_scores(self, content: str) -> Dict[str, float]:
        """
        Извлекает оценки сфер из содержимого отчета.

        Args:
            content: Содержимое отчета

        Returns:
            Словарь {сфера: оценка}
        """
        scores: Dict[str, float] = {}

        # Сначала пробуем найти в формате строк
        pattern: str = r"([💖🏡🤝💼♂️🧠🎨💰])\s+([^:]+):\s+(\d+\.\d+)\s+" r"[🟡🔵🔴🟢]"
        matches = re.finditer(pattern, content)

        for match in matches:
            emoji = match.group(1)
            value = float(match.group(3))
            sphere = self.sphere_normalizer.get_sphere_by_emoji(emoji)
            if sphere:
                scores[sphere] = value

        # Если не нашли, ищем в формате таблицы
        if not scores:
            pattern = r"\|\s*([^|]+)\s*\|\s*(\d+\.\d+)\s*\|\s*" r"[🟡🔵🔴🟢]\s*\|"
            matches = re.finditer(pattern, content)

            valid_spheres: List[str] = [
                "Отношения с любимыми",
                "Отношения с родными",
                "Друзья",
                "Карьера",
                "Физическое здоровье",
                "Ментальное здоровье",
                "Хобби и увлечения",
                "Благосостояние",
            ]

            for match in matches:
                sphere = match.group(1).strip()
                value = float(match.group(2))
                if sphere in valid_spheres:
                    scores[sphere] = value

        return scores

    def _extract_metrics_from_json(self, content: str) -> Optional[List[ProMetric]]:
        """
        Извлекает метрики из JSON-блока.

        Args:
            content: Содержимое отчета

        Returns:
            Список объектов ProMetric или None, если не найдено
        """
        json_block_match = re.search(
            r"## 📊 Метрики и сравнение\n```json\n(.*?)\n```", content, re.DOTALL
        )
        if not json_block_match:
            return None

        try:
            metrics_data: MetricsData = json.loads(json_block_match.group(1))
            metrics: List[ProMetric] = []

            for sphere, sphere_metrics in metrics_data.get("metrics", {}).items():
                for metric_data in sphere_metrics:
                    name = (
                        str(metric_data["name"])
                        if metric_data["name"] is not None
                        else ""
                    )
                    try:
                        current_value = (
                            float(metric_data["current_value"])
                            if metric_data["current_value"] is not None
                            else None
                        )
                    except (ValueError, TypeError):
                        current_value = None
                    try:
                        target_value = (
                            float(metric_data["target_value"])
                            if metric_data["target_value"] is not None
                            else None
                        )
                    except (ValueError, TypeError):
                        target_value = None
                    normalized_name = (
                        str(metric_data["name"]).lower().replace(" ", "_")
                        if metric_data["name"] is not None
                        else ""
                    )
                    metrics.append(
                        ProMetric(
                            sphere=sphere,
                            name=name,
                            current_value=current_value,
                            target_value=target_value,
                            description="",  # Описание не хранится в JSON
                            normalized_name=normalized_name,
                        )
                    )
            return metrics
        except Exception as e:
            self.logger.warning(f"Ошибка при парсинге JSON-блока метрик: {e}")
            return None

    def _extract_metrics_from_table(self, content: str) -> Optional[List[ProMetric]]:
        """
        Извлекает метрики из таблицы.

        Args:
            content: Содержимое отчета

        Returns:
            Список объектов ProMetric или None, если не найдено
        """
        metric_section_match = re.search(
            r"### 📊 Мои метрики\n\s*((?:\|.*\n)+)", content
        )
        if metric_section_match:
            from .pro_data import ProDataParser

            parser = ProDataParser()
            return parser._parse_metrics_section(metric_section_match.group(1))
        return None

    def _find_section_content(self, content: str, section_name: str) -> Optional[str]:
        """
        Находит содержимое заданного раздела.

        Args:
            content: Содержимое отчета
            section_name: Название раздела

        Returns:
            Содержимое раздела или None, если не найдено
        """
        section_match = re.search(
            rf"### {re.escape(section_name)}\n\s*((?:\|.*\n)+)", content
        )
        if section_match:
            return section_match.group(1)
        return None

    def _parse_regular_section(self, content: str) -> Dict[str, list]:
        """
        Парсит обычный раздел.

        Args:
            content: Содержимое раздела

        Returns:
            Словарь {заголовок: список строк}
        """
        from .pro_data import ProDataParser

        parser = ProDataParser()
        return parser._parse_regular_section(content)

    def parse_report(self, file_path: str) -> Optional[HistoricalReport]:
        """
        Парсит один исторический отчет.

        Args:
            file_path: Путь к файлу отчета

        Returns:
            Объект HistoricalReport или None в случае ошибки
        """
        try:
            # Получаем дату из имени файла
            filename = os.path.basename(file_path)
            date = self._extract_date_from_filename(filename)
            if not date:
                return None

            # Читаем содержимое файла
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Извлекаем данные
            hpi = self._extract_hpi(content)
            scores = self._extract_scores(content)
            metrics = self._extract_metrics_from_table(content)

            # Извлекаем PRO-секции
            problems_content = self._find_section_content(content, "🛑 Мои проблемы")
            goals_content = self._find_section_content(content, "🎯 Мои цели")
            blockers_content = self._find_section_content(content, "🚧 Мои блокеры")
            achievements_content = self._find_section_content(
                content, "🏆 Мои достижения"
            )

            # Парсим PRO-секции
            problems = (
                self._parse_regular_section(problems_content)
                if problems_content
                else {}
            )
            goals = self._parse_regular_section(goals_content) if goals_content else {}
            blockers = (
                self._parse_regular_section(blockers_content)
                if blockers_content
                else {}
            )
            achievements = (
                self._parse_regular_section(achievements_content)
                if achievements_content
                else {}
            )

            # Создаем объект отчета
            return HistoricalReport(
                file_path=file_path,
                date=date,
                hpi=hpi if hpi is not None else 0.0,
                scores=scores,
                metrics=metrics,
                problems=problems,
                goals=goals,
                blockers=blockers,
                achievements=achievements,
            )

        except Exception as e:
            self.logger.error(f"Ошибка при парсинге отчета {file_path}: {e}")
            self.logger.error(traceback.format_exc())
            return None

    def get_history(self) -> List[HistoricalReport]:
        """
        Получает историю всех отчетов.

        Returns:
            Список объектов HistoricalReport, отсортированный по дате
        """
        history: List[HistoricalReport] = []

        try:
            # Получаем список всех файлов отчетов
            report_files = [
                f for f in os.listdir(self.reports_dir) if f.endswith("_report.md")
            ]

            # Парсим каждый отчет
            for filename in report_files:
                file_path = os.path.join(self.reports_dir, filename)
                report = self.parse_report(file_path)
                if report:
                    history.append(report)

            # Сортируем по дате
            history.sort(key=lambda x: x.date)

        except Exception as e:
            self.logger.error(
                f"Ошибка при получении истории: {e}\n{traceback.format_exc()}"
            )

        return history

    def get_sphere_history(self, sphere: str) -> List[HistoricalScore]:
        """
        Получает историю оценок конкретной сферы.

        Args:
            sphere: Название сферы

        Returns:
            Список объектов HistoricalScore
        """
        history = []
        emoji = self.sphere_normalizer.get_emoji_by_sphere(sphere)

        if not emoji:
            self.logger.error(f"Неизвестная сфера: {sphere}")
            return []

        for report in self.get_history():
            score = report.scores.get(sphere)
            if score is not None:
                history.append(
                    HistoricalScore(
                        sphere=sphere, date=report.date, score=score, emoji=emoji
                    )
                )

        return history

    def parse(self) -> List[HistoricalReport]:
        """Парсит все отчеты в директории."""
        return self.get_history()
