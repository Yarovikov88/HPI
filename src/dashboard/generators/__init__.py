"""
Пакет генераторов для системы HPI.
Предоставляет инструменты для генерации различных частей отчета.
"""

from .recommendations import (
    ActionStep,
    Evidence,
    Recommendation,
    RecommendationGenerator
)

from .sections import (
    MetricProgress,
    SphereSection,
    SectionGenerator
)

__all__ = [
    'ActionStep',
    'Evidence',
    'Recommendation',
    'RecommendationGenerator',
    'MetricProgress',
    'SphereSection',
    'SectionGenerator'
] 