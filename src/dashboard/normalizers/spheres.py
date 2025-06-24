"""
Модуль для нормализации названий сфер на основе единого конфига.
"""
from typing import Dict, Optional, List
from src.config import SPHERE_CONFIG


class SphereNormalizer:
    """
    Нормализатор названий сфер. Использует SPHERE_CONFIG как единственный источник правды.
    """

    def __init__(self):
        """Инициализация нормализатора."""
        self._name_to_normalized: Dict[str, str] = {}
        self._normalized_to_name: Dict[str, str] = {}
        self._normalized_to_emoji: Dict[str, str] = {}
        self._emoji_to_normalized: Dict[str, str] = {}

        for config in SPHERE_CONFIG:
            name = config["name"]
            normalized = config["normalized"]
            emoji = config["emoji"]

            self._name_to_normalized[name] = normalized
            self._normalized_to_name[normalized] = name
            self._normalized_to_emoji[normalized] = emoji
            self._emoji_to_normalized[emoji] = normalized

    def get_all_normalized_names(self) -> List[str]:
        """Возвращает список всех нормализованных имен в правильном порядке."""
        return [config["normalized"] for config in SPHERE_CONFIG]

    def get_original_name(self, normalized_name: str) -> str:
        """Возвращает оригинальное название сферы по нормализованному."""
        return self._normalized_to_name.get(normalized_name, normalized_name)

    def get_emoji(self, normalized_name: str) -> str:
        """Возвращает эмодзи для сферы по нормализованному названию."""
        return self._normalized_to_emoji.get(normalized_name, "")

    def normalize(self, sphere_identifier: str) -> Optional[str]:
        """
        Нормализует название сферы по любому идентификатору (оригинальное имя, эмодзи, нормализованное имя).
        """
        # Уже нормализовано?
        if sphere_identifier in self._normalized_to_name:
            return sphere_identifier
        # Это оригинальное название?
        if sphere_identifier in self._name_to_normalized:
            return self._name_to_normalized[sphere_identifier]
        # Это эмодзи?
        if sphere_identifier in self._emoji_to_normalized:
            return self._emoji_to_normalized[sphere_identifier]
        
        # Если ничего не подошло, возвращаем None, чтобы обозначить ошибку
        return None 