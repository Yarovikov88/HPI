import sys
import os
import traceback
from datetime import datetime
import logging

# Добавляем корень проекта в sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, url_for

# --- Безопасные импорты из проекта ---
try:
    from src.calculator import find_latest_draft, process_hpi_report
    from src.config import SPHERE_CONFIG
    from src.radar import create_radar_chart
    from src.trend import create_trend_chart
    from src.dashboard.injector import DashboardInjector
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR_MESSAGE = str(e)
    logging.error(f"Ошибка импорта в routes.py: {e}", exc_info=True)
# --- Конец безопасных импортов ---

# --- Модели данных для шаблона ---
class MetricChange:
    """Класс для передачи данных о метриках в шаблон."""
    def __init__(self, metric, change_value=None):
        self.metric = metric
        self.change_value = change_value


# --- Константы ---
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "reports_draft")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports_final")

# --- Flask App ---
app = Flask(__name__, static_folder='static', template_folder='templates')


def get_metrics_with_change(pro_data, history_metrics):
    """Сравнивает текущие метрики с историческими данными."""
    metrics_with_change = []
    if not pro_data or not pro_data.metrics:
        return metrics_with_change

    sphere_normalizer = SphereNormalizer()
    
    for metric in pro_data.metrics:
        previous_value = None
        normalized_sphere = sphere_normalizer.normalize(metric.sphere)

        if metric.normalized_name in history_metrics:
            for prev_metric in history_metrics[metric.normalized_name]:
                if prev_metric.get('sphere') == normalized_sphere:
                    previous_value = prev_metric.get('value')
                    break
        
        change_value = None
        if previous_value is not None and metric.current_value is not None:
            change_value = metric.current_value - previous_value

        metrics_with_change.append(MetricChange(
            metric=metric,
            change_value=change_value
        ))
    return metrics_with_change


@app.route('/')
def index():
    """Главная страница веб-приложения."""
    context = {
        'scores': {},
        'pro_data': None,
        'sections': {},
        'radar_chart_url': None,
        'trend_chart_url': None,
        'error_message': None,
        'sphere_config': SPHERE_CONFIG if IMPORTS_OK else [],
        'sphere_name_to_emoji': {s['name']: s['emoji'] for s in SPHERE_CONFIG} if IMPORTS_OK else {},
        'metrics_with_change': [],
        'data': None
    }

    if not IMPORTS_OK:
        context['error_message'] = f"Критическая ошибка импорта: {IMPORT_ERROR_MESSAGE}."
        return render_template('index.html', **context)

    try:
        # 1. Найти последний черновик
        latest_draft_path = find_latest_draft()
        if not latest_draft_path:
            context['error_message'] = "Не найден ни один черновик в папке 'reports_draft'."
            return render_template('index.html', **context)

        # 2. Рассчитать ПРАВИЛЬНЫЕ баллы по сферам на основе опросника
        scores = process_hpi_report(latest_draft_path)
        if not scores:
             context['error_message'] = "Не удалось рассчитать баллы по сферам. Проверьте структуру черновика."
             return render_template('index.html', **context)
        context['scores'] = scores

        # 3. Использовать DashboardInjector для получения всех данных
        injector = DashboardInjector()
        
        # 4. Сгенерировать готовые секции и данные для дашборда
        template_data = injector.get_dashboard_data()
        
        # 5. Проверить, что данные были сгенерированы
        if not template_data or not template_data.get('spheres'):
            context['error_message'] = "Не удалось сгенерировать данные для дашборда. Убедитесь, что в папке 'reports_final' есть хотя бы два отчета и что они имеют корректную структуру."
            # Все равно попробуем сгенерировать графики, если это возможно
            try:
                _, history = injector._load_data()
                if history and len(history) >= 2:
                    hpi_trend = [{'date': report.date, 'hpi': report.hpi} for report in history]
                    trend_filename = "trend_latest.png"
                    trend_save_path = os.path.join(app.static_folder, 'images', trend_filename)
                    dates = [item['date'] for item in hpi_trend]
                    values = [item['hpi'] for item in hpi_trend]
                    if create_trend_chart(dates, values, trend_save_path):
                        context['trend_chart_url'] = url_for('static', filename=f'images/{trend_filename}', v=datetime.now().timestamp())
            except Exception:
                # Игнорируем ошибки графиков, если основная проблема в данных
                pass
            return render_template('index.html', **context)

        context['data'] = template_data

        # 6. Сгенерировать радар-чарт на основе полученных данных
        # Создаем словарь для сопоставления нормализованного имени и номера сферы
        sphere_name_to_id = {s['normalized']: str(s['number']) for s in SPHERE_CONFIG}
        scores_for_radar = {
            sphere_name_to_id[s['id']]: s['current_score']
            for s in template_data['spheres']
            if s['id'] in sphere_name_to_id and s['current_score'] is not None
        }
        
        if scores_for_radar:
            radar_filename = "radar_latest.png"
            radar_save_path = os.path.join(app.static_folder, 'images', radar_filename)
            create_radar_chart(scores_for_radar, radar_save_path)

        # 7. Сгенерировать график тренда
        try:
            _, history = injector._load_data()
            hpi_trend = [{'date': report.date, 'hpi': report.hpi} for report in history]
            if hpi_trend and len(hpi_trend) >= 2:
                trend_filename = "trend_latest.png"
                trend_save_path = os.path.join(app.static_folder, 'images', trend_filename)
                dates = [item['date'] for item in hpi_trend]
                values = [item['hpi'] for item in hpi_trend]
                create_trend_chart(dates, values, trend_save_path)
        except Exception as e:
            # Тренд менее важен, логируем ошибку, но не падаем
            logging.warning(f"Не удалось сгенерировать график тренда: {e}")


    except Exception as e:
        context['error_message'] = f"Критическая ошибка при загрузке данных: {e}"
        traceback.print_exc()

    return render_template('index.html', **context)


if __name__ == '__main__':
    # Настройка базового логгера для вывода в консоль
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
    app.run(debug=True, host='0.0.0.0', port=5001) 