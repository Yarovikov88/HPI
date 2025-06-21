"""
Модуль для инжекции данных в дашборд HPI.
"""

import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, cast

import yaml

from src.ai_recommendations import HPIRecommendationEngine
from src.dashboard.generators.recommendations import Evidence, Recommendation
from src.dashboard.generators.sections import AIRecommendationsSection, SectionGenerator
from src.dashboard.normalizers.metrics import MetricNormalizer
from src.dashboard.normalizers.spheres import SphereNormalizer
from src.dashboard.parsers.history import HistoryParser
from src.dashboard.parsers.pro_data import ProDataParser

from .formatters import MarkdownFormatter
from .generators import RecommendationGenerator
from .parsers import HistoricalReport, ProData, QuestionsDatabaseParser

# Определяем пути через конфиг
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config.yaml",
)
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DB_PATH = os.path.join(PROJECT_ROOT, config["paths"]["database"])
REPORTS_FINAL_DIR = os.path.join(PROJECT_ROOT, config["paths"]["reports_final"])
REPORTS_DRAFT_DIR = os.path.join(PROJECT_ROOT, config["paths"]["reports_draft"])
MAIN_DASHBOARD_PATH = os.path.join(PROJECT_ROOT, config["paths"]["dashboard"])


class DashboardInjector:
    """Инжектор для обновления дашборда."""

    def __init__(self, version: str = "0.0.0"):
        """
        Инициализация инжектора.

        Args:
            version: Версия системы
        """
        self.version = version
        self.logger = logging.getLogger(__name__)

        # Инициализируем парсеры
        self.questions_parser = QuestionsDatabaseParser(DB_PATH)
        self.pro_parser = ProDataParser()
        self.history_parser = HistoryParser(REPORTS_FINAL_DIR)

        # Инициализируем генераторы
        self.section_generator = SectionGenerator()
        self.recommendation_generator = RecommendationGenerator()

        # Инициализируем форматтер
        self.formatter = MarkdownFormatter()

        # Инициализируем нормализаторы
        self.metric_normalizer = MetricNormalizer()
        self.sphere_normalizer = SphereNormalizer()

        # Инициализируем AI-движок для рекомендаций
        self.ai_engine = HPIRecommendationEngine()

    def _find_latest_draft(self) -> Optional[str]:
        """
        Находит последний черновик отчета (по самой поздней дате в имени файла).
        Returns:
            Путь к файлу черновика или None, если не найден
        """
        if not os.path.exists(REPORTS_DRAFT_DIR):
            self.logger.error(
                f"Директория с черновиками не найдена: {REPORTS_DRAFT_DIR}"
            )
            return None
        all_files = os.listdir(REPORTS_DRAFT_DIR)
        self.logger.info(f"Все файлы в папке reports_draft: {all_files}")
        drafts = []
        for filename in all_files:
            if filename.endswith("_draft.md"):
                parts = filename.split("_")
                if len(parts) >= 3:
                    date_str = parts[0] + "-" + parts[1] + "-" + parts[2]
                else:
                    date_str = filename.split("_")[0]
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    drafts.append((date, filename))
                except Exception as e:
                    self.logger.warning(
                        f"Файл не подходит под формат даты: {filename} ({e})"
                    )
        self.logger.info(
            f"Найдено файлов-кандидатов: {[f'{d[1]} ({d[0]})' for d in drafts]}"
        )
        if not drafts:
            self.logger.error("Черновики отчетов не найдены")
            return None
        latest_draft = max(drafts, key=lambda x: x[0])
        draft_path = os.path.join(REPORTS_DRAFT_DIR, latest_draft[1])
        self.logger.info(f"Выбран последний черновик: {draft_path}")
        return draft_path

    def _load_data(self) -> Tuple[ProData, List[HistoricalReport]]:
        """
        Загружает данные из черновика и исторических отчетов.

        Returns:
            Кортеж (pro_data, history)
        """
        # Находим последний черновик
        draft_path = self._find_latest_draft()
        if not draft_path:
            raise ValueError("Не удалось найти черновик отчета")

        # Читаем содержимое черновика
        with open(draft_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Парсим данные из черновика
        pro_data = self.pro_parser.parse(content)

        # Получаем исторические данные
        history = self.history_parser.get_history()

        return pro_data, history

    def _generate_recommendations(
        self, pro_data: ProData, history: List[HistoricalReport]
    ) -> Dict[str, Recommendation]:
        recommendations = {}
        for sphere_name, _ in pro_data.scores.items():
            reco = None
            if hasattr(self.ai_engine, "generate_recommendation"):
                try:
                    ai_reco = self.ai_engine.generate_recommendation(
                        sphere_name,
                        pro_data.scores.get(sphere_name, 0.0),
                        [h.scores.get(sphere_name, 0.0) for h in history],
                    )
                    if ai_reco is not None:
                        data = getattr(ai_reco, "data", None)
                        if isinstance(data, dict):
                            title = data.get("title", str(ai_reco))
                            description = data.get("description", "")
                        else:
                            title = (
                                getattr(data, "title", str(ai_reco))
                                if data
                                else str(ai_reco)
                            )
                            description = (
                                getattr(data, "description", "") if data else ""
                            )
                        reco = Recommendation(
                            sphere=sphere_name,
                            priority=int(getattr(ai_reco, "priority", 3)),
                            title=title,
                            description=description,
                            action_steps=[],
                            evidence=Evidence(
                                data_points=[], correlations=[], historical_success=0.0
                            ),
                            related_spheres=[],
                        )
                except Exception as e:
                    self.logger.error(
                        f"Ошибка при генерации AI-рекомендации для сферы {sphere_name}: {e}"
                    )
            if reco is None:
                basic_recs = cast(
                    List[str],
                    self.recommendation_generator.generate_basic(
                        {"sphere": sphere_name}
                    ),
                )
                if basic_recs:
                    first = basic_recs[0]
                    if ":" in first:
                        title, description = first.split(":", 1)
                        title = title.strip()
                        description = description.strip()
                    else:
                        title = first
                        description = first
                    reco = Recommendation(
                        sphere=sphere_name,
                        priority=3,
                        title=title,
                        description=description,
                        action_steps=[],
                        evidence=Evidence(
                            data_points=[], correlations=[], historical_success=0.0
                        ),
                        related_spheres=[],
                    )
            if reco:
                recommendations[sphere_name] = reco
        return recommendations

    def inject(self, save_draft: bool = False) -> str:
        """
        Обновляет дашборд, добавляя новые данные и рекомендации.

        Args:
            save_draft: Сохранять ли черновик дашборда

        Returns:
            Путь к сохраненному файлу
        """
        self.logger.info("Начинаю обновление дашборда...")
        try:
            # --- Новый алгоритм: работаем только с финальными отчетами ---
            final_history = self.history_parser.get_history()
            if not final_history:
                raise ValueError("Нет финальных отчетов для генерации дашборда")
            # Берём последний финальный отчет как основной
            current_report = final_history[-1]
            current_date = current_report.date
            # Для сравнения метрик — предпоследний финальный отчет (если есть)
            history = final_history
            # Парсим последний финальный отчет в ProData для AI рекомендаций
            with open(current_report.file_path, "r", encoding="utf-8") as f:
                current_content = f.read()
            pro_data = self.pro_parser.parse(
                current_content, scores=current_report.scores
            )
            # Генерируем секции по истории
            sections = self.section_generator.generate(
                history=history,
                recommendations=self._generate_recommendations(pro_data, history),
            )
            # AI рекомендации
            ai_recs = {}
            ai_error = None
            try:
                # Для каждой сферы пытаемся сгенерировать рекомендацию, собираем ошибки
                for sphere_name, _ in pro_data.scores.items():
                    try:
                        recs = self._generate_recommendations(pro_data, history).get(
                            sphere_name, None
                        )
                        if recs:
                            ai_recs[sphere_name] = recs
                    except Exception as e:
                        ai_error = str(e)
                        self.logger.error(
                            f"Ошибка AI для сферы {sphere_name}: {ai_error}"
                        )
            except Exception as e:
                ai_error = str(e)
                self.logger.error(f"Ошибка генерации AI-рекомендаций: {ai_error}")
            ai_section = None
            if ai_recs or ai_error:
                ai_section = AIRecommendationsSection(
                    recommendations=ai_recs, error=ai_error
                )
            # Формируем дашборд
            history_dicts = [asdict(r) for r in history]
            report_content = self.formatter.format_report(
                sections=sections,
                history=history_dicts,
                date=current_date,
                version=self.version,
            )
            if ai_section:
                # Добавляю AI секцию в конец отчёта
                report_content += "\n" + str(ai_section)
            # Сохраняем дашборд
            with open(MAIN_DASHBOARD_PATH, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.logger.info(f"Дашборд успешно сохранен: {MAIN_DASHBOARD_PATH}")
            return MAIN_DASHBOARD_PATH
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении дашборда: {e}")
            raise

    def _generate_custom_recommendations(
        self, pro_data: "ProData"
    ) -> Dict[str, Recommendation]:
        recommendations = {}
        for sphere_name, sphere_data in pro_data.scores.items():
            if (
                hasattr(sphere_data, "custom_recommendation")
                and sphere_data.custom_recommendation
            ):
                recommendations[sphere_name] = Recommendation(
                    sphere=sphere_name,
                    priority=3,
                    title="Пользовательская рекомендация",
                    description=sphere_data.custom_recommendation,
                    action_steps=[],
                    evidence=Evidence(
                        data_points=[], correlations=[], historical_success=0.0
                    ),
                    related_spheres=[],
                )
        return recommendations

    def _generate_basic_recommendations(
        self, pro_data: "ProData"
    ) -> Dict[str, Recommendation]:
        recommendations = {}
        for sphere_name in pro_data.scores.keys():
            recs = cast(
                List[str],
                self.recommendation_generator.generate_basic({"sphere": sphere_name}),
            )
            if recs:
                first = recs[0]
                if ":" in first:
                    title, description = first.split(":", 1)
                    title = title.strip()
                    description = description.strip()
                else:
                    title = first
                    description = first
                recommendations[sphere_name] = Recommendation(
                    sphere=sphere_name,
                    priority=3,
                    title=title,
                    description=description,
                    action_steps=[],
                    evidence=Evidence(
                        data_points=[], correlations=[], historical_success=0.0
                    ),
                    related_spheres=[],
                )
        return recommendations

    def _generate_ai_recommendations(
        self, pro_data: "ProData", history: List["HistoricalReport"]
    ) -> Tuple[Dict[str, Recommendation], Optional[str]]:
        recommendations = {}
        error_message = None
        for sphere_name in pro_data.scores.keys():
            try:
                reco = self.ai_engine.generate_recommendation(
                    sphere_name,
                    pro_data.scores.get(sphere_name, 0.0),
                    [h.scores.get(sphere_name, 0.0) for h in history],
                )
                if reco:
                    # Привожу к Recommendation из generators.recommendations
                    recommendations[sphere_name] = Recommendation(
                        sphere=sphere_name,
                        priority=int(getattr(reco, "priority", 3)),
                        title=getattr(reco, "title", str(reco)),
                        description=getattr(reco, "description", str(reco)),
                        action_steps=[],
                        evidence=Evidence(
                            data_points=[], correlations=[], historical_success=0.0
                        ),
                        related_spheres=[],
                    )
            except Exception as e:
                error_message = str(e)
                self.logger.error(f"Ошибка AI для сферы {sphere_name}: {error_message}")
        return recommendations, error_message
