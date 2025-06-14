"""
Модуль для нормализации названий метрик.
"""
import re
from typing import Dict


class MetricNormalizer:
    """Нормализатор названий метрик."""

    def __init__(self):
        """Инициализация нормализатора."""
        self._metric_aliases = {
            "профессиональное_развитие": "professional_development",
            "проектная_активность": "project_activity",
            "физическая_активность": "physical_activity",
            "качество_сна": "sleep_quality",
            "ментальное_состояние": "mental_state",
            "отношения_с_партнером": "partner_relationship",
            "семейные_отношения": "family_relationship",
            "общение_с_друзьями": "friends_communication",
            "творческая_активность": "creative_activity",
            "финансовая_стабильность": "financial_stability"
        }

    def normalize(self, name: str) -> str:
        """
        Нормализует название метрики.
        
        Args:
            name: Название метрики
            
        Returns:
            Нормализованное название
        """
        if not name:
            return ""
            
        # Приводим к нижнему регистру и заменяем пробелы на подчеркивания
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+', '_', normalized)
        
        # Транслитерация русских букв (если есть)
        normalized = normalized.replace('а', 'a')
        normalized = normalized.replace('б', 'b')
        normalized = normalized.replace('в', 'v')
        normalized = normalized.replace('г', 'g')
        normalized = normalized.replace('д', 'd')
        normalized = normalized.replace('е', 'e')
        normalized = normalized.replace('ё', 'e')
        normalized = normalized.replace('ж', 'zh')
        normalized = normalized.replace('з', 'z')
        normalized = normalized.replace('и', 'i')
        normalized = normalized.replace('й', 'y')
        normalized = normalized.replace('к', 'k')
        normalized = normalized.replace('л', 'l')
        normalized = normalized.replace('м', 'm')
        normalized = normalized.replace('н', 'n')
        normalized = normalized.replace('о', 'o')
        normalized = normalized.replace('п', 'p')
        normalized = normalized.replace('р', 'r')
        normalized = normalized.replace('с', 's')
        normalized = normalized.replace('т', 't')
        normalized = normalized.replace('у', 'u')
        normalized = normalized.replace('ф', 'f')
        normalized = normalized.replace('х', 'h')
        normalized = normalized.replace('ц', 'ts')
        normalized = normalized.replace('ч', 'ch')
        normalized = normalized.replace('ш', 'sh')
        normalized = normalized.replace('щ', 'sch')
        normalized = normalized.replace('ъ', '')
        normalized = normalized.replace('ы', 'y')
        normalized = normalized.replace('ь', '')
        normalized = normalized.replace('э', 'e')
        normalized = normalized.replace('ю', 'yu')
        normalized = normalized.replace('я', 'ya')
        
        # Проверяем алиасы
        if normalized in self._metric_aliases:
            return self._metric_aliases[normalized]
            
        # Убираем все символы, кроме букв, цифр и подчеркиваний
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        return normalized

    def add_replacement(self, old: str, new: str) -> None:
        """
        Добавляет новое правило замены в нормализатор.
        
        Args:
            old: Что заменять
            new: На что заменять
        """
        self._metric_aliases[old.lower()] = new.lower()

    def remove_replacement(self, old: str) -> None:
        """
        Удаляет правило замены из нормализатора.
        
        Args:
            old: Какое правило удалить
        """
        self._metric_aliases.pop(old.lower(), None)

    def get_replacements(self) -> Dict[str, str]:
        """
        Возвращает текущий словарь замен.
        
        Returns:
            Копия словаря текущих правил замены
        """
        return dict(self._metric_aliases) 