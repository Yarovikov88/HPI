"""
Модуль для парсинга базы вопросов HPI.
"""
import os
import re
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..normalizers import SphereNormalizer


@dataclass
class MetricDefinition:
    """Определение метрики из базы вопросов."""
    name: str
    unit: Optional[str] = None
    type: Optional[str] = None


@dataclass
class SphereMetrics:
    """Метрики для конкретной сферы."""
    sphere_name: str
    sphere_emoji: str
    metrics: List[MetricDefinition]


class QuestionsDatabaseParser:
    """Парсер базы вопросов HPI."""

    def __init__(self, database_path: str):
        """
        Инициализация парсера.
        
        Args:
            database_path: Путь к файлу базы вопросов (questions.md)
        """
        self.database_path = database_path
        self.sphere_normalizer = SphereNormalizer()
        self.logger = logging.getLogger(__name__)

    def _extract_json_blocks(self, content: str) -> Dict[str, str]:
        """
        Извлекает JSON-блоки для каждой сферы из контента.
        
        Args:
            content: Содержимое файла базы вопросов
            
        Returns:
            Словарь {название_сферы: json_блок}
        """
        json_blocks = {}
        
        # Ищем заголовок типа "## 💖 Отношения с любимыми" и следующий за ним блок ```json ... ```
        pattern = re.compile(
            r"##\s*(?P<emoji>[\U0001F000-\U0001FA95\s\S]+?)\s*(?P<name>.*?)\n```json\n([\s\S]+?)\n```",
            re.DOTALL
        )
        
        for match in pattern.finditer(content):
            emoji = match.group('emoji').strip()
            name = match.group('name').strip()
            json_content = match.group(3)
            
            # Проверяем, что это валидная сфера
            sphere = self.sphere_normalizer.get_sphere_by_emoji(emoji)
            if sphere:
                json_blocks[sphere] = json_content
            else:
                self.logger.warning(f"Найден блок с неизвестным эмодзи: {emoji}")
                
        return json_blocks

    def _parse_metrics_from_json(self, json_content: str) -> List[MetricDefinition]:
        """
        Извлекает определения метрик из JSON-блока.
        
        Args:
            json_content: JSON-строка с данными сферы
            
        Returns:
            Список определений метрик
        """
        metrics = []
        try:
            data = json.loads(json_content)
            for item in data:
                if item.get("category") == "metrics" and "metrics" in item:
                    for metric in item["metrics"]:
                        metrics.append(
                            MetricDefinition(
                                name=metric.get("name", ""),
                                unit=metric.get("unit"),
                                type=metric.get("type")
                            )
                        )
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка декодирования JSON: {e}")
        
        return metrics

    def parse(self) -> List[SphereMetrics]:
        """
        Парсит файл базы вопросов и извлекает все метрики по сферам.
        
        Returns:
            Список объектов SphereMetrics с метриками для каждой сферы
        """
        if not os.path.exists(self.database_path):
            self.logger.error(f"Файл базы данных вопросов не найден: {self.database_path}")
            return []
            
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла базы вопросов: {e}")
            return []
            
        # Извлекаем JSON-блоки для каждой сферы
        json_blocks = self._extract_json_blocks(content)
        
        # Парсим метрики из каждого блока
        sphere_metrics = []
        for sphere_name, json_content in json_blocks.items():
            metrics = self._parse_metrics_from_json(json_content)
            if metrics:
                sphere_metrics.append(
                    SphereMetrics(
                        sphere_name=sphere_name,
                        sphere_emoji=self.sphere_normalizer.get_emoji_by_sphere(sphere_name),
                        metrics=metrics
                    )
                )
            
        self.logger.info(f"Извлечены метрики для {len(sphere_metrics)} сфер")
        return sphere_metrics

    def get_metric_names(self, sphere: Optional[str] = None) -> List[str]:
        """
        Возвращает список названий всех метрик.
        
        Args:
            sphere: Опционально, название сферы для фильтрации
            
        Returns:
            Список названий метрик
        """
        metrics = []
        for sphere_metrics in self.parse():
            if not sphere or sphere_metrics.sphere_name == sphere:
                metrics.extend([m.name for m in sphere_metrics.metrics])
        return metrics

    def parse_spheres_master_list(self) -> List[str]:
        """
        Парсит master-таблицу сфер из начала файла questions.md и возвращает список названий сфер.
        """
        if not os.path.exists(self.database_path):
            self.logger.error(f"Файл базы данных вопросов не найден: {self.database_path}")
            return []
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла базы вопросов: {e}")
            return []
        # Ищем таблицу сфер
        pattern = re.compile(r"\|\s*Короткое название\s*\|.*?\n(\|.*?\n)+", re.DOTALL)
        match = pattern.search(content)
        if not match:
            self.logger.error("Не найдена master-таблица сфер в базе вопросов!")
            return []
        table = match.group(0)
        lines = [l for l in table.splitlines() if l.strip().startswith('|') and not l.strip().startswith('|:')]
        spheres = []
        for line in lines[1:]:
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) >= 3:
                spheres.append(parts[1])  # Полное название
        return spheres 