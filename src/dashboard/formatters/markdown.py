"""
Модуль для форматирования отчетов HPI в Markdown.
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..generators import SphereSection, MetricProgress, Recommendation
from ...trend import generate_trend_chart


class MarkdownFormatter:
    """Форматтер для создания Markdown-отчетов."""

    def __init__(self):
        """Инициализация форматтера."""
        self.logger = logging.getLogger(__name__)

    def _format_header(
        self,
        date: datetime,
        version: str
    ) -> str:
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

    def _format_metric_progress(
        self,
        metric: MetricProgress
    ) -> str:
        """
        Форматирует прогресс по метрике.
        
        Args:
            metric: Объект с данными о прогрессе метрики
            
        Returns:
            Строка с метрикой в формате Markdown
        """
        # Определяем эмодзи для статуса
        status_emoji = {
            "improved": "📈",
            "declined": "📉",
            "stable": "📊"
        }.get(metric.status, "📊")
        
        # Форматируем изменение
        change_str = ""
        if metric.previous_value is not None:
            sign = "+" if metric.change_percent > 0 else ""
            change_str = f" ({sign}{metric.change_percent:.1f}%)"
            
        return f"""- {status_emoji} **{metric.name}**: {metric.current_value:.1f} → {metric.target_value:.1f}{change_str}"""

    def _format_action_steps(
        self,
        steps: List
    ) -> str:
        """
        Форматирует шаги действий из рекомендации.
        
        Args:
            steps: Список шагов действий
            
        Returns:
            Строка с шагами в формате Markdown
        """
        if not steps:
            return ""
            
        result = ["### Шаги к улучшению\n"]
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

    def _format_evidence(
        self,
        evidence
    ) -> str:
        """
        Форматирует доказательную базу рекомендации.
        
        Args:
            evidence: Объект с доказательной базой
            
        Returns:
            Строка с доказательствами в формате Markdown
        """
        if not evidence:
            return ""
            
        result = ["### Обоснование\n"]
        
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

    def _format_sphere_section(
        self,
        section: SphereSection
    ) -> str:
        """
        Форматирует секцию для сферы.
        
        Args:
            section: Объект с данными секции
            
        Returns:
            Строка с секцией в формате Markdown
        """
        # Форматируем заголовок с эмодзи и оценкой
        result = [f"## {section.emoji} {section.name}"]
        
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
            result.append(f"**{section.recommendation.title}**")
            result.append(f"\n{section.recommendation.description}\n")
            
            # Добавляем шаги действий
            result.append(self._format_action_steps(section.recommendation.action_steps))
            
            # Добавляем доказательную базу
            result.append(self._format_evidence(section.recommendation.evidence))
            
        return "\n".join(result)

    def format_report(
        self,
        sections: Dict[str, SphereSection],
        date: datetime,
        version: str
    ) -> str:
        """
        Форматирует полный отчет.
        
        Args:
            sections: Словарь с секциями отчета
            date: Дата отчета
            version: Версия системы
            
        Returns:
            Строка с полным отчетом в формате Markdown
        """
        # Начинаем с заголовка
        result = [self._format_header(date, version)]
        
        # Удаляем оглавление (Содержание)
        # result.append("## Содержание\n")
        # for section in sections.values():
        #     result.append(f"- [{section.emoji} {section.name}](#{section.name.lower().replace(' ', '-')})")
        # result.append("\n---\n")
        result.append("\n---\n")
        
        # Добавляем секции
        for section in sections.values():
            result.append(self._format_sphere_section(section))
            result.append("\n---\n")
            
        return "\n".join(result)

    def format_dashboard(
        self,
        sections: Dict[str, SphereSection],
        history: List[Dict],
        date: datetime,
        version: str
    ) -> str:
        """
        Форматирует дашборд в специальном формате.
        
        Args:
            sections: Словарь с секциями дашборда
            history: История изменений HPI
            date: Дата обновления
            version: Версия системы
            
        Returns:
            Строка с дашбордом в формате Markdown
        """
        # Получаем последний HPI и оценки
        latest_report = history[-1] if history else None
        latest_hpi = latest_report['hpi'] if latest_report else 0.0
        latest_scores = latest_report['scores'] if latest_report else {}
        
        # Определяем статус
        status = "🟢" if latest_hpi >= 70 else "🟡" if latest_hpi >= 50 else "🔴"
        
        # Генерируем график тренда
        trend_path = generate_trend_chart(history)
        if not trend_path:
            self.logger.error("Не удалось сгенерировать график тренда")
            trend_path = "../reports_final/images/trend.png"  # Fallback путь
        
        # Добавляем заголовок
        result = [f"# HPI Dashboard v{version}\n\n"]
        
        # Добавляем основные секции
        result.extend([
            f"## Human Performance Index: {latest_hpi:.1f} {status}\n",
            "> [!note]- 📈 Динамика HPI",
            f"> ![Динамика HPI]({trend_path})",
            ">\n",
            "> [!note]- ⚖️ Баланс по сферам",
            "> ![Баланс по сферам](../reports_final/images/2025-06-14_radar.png)",
            ">",
            "> | Дата | 💖 | 🏡 | 🤝 | 💼 | ♂️ | 🧠 | 🎨 | 💰 |",
            "> |:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
        ])
        
        # Добавляем историю в обратном порядке (новые даты сверху)
        for report in reversed(history):
            scores = report['scores']
            result.append(
                f"> | {report['date']} | " +
                f"{scores.get('Отношения с любимыми', 0.0):.1f} | " +
                f"{scores.get('Отношения с родными', 0.0):.1f} | " +
                f"{scores.get('Друзья', 0.0):.1f} | " +
                f"{scores.get('Карьера', 0.0):.1f} | " +
                f"{scores.get('Физическое здоровье', 0.0):.1f} | " +
                f"{scores.get('Ментальное здоровье', 0.0):.1f} | " +
                f"{scores.get('Хобби и увлечения', 0.0):.1f} | " +
                f"{scores.get('Благосостояние', 0.0):.1f} |"
            )
        
        result.append("\n---\n")
        result.append("## PRO-разделы\n")

        # Проблемы
        has_problems = any(section.problems for section in sections.values())
        if has_problems:
            result.append("> [!data]- 🛑 Мои проблемы")
            result.append("> | Сфера | Проблема |")
            result.append("> |:---:|:---|")
            for section in sections.values():
                for problem in section.problems:
                    result.append(f"> | {section.emoji} | {problem} |")
        else:
            result.append("> [!example]- 🛑 Мои проблемы")
            result.append("> | Сфера | Проблема |")
            result.append("> |:---:|:---|")
            # Можно добавить примерные строки, если нужно

        result.append("\n")
        # Цели
        has_goals = any(section.goals for section in sections.values())
        if has_goals:
            result.append("> [!data]- 🎯 Мои цели")
            result.append("> | Сфера | Цель |")
            result.append("> |:---:|:---|")
            for section in sections.values():
                for goal in section.goals:
                    result.append(f"> | {section.emoji} | {goal} |")
        else:
            result.append("> [!example]- 🎯 Мои цели")
            result.append("> | Сфера | Цель |")
            result.append("> |:---:|:---|")

        result.append("\n")
        # Блокеры
        has_blockers = any(section.blockers for section in sections.values())
        if has_blockers:
            result.append("> [!data]- 🚧 Мои блокеры")
            result.append("> | Сфера | Блокер |")
            result.append("> |:---:|:---|")
            for section in sections.values():
                for blocker in section.blockers:
                    result.append(f"> | {section.emoji} | {blocker} |")
        else:
            result.append("> [!example]- 🚧 Мои блокеры")
            result.append("> | Сфера | Блокер |")
            result.append("> |:---:|:---|")

        result.append("\n")
        # Метрики
        has_metrics = any(section.metrics for section in sections.values())
        if has_metrics:
            result.append("> [!data]- 📊 Мои метрики")
            result.append("> | Сфера | Метрика | Значение | Цель | Изменение |")
            result.append("> |:---:|:---|:---:|:---:|:---:|")
            for section in sections.values():
                for metric in section.metrics:
                    change = ""
                    if metric.previous_value is not None and metric.current_value is not None:
                        sign = "+" if metric.change_percent > 0 else ""
                        change = f"{sign}{metric.change_percent:.1f}%"
                    current = f"{metric.current_value:.1f}" if metric.current_value is not None else "—"
                    target = f"{metric.target_value:.1f}" if metric.target_value is not None else "—"
                    result.append(
                        f"> | {section.emoji} | {metric.name} | {current} | "
                        f"{target} | {change} |"
                    )
        else:
            result.append("> [!example]- 📊 Мои метрики")
            result.append("> | Сфера | Метрика | Значение | Цель | Изменение |")
            result.append("> |:---:|:---|:---:|:---:|:---:|")

        result.append("\n")
        # Рекомендации
        has_recs = any(section.recommendation for section in sections.values())
        if has_recs:
            result.append("> [!data]- 💡 Мои рекомендации")
            result.append("> | Сфера | Рекомендация |")
            result.append("> |:---:|:---|")
            for section in sections.values():
                if section.recommendation:
                    rec = section.recommendation
                    if isinstance(rec, str):
                        result.append(f"> | {section.emoji} | {rec} |")
                    elif isinstance(rec, list):
                        for r in rec:
                            result.append(f"> | {section.emoji} | {r} |")
                    elif hasattr(rec, 'title') and hasattr(rec, 'description'):
                        result.append(f"> | {section.emoji} | **{rec.title}**<br>{rec.description} |")
                        if hasattr(rec, 'action_steps') and rec.action_steps:
                            result.append("> | | **Шаги:**<br>" + "<br>".join(rec.action_steps))
                    else:
                        result.append(f"> | {section.emoji} | {str(rec)} |")
        else:
            result.append("> [!example]- 💡 Мои рекомендации")
            result.append("> | Сфера | Рекомендация |")
            result.append("> |:---:|:---|")

        return "\n".join(result) 