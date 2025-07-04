"""
Модуль для парсинга PRO-секций из черновиков отчетов HPI.
"""
import re
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from ..normalizers import MetricNormalizer, SphereNormalizer
from rich import print as rprint
from rich.pretty import Pretty
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns

# Глобальный фильтр для предупреждений о некорректных метриках
logged_metric_warnings: set = set()

@dataclass
class ProMetric:
    """Метрика из PRO-секции."""
    sphere: str
    name: str
    current_value: Optional[float]
    target_value: Optional[float]
    description: str
    normalized_name: str


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


class ProDataParser:
    """Парсер PRO-секций из черновиков отчетов."""

    def __init__(self):
        """Инициализация парсера."""
        self.sphere_normalizer = SphereNormalizer()
        self.metric_normalizer = MetricNormalizer()
        self.logger = logging.getLogger(__name__)

        # Названия всех PRO-секций
        self.pro_sections = [
            '🛑 Мои проблемы',
            '🎯 Мои цели',
            '🚧 Мои блокеры',
            '🏆 Мои достижения',
            '📊 Мои метрики',
            '📝 Общие вопросы'  # Новая секция
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
        pattern = rf"(?:##|###)\s*{re.escape(section_title)}(.*?)(?=(?:##|###)|$)"
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
        rows = []
        if not table_content:
            return rows
            
        # Разбиваем на строки и фильтруем пустые
        lines = [line.strip() for line in table_content.splitlines() if line.strip()]
        
        for line in lines:
            if line.startswith('|'):
                # Разбиваем строку по | и убираем пустые значения
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells and not any('---' in cell for cell in cells):  # Пропускаем строку форматирования
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
        metrics = []
        rows = self._parse_table_rows(content)
        global logged_metric_warnings  # Используем глобальный set
        for row in rows:
            if len(row) >= 4:
                sphere_candidate = row[0]
                metric_name = row[1]
                current_value = row[2]
                target_value = row[3]
                description = row[4] if len(row) > 4 else ""
                # Определяем сферу по эмодзи или названию
                current_sphere = None
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
                        current = float(current_value.replace(",", ".").replace(" ", ""))
                    except Exception:
                        current = None
                    try:
                        target = float(target_value.replace(",", ".").replace(" ", ""))
                    except Exception:
                        target = None
                    # Если оба значения не удалось преобразовать — логируем warning только один раз
                    if current is None or target is None:
                        warning_key = (metric_name, str(current_value), str(target_value))
                        if warning_key not in logged_metric_warnings:
                            logging.warning(f"Некорректное значение метрики '{metric_name}': '{current_value}' или '{target_value}' — не удалось преобразовать в число")
                            logged_metric_warnings.add(warning_key)
                    metrics.append(
                        ProMetric(
                            sphere=current_sphere,
                            name=metric_name,
                            current_value=current,
                            target_value=target,
                            description=description,
                            normalized_name=self.metric_normalizer.normalize(metric_name)
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
        section_data = {}
        rows = self._parse_table_rows(content)
        for row in rows:
            if len(row) >= 2:
                sphere_candidate = row[0]
                value = row[1]
                # Определяем сферу
                current_sphere = None
                for emoji, sphere in self.sphere_normalizer.get_all_emojis().items():
                    if emoji in sphere_candidate:
                        current_sphere = sphere
                        break
                if not current_sphere:
                    current_sphere = self.sphere_normalizer.normalize(sphere_candidate)
                # Всегда нормализуем!
                if current_sphere:
                    normalized_sphere = self.sphere_normalizer.normalize(current_sphere)
                    if normalized_sphere not in section_data:
                        section_data[normalized_sphere] = []
                    section_data[normalized_sphere].append(value)
        return section_data

    def _parse_general_notes_section(self, content: str) -> Dict[str, str]:
        """
        Парсит секцию общих вопросов/заметок.
        Args:
            content: Содержимое секции
        Returns:
            Словарь {вопрос: ответ}
        """
        notes = {}
        rows = self._parse_table_rows(content)
        for row in rows:
            if len(row) >= 2:
                question = row[0]
                answer = row[1]
                notes[question] = answer
        return notes

    def parse(self, content: str) -> ProData:
        """
        Парсит все PRO-секции из текста.
        Args:
            content: Текст черновика
        Returns:
            Объект ProData с данными всех секций
        """
        sections_data = {
            'problems': {},
            'goals': {},
            'blockers': {},
            'achievements': {},
            'metrics': [],
            'scores': {},
            'general_notes': {}  # Новое поле
        }
        logging.debug("--- Начало парсинга PRO-секций ---")
        section_map = {
            '🛑 Мои проблемы': 'problems',
            '🎯 Мои цели': 'goals',
            '🚧 Мои блокеры': 'blockers',
            '🏆 Мои достижения': 'achievements'
        }
        for section_title in self.pro_sections:
            section_content = self._find_section_content(content, section_title)
            if not section_content:
                logging.debug(f"Секция '{section_title}' не найдена в черновике")
                continue
            logging.debug(f"Найдена секция '{section_title}', размер контента: {len(section_content)} символов")
            if section_title == '📊 Мои метрики':
                metrics = self._parse_metrics_section(section_content)
                logging.debug(f"Распарсено {len(metrics)} метрик: {metrics}")
                sections_data['metrics'] = metrics
                sphere_metrics = {}
                for metric in metrics:
                    if metric.current_value is not None:
                        if metric.sphere not in sphere_metrics:
                            sphere_metrics[metric.sphere] = []
                        sphere_metrics[metric.sphere].append(metric.current_value)
                for sphere, values in sphere_metrics.items():
                    if values:
                        sections_data['scores'][sphere] = sum(values) / len(values)
                        logging.debug(f"Вычислен score для сферы '{sphere}': {sections_data['scores'][sphere]}")
            elif section_title == '📝 Общие вопросы':
                sections_data['general_notes'] = self._parse_general_notes_section(section_content)
                logging.debug(f"Распарсены общие вопросы: {sections_data['general_notes']}")
            elif section_title in section_map:
                section_key = section_map[section_title]
                section_data = self._parse_regular_section(section_content)
                logging.debug(f"Распарсена секция '{section_title}', найдено данных для {len(section_data)} сфер: {section_data}")
                sections_data[section_key] = section_data
        # Удаляю весь rich-вывод (console.print, rprint, Table, Panel, Columns и т.д.)
        logging.debug("--- Конец парсинга PRO-секций ---")
        return ProData(
            scores=sections_data['scores'],
            metrics=sections_data['metrics'],
            problems=sections_data['problems'],
            goals=sections_data['goals'],
            blockers=sections_data['blockers'],
            achievements=sections_data['achievements'],
            general_notes=sections_data['general_notes']
        ) 