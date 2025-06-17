"""
Модуль для инжекции данных в дашборд HPI.
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .parsers import (
    ProDataParser,
    QuestionsDatabaseParser,
    HistoryParser,
    ProData,
    HistoricalReport
)
from .generators import (
    RecommendationGenerator,
    SectionGenerator,
    Recommendation,
    SphereSection
)
from .formatters import MarkdownFormatter
from .ai import AIRecommendationEngine
from .normalizers import MetricNormalizer, SphereNormalizer

# Определяем пути
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'questions.md')
REPORTS_FINAL_DIR = os.path.join(PROJECT_ROOT, 'reports_final')
REPORTS_DRAFT_DIR = os.path.join(PROJECT_ROOT, 'reports_draft')
MAIN_DASHBOARD_PATH = os.path.join(PROJECT_ROOT, 'interfaces', 'dashboard.md')

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
        self.ai_engine = AIRecommendationEngine()

    def _find_latest_draft(self) -> Optional[str]:
        """
        Находит последний черновик отчета (по самой поздней дате в имени файла).
        Returns:
            Путь к файлу черновика или None, если не найден
        """
        if not os.path.exists(REPORTS_DRAFT_DIR):
            self.logger.error(f"Директория с черновиками не найдена: {REPORTS_DRAFT_DIR}")
            return None
        all_files = os.listdir(REPORTS_DRAFT_DIR)
        self.logger.info(f"Все файлы в папке reports_draft: {all_files}")
        drafts = []
        for filename in all_files:
            if filename.endswith('_draft.md'):
                parts = filename.split('_')
                if len(parts) >= 3:
                    date_str = parts[0] + '-' + parts[1] + '-' + parts[2]
                else:
                    date_str = filename.split('_')[0]
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    drafts.append((date, filename))
                except Exception as e:
                    self.logger.warning(f"Файл не подходит под формат даты: {filename} ({e})")
        self.logger.info(f"Найдено файлов-кандидатов: {[f'{d[1]} ({d[0]})' for d in drafts]}")
        if not drafts:
            self.logger.error("Черновики отчетов не найдены")
            return None
        latest_draft = max(drafts, key=lambda x: x[0])
        draft_path = os.path.join(REPORTS_DRAFT_DIR, latest_draft[1])
        self.logger.info(f"Выбран последний черновик: {draft_path}")
        return draft_path

    def _load_data(self) -> tuple[ProData, List[HistoricalReport]]:
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
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Парсим данные из черновика
        pro_data = self.pro_parser.parse(content)
        
        # Получаем исторические данные
        history = self.history_parser.get_history()
        
        return pro_data, history

    def _generate_recommendations(
        self,
        pro_data: ProData,
        history: List[HistoricalReport]
    ) -> Dict[str, List[Recommendation]]:
        """
        Генерирует рекомендации для каждой сферы.
        
        Args:
            pro_data: Данные текущего отчета
            history: Список исторических отчетов
            
        Returns:
            Словарь {сфера: список рекомендаций}
        """
        recommendations = {}
        
        # Для каждой сферы генерируем рекомендации
        for sphere, score in pro_data.scores.items():
            sphere_recommendations = []
            # Если у AI движка есть generate_recommendation, вызываем его для каждой сферы
            if hasattr(self.ai_engine, 'generate_recommendation'):
                try:
                    rec = self.ai_engine.generate_recommendation(
                        sphere=sphere,
                        pro_data=pro_data,
                        history=history
                    )
                    if rec:
                        # Оборачиваем строку в Recommendation
                        if isinstance(rec, str):
                            rec = Recommendation(
                                sphere=sphere,
                                priority=1,
                                title=rec,
                                description="",
                                action_steps=[],
                                evidence=Evidence(data_points=[], correlations=[], historical_success=0.0),
                                related_spheres=[]
                            )
                        sphere_recommendations = [rec]
                    else:
                        # generate_basic возвращает список строк, оборачиваем первую строку в Recommendation
                        basic_recs = self.recommendation_generator.generate_basic({
                            'sphere': sphere,
                            'current_score': score,
                            'pro_data': pro_data,
                            'history': history
                        })
                        if isinstance(basic_recs, list) and basic_recs:
                            sphere_recommendations = [Recommendation(
                                sphere=sphere,
                                priority=3,
                                title=basic_recs[0].split(':')[0] if ':' in basic_recs[0] else basic_recs[0],
                                description=basic_recs[0].split(':', 1)[1].strip() if ':' in basic_recs[0] else basic_recs[0],
                                action_steps=[],
                                evidence=None,
                                related_spheres=[]
                            )]
                        else:
                            sphere_recommendations = []
                except Exception as e:
                    self.logger.error(f"Ошибка при генерации AI-рекомендации для сферы {sphere}: {e}")
                    basic_recs = self.recommendation_generator.generate_basic({
                        'sphere': sphere,
                        'current_score': score,
                        'pro_data': pro_data,
                        'history': history
                    })
                    if isinstance(basic_recs, list) and basic_recs:
                        sphere_recommendations = [Recommendation(
                            sphere=sphere,
                            priority=3,
                            title=basic_recs[0].split(':')[0] if ':' in basic_recs[0] else basic_recs[0],
                            description=basic_recs[0].split(':', 1)[1].strip() if ':' in basic_recs[0] else basic_recs[0],
                            action_steps=[],
                            evidence=None,
                            related_spheres=[]
                        )]
                    else:
                        sphere_recommendations = []
            else:
                # Fallback: только базовые рекомендации
                basic_recs = self.recommendation_generator.generate_basic({
                    'sphere': sphere,
                    'current_score': score,
                    'pro_data': pro_data,
                    'history': history
                })
                if isinstance(basic_recs, list) and basic_recs:
                    sphere_recommendations = [Recommendation(
                        sphere=sphere,
                        priority=3,
                        title=basic_recs[0].split(':')[0] if ':' in basic_recs[0] else basic_recs[0],
                        description=basic_recs[0].split(':', 1)[1].strip() if ':' in basic_recs[0] else basic_recs[0],
                        action_steps=[],
                        evidence=None,
                        related_spheres=[]
                    )]
                else:
                    sphere_recommendations = []
            recommendations[sphere] = sphere_recommendations
            
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
        ai_error = None
        ai_recs = {}
        try:
            # Получаем исторические данные только из финальных отчетов
            history = self.history_parser.get_history()
            if len(history) < 1:
                raise ValueError("Недостаточно финальных отчетов для генерации дашборда")
            current_report = history[-1]
            # Парсим последний финальный отчет в ProData для AI рекомендаций
            with open(current_report.file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            pro_data = self.pro_parser.parse(current_content)
            # Генерируем секции только по двум последним финальным отчетам
            sections = self.section_generator.generate(
                history=history,
                recommendations=self._generate_recommendations(pro_data, history)
            )
            # Добавляю секцию ai_recommendations для форматтера
            ai_recs = self._generate_recommendations(pro_data, history)
            if ai_recs:
                # Кладём в секцию не список, а сам Recommendation (или None)
                sections['ai_recommendations'] = {sphere: recs[0] if recs else None for sphere, recs in ai_recs.items()}
            # DEBUG: выводим структуру sections в лог и в markdown
            self.logger.info(f"SECTIONS DEBUG: {{k: type(v) for k, v in sections.items()}}: " + str({k: type(v) for k, v in sections.items()}))
            sections['debug_sections'] = {k: str(type(v)) for k, v in sections.items()}
            # Преобразуем историю в формат для дашборда
            history_data = []
            for report in history:
                history_data.append({
                    'date': report.date.strftime('%Y-%m-%d'),
                    'hpi': report.hpi,
                    'scores': report.scores
                })
            # Формируем дашборд
            dashboard_content = self.formatter.format_dashboard(
                sections=sections,
                history=history_data,
                date=history[-1].date,
                version=self.version
            )
            # Сохраняем дашборд
            with open(MAIN_DASHBOARD_PATH, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            self.logger.info(f"Дашборд успешно сохранен: {MAIN_DASHBOARD_PATH}")
            return MAIN_DASHBOARD_PATH
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении дашборда: {e}")
            raise 