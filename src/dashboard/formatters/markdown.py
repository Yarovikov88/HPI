"""
Модуль для форматирования отчетов HPI в Markdown.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..generators import ActionStep, Evidence, MetricProgress, SphereSection


class MarkdownFormatter:
    """Форматтер для создания Markdown-отчетов."""

    def __init__(self):
        """Инициализация форматтера."""
        self.logger = logging.getLogger(__name__)

    def _format_header(self, date: datetime, version: str) -> str:
        """
        Форматирует заголовок отчета.

        Args:
            date: Дата отчета
            version: Версия системы

        Returns:
            Строка с заголовком в формате Markdown
        """
        return f"""# Отчет HPI
*Сгенерировано {date.strftime('%d.%m.%Y %H:%M')} • Версия {version}*

---
"""

    def _format_metric_progress(self, metric: MetricProgress) -> str:
        """
        Форматирует прогресс по метрике.

        Args:
            metric: Объект с данными о прогрессе метрики

        Returns:
            Строка с метрикой в формате Markdown
        """
        # Определяем эмодзи для статуса
        status_emoji: str = {"improved": "📈", "declined": "📉", "stable": "📊"}.get(
            metric.status, "📊"
        )

        # Форматируем изменение
        change_str: str = ""
        if metric.previous_value is not None:
            sign = "+" if metric.change_percent > 0 else ""
            change_str = f" ({sign}{metric.change_percent:.1f}%)"

        return (
            f"- {status_emoji} **{metric.name}**: "
            f"{metric.current_value:.1f} → {metric.target_value:.1f}{change_str}"
        )

    def _format_action_steps(self, steps: List[ActionStep]) -> str:
        """
        Форматирует шаги действий из рекомендации.

        Args:
            steps: Список шагов действий

        Returns:
            Строка с шагами в формате Markdown
        """
        if not steps:
            return ""

        result: List[str] = ["### Шаги к улучшению\n"]
        for i, step in enumerate(steps, 1):
            impact = "⭐" * round(step.expected_impact * 5)
            result.append(f"{i}. {step.description}")
            result.append(f"   - Ожидаемый эффект: {impact}")
            result.append(f"   - Оценка времени: {step.estimated_time}")
            if step.dependencies:
                deps = ", ".join(step.dependencies)
                result.append(f"   - Требуется: {deps}")
            result.append("")

        return "\n".join(result)

    def _format_evidence(self, evidence: Evidence) -> str:
        """
        Форматирует доказательную базу рекомендации.

        Args:
            evidence: Объект с доказательной базой

        Returns:
            Строка с доказательствами в формате Markdown
        """
        if not evidence:
            return ""

        result: List[str] = ["### Обоснование\n"]

        # Добавляем основные наблюдения
        if evidence.data_points:
            result.append("**Наблюдения:**")
            for point in evidence.data_points:
                result.append(f"- {point}")
            result.append("")

        # Добавляем корреляции
        if evidence.correlations:
            result.append("**Корреляции:**")
            for corr in evidence.correlations:
                result.append(f"- {corr}")
            result.append("")

        # Добавляем исторический успех
        if evidence.historical_success:
            success_percent = evidence.historical_success * 100
            result.append(f"**Исторический успех:** {success_percent:.1f}%\n")

        return "\n".join(result)

    def _format_sphere_section(self, section: SphereSection) -> str:
        """
        Форматирует секцию для сферы.

        Args:
            section: Объект с данными секции

        Returns:
            Строка с секцией в формате Markdown
        """
        # Форматируем заголовок с эмодзи и оценкой
        result: List[str] = [f"## {section.emoji} {section.name}"]

        # Добавляем текущую оценку и изменение
        score_line = f"**Текущая оценка:** {section.current_score:.1f}"
        if section.previous_score is not None:
            sign = "+" if section.change_percent > 0 else ""
            score_line += f" ({sign}{section.change_percent:.1f}%)"
        result.append(score_line + "\n")

        # Добавляем метрики
        if section.metrics:
            result.append("### Метрики")
            for metric in section.metrics:
                result.append(self._format_metric_progress(metric))
            result.append("")

        # Добавляем проблемы
        if section.problems:
            result.append("### Проблемы")
            for problem in section.problems:
                result.append(f"- {problem}")
            result.append("")

        # Добавляем цели
        if section.goals:
            result.append("### Цели")
            for goal in section.goals:
                result.append(f"- {goal}")
            result.append("")

        # Добавляем блокеры
        if section.blockers:
            result.append("### Блокеры")
            for blocker in section.blockers:
                result.append(f"- {blocker}")
            result.append("")

        # Добавляем рекомендацию
        if section.recommendation:
            result.append("### Рекомендация")
            rec = section.recommendation
            if isinstance(rec, list):
                for r in rec:
                    result.append(f"- {str(r)}")
            elif isinstance(rec, str):
                result.append(f"- {rec}")
            elif hasattr(rec, "title") and hasattr(rec, "description"):
                result.append(f"**{rec.title}**")
                result.append(f"\n{rec.description}\n")
                # Добавляем шаги действий
                if hasattr(rec, "action_steps"):
                    result.append(self._format_action_steps(rec.action_steps))
                # Добавляем доказательную базу
                if hasattr(rec, "evidence"):
                    result.append(self._format_evidence(rec.evidence))
            else:
                result.append(f"- {str(rec)}")

        return "\n".join(result)

    def _format_metrics_json(self, sections: Dict[str, SphereSection]) -> str:
        """
        Форматирует метрики и сравнение в JSON-блок.

        Args:
            sections: Словарь с секциями по сферам

        Returns:
            Строка с JSON-блоком метрик
        """
        metrics_data: Dict[str, Dict] = {"metrics": {}, "comparison": {}}

        for sphere_name, section in sections.items():
            # Добавляем метрики
            if section.metrics:
                metrics_data["metrics"][sphere_name] = []
                for metric in section.metrics:
                    metric_data = {
                        "name": metric.name,
                        "current_value": metric.current_value,
                        "target_value": metric.target_value,
                        "previous_value": metric.previous_value,
                        "change_percent": metric.change_percent,
                        "status": metric.status,
                    }
                    metrics_data["metrics"][sphere_name].append(metric_data)

            # Добавляем сравнение
            metrics_data["comparison"][sphere_name] = {
                "current_score": section.current_score,
                "previous_score": section.previous_score,
                "change_percent": section.change_percent,
            }

        return (
            f"\n```json\n"
            f"{json.dumps(metrics_data, indent=2, ensure_ascii=False)}\n"
            f"```\n"
        )

    def format_report(
        self,
        sections: Dict[str, SphereSection],
        history: List[Dict],
        date: datetime,
        version: str,
    ) -> str:
        """
        Основной метод для форматирования всего отчета.

        Args:
            sections: Словарь с секциями по сферам
            history: История изменений HPI
            date: Дата отчета
            version: Версия системы

        Returns:
            Строка с полным отчетом в формате Markdown
        """
        # Форматируем заголовок
        report: str = self._format_header(date, version)

        # Добавляем HPI и диаграммы
        report += self._format_hpi_section(history)

        # Добавляем все остальные секции
        for section in sections.values():
            report += self._format_sphere_section(section)
            report += "\n---\n"

        # Добавляем JSON-блок с метриками
        report += self._format_metrics_json(sections)

        return report

    def _get_latest_diagrams(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Находит последние файлы диаграмм (радар и тренд) в указанной директории.
        """
        files = os.listdir(path)
        # Фильтруем файлы, чтобы найти только нужные изображения
        radar_files = [f for f in files if f.endswith("_radar.png")]
        trend_files = [f for f in files if f.endswith("_trend.png")]

        # Сортируем по дате в названии файла (YYYY-MM-DD)
        latest_radar = sorted(radar_files, reverse=True)[0] if radar_files else None
        latest_trend = sorted(trend_files, reverse=True)[0] if trend_files else None

        # Возвращаем относительные пути для Markdown
        radar_path = os.path.join(path, latest_radar) if latest_radar else None
        trend_path = os.path.join(path, latest_trend) if latest_trend else None

        # Заменяем бэкслэши на слэши для корректной работы в Markdown
        if radar_path:
            radar_path = radar_path.replace("\\\\", "/")
        if trend_path:
            trend_path = trend_path.replace("\\\\", "/")

        return trend_path, radar_path

    def _format_hpi_section(self, history: List[Dict]) -> str:
        """
        Форматирует секцию с общим HPI, диаграммами и таблицей баланса.
        """
        if not history:
            return ""

        # Получаем последний HPI
        latest = history[-1]
        latest_hpi = latest["hpi"]
        status_emoji = (
            "🟢"
            if latest_hpi >= 85
            else "🔵" if latest_hpi >= 70 else "🟡" if latest_hpi >= 55 else "🔴"
        )

        result: List[str] = [
            f"## Human Performance Index: {latest_hpi:.1f} {status_emoji}\n"
        ]

        # Получаем пути к диаграммам
        trend_path, radar_path = self._get_latest_diagrams("reports_final/images")

        # Добавляем тренд
        result.append("> [!note]- 📈 Динамика HPI")
        if trend_path:
            result.append(f"> ![{trend_path}]({trend_path})")
        result.append(">\n")

        # Добавляем радар и таблицу баланса
        result.append("> [!note]- ⚖️ Баланс по сферам")
        if radar_path:
            result.append(f"> ![{radar_path}]({radar_path})")
        result.append(">")
        result.append("> | Дата | 💖 | 🏡 | 🤝 | 💼 | ♂️ | 🧠 | 🎨 | 💰 |")
        result.append("> |:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

        # Выводим строки таблицы в обратном порядке
        for report in reversed(history):
            date_str = report["date"].strftime("%Y-%m-%d")
            scores = [
                report["scores"].get("Отношения с любимыми", 0.0),
                report["scores"].get("Отношения с родными", 0.0),
                report["scores"].get("Друзья", 0.0),
                report["scores"].get("Карьера", 0.0),
                report["scores"].get("Физическое здоровье", 0.0),
                report["scores"].get("Ментальное здоровье", 0.0),
                report["scores"].get("Хобби и увлечения", 0.0),
                report["scores"].get("Благосостояние", 0.0),
            ]
            scores_str = " | ".join([f"{s:.1f}" for s in scores])
            result.append(f"> | {date_str} | {scores_str} |")

        result.append("\n---\n")

        return "\n".join(result)
