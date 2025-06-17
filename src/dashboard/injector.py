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
            
            # Если у AI движка нет нужного метода — всегда используем базовый генератор
            if not hasattr(self.ai_engine, 'get_sphere_context'):
                context = None  # или можно собрать минимальный контекст, если нужно
                sphere_recommendations = self.recommendation_generator.generate_basic({
                    'sphere': sphere,
                    'current_score': score,
                    'pro_data': pro_data,
                    'history': history
                })
            else:
                try:
                    context = self.ai_engine.get_sphere_context(
                        sphere=sphere,
                        current_score=score,
                        pro_data=pro_data,
                        history=history
                    )
                    if os.getenv("OPENAI_API_KEY"):
                        sphere_recommendations = self.ai_engine.generate_recommendations(context)
                    else:
                        sphere_recommendations = self.recommendation_generator.generate_basic(context)
                except Exception as e:
                    self.logger.error(f"Ошибка при генерации рекомендаций для сферы {sphere}: {e}")
                    sphere_recommendations = self.recommendation_generator.generate_basic(context)
                
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
            # Загружаем данные
            pro_data, history = self._load_data()
            # Получаем путь к последнему черновику и дату из имени файла
            draft_path = self._find_latest_draft()
            draft_date = None
            if draft_path:
                draft_filename = os.path.basename(draft_path)
                try:
                    draft_date_str = draft_filename.split('_')[0]
                    draft_date = datetime.strptime(draft_date_str, '%Y-%m-%d')
                except Exception as e:
                    self.logger.warning(f"Не удалось извлечь дату из имени черновика: {draft_filename} ({e})")
            # Преобразуем историю в формат для дашборда
            history_data = []
            for report in history:
                history_data.append({
                    'date': report.date.strftime('%Y-%m-%d'),
                    'hpi': report.hpi,
                    'scores': report.scores
                })
            # Генерируем рекомендации
            recommendations = self._generate_recommendations(pro_data, history)
            # Попытка сгенерировать AI-рекомендации
            try:
                if os.getenv("OPENAI_API_KEY"):
                    from .ai import AIRecommendationEngine
                    ai_engine = AIRecommendationEngine()
                    for sphere in pro_data.scores.keys():
                        self.logger.info(f"[AI] Генерация AI-рекомендации для сферы: {sphere}")
                        rec = ai_engine.generate_recommendation(sphere, pro_data, history)
                        self.logger.info(f"[AI] Тип rec для '{sphere}': {type(rec)}; repr: {repr(rec)}")
                        if rec is not None:
                            self.logger.info(f"[AI] Получена AI-рекомендация для '{sphere}': {getattr(rec, 'description', str(rec))}")
                            ai_recs[sphere] = rec  # Сохраняем весь объект Recommendation
                        else:
                            self.logger.warning(f"[AI] Не удалось сгенерировать AI-рекомендацию для '{sphere}'")
                            ai_recs[sphere] = None
                    self.logger.info(f"[AI] Итоговый ai_recs: {repr(ai_recs)}")
                else:
                    ai_error = "OPENAI_API_KEY не найден. AI-рекомендации недоступны."
            except Exception as e:
                ai_error = str(e)
                self.logger.error(f"Ошибка генерации AI-рекомендаций: {e}", exc_info=True)
            # Генерируем секции для каждой сферы
            sections = self.section_generator.generate(
                pro_data,
                history,
                recommendations
            )
            # Добавляем секцию AI-рекомендаций (или ошибку)
            if ai_error:
                sections['ai_recommendations'] = {'Ошибка': ai_error}
            elif ai_recs:
                sections['ai_recommendations'] = ai_recs
            else:
                sections['ai_recommendations'] = {'Ошибка': 'AI-рекомендации не были сгенерированы. Проверьте настройки или попробуйте позже.'}
            self.logger.info(f"Сгенерировано секций: {len(sections)}")
            if sections:
                first_sphere = next(iter(sections))
                self.logger.info(f"Пример секции для '{first_sphere}': {sections[first_sphere]}")
            for k, v in sections.items():
                self.logger.info(f"Секция '{k}': {str(v)[:200]}")
            # Форматируем дашборд
            dashboard_content = self.formatter.format_dashboard(
                sections=sections,
                history=history_data,
                date=draft_date if draft_date else datetime.now(),
                version=self.version
            )
            self.logger.info(f"Первые 500 символов dashboard_content:\n{dashboard_content[:500]}")
            if save_draft:
                # Сохраняем как черновик
                date_str = draft_date.strftime('%Y-%m-%d') if draft_date else datetime.now().strftime('%Y-%m-%d')
                filename = f"{date_str}_dashboard_draft.md"
                save_dir = REPORTS_DRAFT_DIR
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, filename)
            else:
                # Обновляем основной дашборд
                file_path = MAIN_DASHBOARD_PATH
                # Создаем директорию, если её нет
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Сохраняем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            self.logger.info(f"Дашборд успешно сохранен: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении дашборда: {e}")
            raise 