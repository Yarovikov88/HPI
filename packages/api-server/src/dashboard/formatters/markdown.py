"""
Модуль для форматирования отчетов HPI в Markdown.
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re

from ..generators import SphereSection, MetricProgress, Recommendation
from ...trend import generate_trend_chart
from ..normalizers import SphereNormalizer
from ..generators.sections import SphereSection


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
            rec = section.recommendation
            if isinstance(rec, list):
                for r in rec:
                    result.append(f"- {str(r)}")
            elif isinstance(rec, str):
                result.append(f"- {rec}")
            elif hasattr(rec, 'title') and hasattr(rec, 'description'):
                result.append(f"**{rec.title}**")
                result.append(f"\n{rec.description}\n")
                # Добавляем шаги действий
                if hasattr(rec, 'action_steps'):
                    result.append(self._format_action_steps(rec.action_steps))
                # Добавляем доказательную базу
                if hasattr(rec, 'evidence'):
                    result.append(self._format_evidence(rec.evidence))
            else:
                result.append(f"- {str(rec)}")
            
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
        version: str,
        openai_error: Optional[str] = None
    ) -> str:
        """
        Форматирует дашборд в специальном формате.
        
        Args:
            sections: Словарь с секциями дашборда
            history: История изменений HPI
            date: Дата обновления
            version: Версия системы
            openai_error: Ошибка теста OpenAI
            
        Returns:
            Строка с дашбордом в формате Markdown
        """
        result = []
        # Отладочный вывод структуры sections
        # result.append("> [!note]- DEBUG: sections keys/types: " + ", ".join([f"{k}: {type(v)}" for k, v in sections.items()]))
        
        # Фильтруем только SphereSection для проверки наличия проблем и т.д.
        sphere_sections = [s for s in sections.values() if isinstance(s, SphereSection)]
        has_problems = any(s.problems for s in sphere_sections)
        has_goals = any(s.goals for s in sphere_sections)
        has_blockers = any(s.blockers for s in sphere_sections)
        has_achievements = any(getattr(s, 'achievements', None) for s in sphere_sections)
        
        # Получаем последний HPI и оценки
        latest_report = history[-1] if history else None
        if latest_report:
            # Если это объект, а не dict
            latest_hpi = getattr(latest_report, 'hpi', 0.0)
            latest_scores = getattr(latest_report, 'scores', {})
        else:
            latest_hpi = 0.0
            latest_scores = {}
        # Определяем статус
        status = "🟢" if latest_hpi >= 70 else "🟡" if latest_hpi >= 50 else "🔴"
        
        # Генерируем график тренда
        trend_path = None
        if history:
            last_report = history[-1]
            date = getattr(last_report, 'date', None)
            if date:
                date_str = date.strftime('%Y-%m-%d')
                abs_candidate_path = os.path.join('reports_final', 'images', f'{date_str}_trend.png')
                rel_candidate_path = f"../reports_final/images/{date_str}_trend.png"
                if os.path.exists(abs_candidate_path):
                    trend_path = rel_candidate_path
        if not trend_path:
            abs_fallback_path = os.path.join('reports_final', 'images', 'trend.png')
            rel_fallback_path = '../reports_final/images/trend.png'
            if os.path.exists(abs_fallback_path):
                trend_path = rel_fallback_path
        if not trend_path:
            trend_md = '> График недоступен'
        else:
            trend_md = f"> ![Динамика HPI]({trend_path})"
        
        # Добавляем заголовок
        result.append(f"# HPI Dashboard v{version}\n\n")
        
        # Добавляем основные секции
        result.extend([
            f"## Human Performance Index: {latest_hpi:.1f} {status}\n",
            "> [!note]- 📈 Динамика HPI",
            trend_md,
            ">\n",
            "> [!note]- ⚖️ Баланс по сферам",
            "> ![Баланс по сферам](../reports_final/images/2025-06-14_radar.png)",
            ">",
            "> | Дата | 💖 | 🏡 | 🤝 | 💼 | ♂️ | 🧠 | 🎨 | 💰 |",
            "> |:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
        ])
        
        # Добавляем историю в обратном порядке (новые даты сверху)
        for report in reversed(history):
            # Если это объект, а не dict
            date = getattr(report, 'date', None)
            if date:
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = report.get('date', '')
            scores = getattr(report, 'scores', None)
            if scores is None:
                scores = report.get('scores', {})
            result.append(
                f"> | {date_str} | " +
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

        # Используем нормализованные имена сфер для master_order
        normalizer = SphereNormalizer()
        master_order = [
            normalizer.normalize('Отношения с любимыми'),
            normalizer.normalize('Отношения с родными'),
            normalizer.normalize('Друзья'),
            normalizer.normalize('Карьера'),
            normalizer.normalize('Физическое здоровье'),
            normalizer.normalize('Ментальное здоровье'),
            normalizer.normalize('Хобби и увлечения'),
            normalizer.normalize('Благосостояние')
        ]

        # Проблемы
        result.append("> [!example]- <span style='color:#b37feb'>🛑 Мои проблемы</span>")
        result.append("> | Сфера | Проблема |")
        result.append("> |:---:|:---|")
        for section in sphere_sections:
            emoji = section.emoji
            for problem in section.problems:
                result.append(f"> | {emoji} | {problem} |")
        result.append("\n")
        # Цели
        result.append("> [!example]- <span style='color:#b37feb'>🎯 Мои цели</span>")
        result.append("> | Сфера | Цель |")
        result.append("> |:---:|:---|")
        for section in sphere_sections:
            emoji = section.emoji
            for goal in section.goals:
                result.append(f"> | {emoji} | {goal} |")
        result.append("\n")
        # Блокеры
        result.append("> [!example]- <span style='color:#b37feb'>🚧 Мои блокеры</span>")
        result.append("> | Сфера | Блокер |")
        result.append("> |:---:|:---|")
        for section in sphere_sections:
            emoji = section.emoji
            for blocker in section.blockers:
                result.append(f"> | {emoji} | {blocker} |")
        result.append("\n")
        # Метрики
        result.append("> [!example]- <span style='color:#b37feb'>📊 Мои метрики</span>")
        result.append("> | Сфера | Метрика | Значение | Цель | Изменение |")
        result.append("> |:---:|:---|:---:|:---:|:---:|")
        for section in sphere_sections:
            emoji = section.emoji
            for metric in section.metrics:
                change = metric.current_value - (metric.previous_value or 0)
                percent = metric.change_percent
                result.append(f"> | {emoji} | {metric.name} | {metric.current_value} | {metric.target_value} | {change:+.1f} ({percent:+.1f}%) |")
        result.append("\n")
        # Базовые рекомендации
        result.append("> [!example]- 💡 Базовые рекомендации")
        result.append("> | Сфера | Рекомендация |")
        result.append("> |:---:|:---|")
        for sphere_name in master_order:
            section = sections.get(sphere_name)
            emoji = section.emoji if section else ''
            rec = section.recommendation if section else None
            if not rec:
                result.append(f"> | {emoji} | Нет рекомендации |")
                continue
            if isinstance(rec, str):
                result.append(f"> | {emoji} | {rec} |")
            elif hasattr(rec, 'title') and getattr(rec, 'title'):
                result.append(f"> | {emoji} | {rec.title} |")
            else:
                result.append(f"> | {emoji} | {str(rec)} |")
        result.append("\n")
        # AI-рекомендации (только если нет ошибки)
        if not openai_error:
            ai_recs = sections.get('ai_recommendations')
            if ai_recs:
                result.append("")
                result.append("> [!example]- <span style='color:#b37feb'>🤖 AI рекомендации</span>")
                result.append("> | Сфера | AI-рекомендация | Описание | Шаги | Обоснование |")
                result.append("> |:---:|:---|:---|:---|:---|")
                for sphere_name in master_order:
                    emoji = normalizer.get_emoji(sphere_name)
                    rec = ai_recs.get(sphere_name)
                    if not rec:
                        result.append(f"> | {emoji} | Нет AI-рекомендации |  |  |  |")
                        continue
                    # Title
                    title = rec.title if hasattr(rec, 'title') and rec.title else (str(rec) if isinstance(rec, str) else '')
                    # Description
                    desc = rec.description if hasattr(rec, 'description') and rec.description else ''
                    # Steps
                    steps = ''
                    if hasattr(rec, 'action_steps') and rec.action_steps:
                        steps = '<br/>'.join(f"{i+1}. {s.description}" for i, s in enumerate(rec.action_steps))
                    # Evidence
                    evidence = ''
                    if hasattr(rec, 'evidence') and rec.evidence:
                        ev = rec.evidence
                        parts = []
                        if getattr(ev, 'data_points', None):
                            parts.append('Наблюдения: ' + '; '.join(ev.data_points))
                        if getattr(ev, 'correlations', None):
                            parts.append('Корреляции: ' + '; '.join(ev.correlations))
                        if getattr(ev, 'historical_success', None):
                            parts.append(f"Исторический успех: {ev.historical_success*100:.0f}%")
                        evidence = '<br/>'.join(parts)
                    result.append(f"> | {emoji} | {title} | {desc} | {steps} | {evidence} |")
        # Добавляем блок ошибки OpenAI, только если есть ошибка
        if openai_error:
            result.append("")  # пустая строка для разрыва callout
            result.append("> [!danger]- <span style='color:#ff7875'>❗ Ошибка теста OpenAI</span>")
            result.append("> | Тип    | Сообщение                |\n> |:------:|:-------------------------|\n> | OpenAI | " + str(openai_error).replace("\n", " ") + " |")
            result.append("---")

        return "\n".join(result) 