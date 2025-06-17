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
            date_str = filename.split('_')[0]
            return datetime.strptime(date_str, '%Y-%m-%d')
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
            Словарь {сфера: оценка}
        """
        scores = {}
        
        # Сначала пробуем найти в формате строк
        pattern = r'([💖🏡🤝💼♂️🧠🎨💰])\s+([^:]+):\s+(\d+\.\d+)\s+[🟡🔵🔴]'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            emoji = match.group(1)
            value = float(match.group(3))
            sphere = self.sphere_normalizer.get_sphere_by_emoji(emoji)
            if sphere:
                scores[sphere] = value
                
        # Если не нашли, ищем в формате таблицы
        if not scores:
            pattern = r'\|\s*([^|]+)\s*\|\s*(\d+\.\d+)\s*\|\s*[🟡🔵🔴]\s*\|'
            matches = re.finditer(pattern, content)
            
            for match in matches:
                sphere = match.group(1).strip()
                value = float(match.group(2))
                if sphere in [
                    "Отношения с любимыми",
                    "Отношения с родными",
                    "Друзья",
                    "Карьера",
                    "Физическое здоровье",
                    "Ментальное здоровье",
                    "Хобби и увлечения",
                    "Благосостояние"
                ]:
                    scores[sphere] = value
            
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
            
            if not hpi or not scores:
                self.logger.warning(f"Не удалось извлечь все данные из отчета: {file_path}")
                return None
                
            return HistoricalReport(
                date=date,
                hpi=hpi,
                scores=scores,
                file_path=file_path,
                metrics=metrics
            )
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге отчета {file_path}: {e}")
            return None

    def get_history(self) -> List[HistoricalReport]:
        """
        Получает историю из всех отчетов в директории, только по датам, для которых есть черновики.
        
        Returns:
            Список объектов HistoricalReport
        """
        history = []
        # Получаем список дат черновиков
        draft_dates = set()
        draft_dir = os.path.join(os.path.dirname(self.reports_dir), 'reports_draft')
        if os.path.exists(draft_dir):
            for filename in os.listdir(draft_dir):
                if filename.endswith('_draft.md'):
                    try:
                        date_str = filename.split('_')[0]
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        draft_dates.add(date.date())
                    except Exception:
                        continue
        if not os.path.exists(self.reports_dir):
            self.logger.error(f"Директория с отчетами не найдена: {self.reports_dir}")
            return history
        # Собираем все файлы отчетов только по датам черновиков
        for filename in os.listdir(self.reports_dir):
            if not filename.endswith('_report.md'):
                continue
            date = self._extract_date_from_filename(filename)
            if not date or date.date() not in draft_dates:
                continue
            file_path = os.path.join(self.reports_dir, filename)
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