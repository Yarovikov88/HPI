"""
Модуль для нормализации названий сфер.
"""

from typing import Dict, Optional, TypedDict


class SphereEmoji(TypedDict):
    """Тип для эмодзи сфер."""

    emoji: str
    name: str


class NormalizedSphere(TypedDict):
    """Тип для нормализованных сфер."""

    key: str
    name: str


class SphereNormalizer:
    """Нормализатор названий сфер."""

    def __init__(self):
        """Инициализация нормализатора."""
        self._sphere_emojis: Dict[str, str] = {
            "💖": "Отношения с любимыми",
            "🏡": "Отношения с родными",
            "🤝": "Друзья",
            "💼": "Карьера",
            "♂️": "Физическое здоровье",
            "🧠": "Ментальное здоровье",
            "🎨": "Хобби и увлечения",
            "💰": "Благосостояние",
        }

        self._normalized_spheres: Dict[str, str] = {
            "love": "Отношения с любимыми",
            "family": "Отношения с родными",
            "friends": "Друзья",
            "career": "Карьера",
            "physical": "Физическое здоровье",
            "mental": "Ментальное здоровье",
            "hobby": "Хобби и увлечения",
            "wealth": "Благосостояние",
        }

    def get_all_emojis(self) -> Dict[str, str]:
        """
        Возвращает словарь всех эмодзи и их сфер.

        Returns:
            Словарь {эмодзи: название_сферы}
        """
        return self._sphere_emojis

    def get_emoji(self, sphere: str) -> str:
        """
        Возвращает эмодзи для сферы.

        Args:
            sphere: Название сферы

        Returns:
            Эмодзи сферы или пустую строку
        """
        for emoji, name in self._sphere_emojis.items():
            if name == sphere:
                return emoji
        return ""

    def get_sphere_by_emoji(self, emoji: str) -> Optional[str]:
        """
        Возвращает название сферы по эмодзи.

        Args:
            emoji: Эмодзи сферы

        Returns:
            Название сферы или None, если не найдено
        """
        return self._sphere_emojis.get(emoji)

    def get_emoji_by_sphere(self, sphere: str) -> Optional[str]:
        """
        Возвращает эмодзи для заданной сферы.

        Args:
            sphere: Название сферы

        Returns:
            Эмодзи сферы или None, если не найдено
        """
        for emoji, name in self._sphere_emojis.items():
            if name == sphere:
                return emoji
        return None

    def normalize(self, sphere: str) -> str:
        """
        Нормализует название сферы.

        Args:
            sphere: Название сферы

        Returns:
            Нормализованное название сферы
        """
        # Проверяем прямое совпадение
        if sphere in self._normalized_spheres.values():
            return sphere

        # Проверяем по ключу
        if sphere in self._normalized_spheres:
            return self._normalized_spheres[sphere]

        # Возвращаем исходное значение, если не удалось нормализовать
        return sphere
