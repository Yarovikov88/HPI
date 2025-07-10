"""
Модуль для работы с историческими данными HPI.
"""
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..normalizers import SphereNormalizer
from .pro_data import ProMetric
import json


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
    hpi: float
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
        # Паттерн для YYYY-MM-DD
        match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except ValueError:
                self.logger.warning(f"Некорректный формат даты в имени файла: {filename}")
                return None
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
        pattern = r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*(\d+\.\d+)\*\*\s*\|\s*[🟡🔵🔴🟢]\s*\|'
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))
            
        # Если не нашли, ищем в старом формате таблицы
        pattern = r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*(\d+\.\d+)\*\*\s*\|'
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))
            
        # Если не нашли, ищем в формате строки
        pattern = r'HPI:\s*(\d+\.\d+)\s*[🟡🔵🔴🟢]'
        match = re.search(pattern, content)
        if match:
            return float(match.group(1))
            
        # Если не нашли, ищем в итоговой таблице
        pattern = r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*(\d+\.\d+)\*\*\s*\|\s*[🟡🔵🔴🟢]\s*\|'
        match = re.search(pattern, content)
        return float(match.group(1)) if match else None

    def _extract_scores(self, content: str) -> Dict[str, float]:
        """
        Извлекает оценки сфер из содержимого отчета.
        
        Args:
            content: Содержимое отчета
            
        Returns:
            Словарь {нормализованная_сфера: оценка}
        """
        scores = {}
        
        # Паттерн для поиска всех таблиц с баллами
        pattern = r'\|\s*([^|]+?)\s*\|\s*(\d+\.\d+)\s*\|\s*[🟡🔵🔴]\s*\|'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            sphere_identifier = match.group(1).strip()
            value = float(match.group(2))
            
            # Пропускаем строку с HPI
            if 'Итоговый HPI' in sphere_identifier:
                continue
            
            # Нормализуем сферу по названию или эмодзи
            normalized_sphere = self.sphere_normalizer.normalize(sphere_identifier)
            
            if normalized_sphere:
                scores[normalized_sphere] = value
            else:
                self.logger.warning(
                    f"Не удалось нормализовать сферу: '{sphere_identifier}'"
                )
                
        return scores

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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Извлекаем данные
            hpi = self._extract_hpi(content)
            scores = self._extract_scores(content)

            # --- Новый код: парсим метрики из таблицы ---
            metrics = []
            # Ищем секцию метрик по заголовку
            metric_section_match = re.search(r'(?:📊 Мои метрики|Мои метрики)[^\n]*\n((?:\|.*\n)+)', content)
            if metric_section_match:
                from .pro_data import ProDataParser
                parser = ProDataParser()
                metrics = parser._parse_metrics_section(metric_section_match.group(1))
            # --- Конец нового кода ---

            # --- Десериализация PRO-секций из JSON-блока ---
            problems = goals = blockers = achievements = general_notes = None
            json_block_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_block_match:
                try:
                    pro_json = json.loads(json_block_match.group(1))
                    problems = pro_json.get('problems')
                    goals = pro_json.get('goals')
                    blockers = pro_json.get('blockers')
                    achievements = pro_json.get('achievements')
                    general_notes = pro_json.get('general_notes')
                except Exception as e:
                    self.logger.warning(f"Ошибка при парсинге JSON-блока PRO-секций: {e}")
            # --- Конец десериализации ---
            
            if not hpi or not scores:
                self.logger.warning(f"Не удалось извлечь все данные из отчета: {file_path}")
                return None
                
            return HistoricalReport(
                date=date,
                hpi=hpi,
                scores=scores,
                file_path=file_path,
                metrics=metrics,
                problems=problems,
                goals=goals,
                blockers=blockers,
                achievements=achievements,
                general_notes=general_notes
            )
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге отчета {file_path}: {e}")
            return None

    def get_history(self) -> List[HistoricalReport]:
        """
        Получает историю из всех финальных отчетов в директории, без привязки к драфтам.
        Returns:
            Список объектов HistoricalReport
        """
        history = []
        if not os.path.exists(self.reports_dir):
            self.logger.error(f"Директория с отчетами не найдена: {self.reports_dir}")
            return history
        for filename in os.listdir(self.reports_dir):
            file_path = os.path.join(self.reports_dir, filename)
            # Пропускаем директории (например, 'images')
            if os.path.isdir(file_path):
                continue
            if not filename.endswith('_report.md'):
                continue
            date = self._extract_date_from_filename(filename)
            if not date:
                continue
            report = self.parse_report(file_path)
            if report:
                history.append(report)
        # Сортируем по дате
        history.sort(key=lambda r: r.date)
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
                        sphere=sphere,
                        date=report.date,
                        score=score,
                        emoji=emoji
                    )
                )
                
        return history 