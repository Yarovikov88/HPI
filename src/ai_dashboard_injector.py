"""
HPI AI Dashboard Injector
Генерирует файл AI_Recommendations.md с актуальными рекомендациями для дашборда HPI.
"""
import locale
import os
import re
from datetime import datetime
from ai_recommendations import HPIRecommendationEngine
import random
import sys
from typing import Dict, List
import logging
from trend import generate_trend_chart
import json

# --- Принудительное использование UTF-8 ---
try:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except locale.Error:
    print("Warning: Could not set locale to C.UTF-8. Emoji support might be limited.")
# --- Конец принудительного использования UTF-8 ---

# --- КОНФИГУРАЦИЯ ---
# Абсолютные пути от корня проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(PROJECT_ROOT, 'reports_draft')
INTERFACES_DIR = os.path.join(PROJECT_ROOT, 'interfaces')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
REPORTS_FINAL_DIR = os.path.join(PROJECT_ROOT, 'reports_final')

# Конфигурация сфер, чтобы гарантировать порядок и наличие всех данных
SPHERES_CONFIG = [
    {"key": "Отношения с любимыми", "emoji": "💖"},
    {"key": "Отношения с родными", "emoji": "🏡"},
    {"key": "Друзья", "emoji": "🤝"},
    {"key": "Карьера", "emoji": "💼"},
    {"key": "Физическое здоровье", "emoji": "♂️"},
    {"key": "Ментальное здоровье", "emoji": "🧠"},
    {"key": "Хобби и увлечения", "emoji": "🎨"},
    {"key": "Благосостояние", "emoji": "💰"}
]

def parse_questions_database() -> Dict[str, List[str]]:
    """
    Парсит файл questions.md и извлекает все стандартные метрики для каждой сферы.
    Возвращает словарь, где ключ - название сферы, а значение - список названий метрик.
    """
    db_path = os.path.join(PROJECT_ROOT, 'database', 'questions.md')
    if not os.path.exists(db_path):
        logging.error(f"Файл базы данных вопросов не найден: {db_path}")
        return {}

    with open(db_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sphere_metrics = {}
    
    # Регулярное выражение для поиска JSON-блоков для каждой сферы
    # Ищет заголовок типа "## 💖 Отношения с любимыми" и следующий за ним блок ```json ... ```
    pattern = re.compile(r"##\s*(?P<emoji>[\U0001F000-\U0001FA95\s\S]+?)\s*(?P<name>.*?)\n```json\n([\s\S]+?)\n```", re.DOTALL)

    matches = pattern.finditer(content)
    
    for match in matches:
        sphere_name = match.group('name').strip()
        json_content = match.group(3)

        try:
            data = json.loads(json_content)
            for item in data:
                if item.get("category") == "metrics" and "metrics" in item:
                    # Собираем имена всех метрик для данной сферы
                    metric_names = [m.get("name") for m in item["metrics"] if m.get("name")]
                    if sphere_name in [s['key'] for s in SPHERES_CONFIG]:
                        sphere_metrics[sphere_name] = metric_names
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка декодирования JSON для сферы '{sphere_name}': {e}")
            continue
            
    logging.info(f"Из базы данных загружены стандартные метрики для {len(sphere_metrics)} сфер.")
    return sphere_metrics

# --- УТИЛИТЫ ---

def get_score_emoji(score: float, is_hpi: bool = False) -> str:
    """Конвертирует оценку в emoji-индикатор."""
    if is_hpi:
        if score >= 80: return "🟢"
        if score >= 60: return "🔵"
        if score >= 40: return "🟡"
        return "🔴"
    else:
        if score >= 8.0: return "🟢"
        if score >= 6.0: return "🔵"
        if score >= 4.0: return "🟡"
        return "🔴"

def collect_reports_history() -> List[Dict]:
    """
    Собирает историю HPI и оценок по сферам из всех финальных отчетов.
    Возвращает список словарей, каждый из которых представляет один отчет.
    """
    history = []
    if not os.path.exists(REPORTS_FINAL_DIR):
        logging.error(f"Папка с финальными отчетами не найдена: {REPORTS_FINAL_DIR}")
        return []

    report_files = [f for f in os.listdir(REPORTS_FINAL_DIR) if f.endswith("_report.md")]
    logging.info(f"Найдено {len(report_files)} отчетов для сбора истории.")

    for filename in report_files:
        try:
            date_str = filename.split('_')[0]
            report_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            filepath = os.path.join(REPORTS_FINAL_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            report_data = {'date': report_date, 'scores': {}}

            hpi_match = re.search(r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*([\d\.]+)\*\*\s*\|', content)
            if hpi_match:
                report_data['hpi'] = float(hpi_match.group(1))
            
            for sphere in SPHERES_CONFIG:
                pattern = rf"\| {re.escape(sphere['key'])} \| ([\d\.]+) \|"
                match = re.search(pattern, content)
                if match:
                    report_data['scores'][sphere['key']] = float(match.group(1))

            if 'hpi' in report_data:
                history.append(report_data)
            else:
                logging.warning(f"Не удалось найти HPI в отчете: {filename}")
        except Exception as e:
            logging.error(f"Ошибка при обработке отчета {filename} для истории: {e}")
            continue
    
    history.sort(key=lambda x: x['date'])
    logging.info(f"Собрано {len(history)} записей в истории.")
    return history

def generate_dummy_recommendations(pro_data: Dict) -> Dict[str, str]:
    """
    Генерирует 'фальшивые' AI-рекомендации на основе PRO-данных.
    Это временная заглушка до реализации полноценного AI-модуля.
    """
    recommendations = {}
    
    # Пример простой логики: ищем ключевые слова в проблемах и целях
    problems = pro_data.get('Мои проблемы', {})
    goals = pro_data.get('Мои цели', {})

    for sphere, problem in problems.items():
        if "выгорание" in problem.lower() or "апатия" in problem.lower():
            recommendations[sphere] = "Обнаружены признаки выгорания. Рассмотрите возможность взять короткий отпуск или снизить нагрузку."
        elif "редко" in problem.lower():
             recommendations[sphere] = f"Вы указали, что редко видитесь/созваниваетесь. Попробуйте запланировать регулярную встречу или звонок."

    for sphere, goal in goals.items():
        if "курс" in goal.lower() or "обучение" in goal.lower():
            recommendations[sphere] = f"Отличная цель! Для прохождения курса по '{goal}' создайте учебный план и выделите время в календаре."
        elif "найти" in goal.lower() and "работу" in goal.lower():
             recommendations[sphere] = "Для поиска новой работы обновите резюме и начните ежедневно просматривать вакансии на 1-2 площадках."

    logging.info(f"Сгенерированы dummy-рекомендации: {recommendations}")
    return recommendations

def find_latest_draft() -> str | None:
    """Находит последний по дате изменения черновик в папке."""
    logging.info("Поиск последнего черновика...")
    if not os.path.exists(DRAFTS_DIR):
        logging.error(f"Папка с черновиками не найдена: {DRAFTS_DIR}")
        return None
    
    drafts = [os.path.join(DRAFTS_DIR, f) for f in os.listdir(DRAFTS_DIR) if f.endswith("_draft.md")]
    if not drafts:
        logging.error("Черновики не найдены в директории: %s", DRAFTS_DIR)
        return None
    
    logging.info(f"Найдено {len(drafts)} черновиков. Выбираем последний...")
    latest_draft = max(drafts, key=os.path.getmtime)
    logging.info(f"Выбран черновик: {latest_draft}")
    return latest_draft

def parse_pro_data(md_content: str) -> Dict[str, Dict[str, str]]:
    """
    Извлекает все PRO-данные из черновика.
    Возвращает словарь, где ключ - название секции.
    Для обычных секций значение - словарь {сфера: ответ}.
    Для 'Мои метрики' значение - список словарей [{'sphere': сфера, 'metric': метрика, ...}].
    """
    logging.info("Начало парсинга PRO-секций из черновика.")
    pro_sections = ['Мои проблемы', 'Мои цели', 'Мои блокеры', 'Мои достижения', 'Мои метрики']
    all_pro_data = {}

    for section_title in pro_sections:
        logging.debug(f"Поиск секции: '{section_title}'")
        lines = md_content.split('\n')
        
        for i, line in enumerate(lines):
            if section_title in line and line.strip().startswith('###'):
                logging.debug(f"Найдена строка с заголовком секции: '{line.strip()}'")
                
                # Специальная обработка для 'Мои метрики'
                if section_title == 'Мои метрики':
                    metrics_data = []
                    for table_line in lines[i+1:]:
                        if table_line.strip().startswith('###'): break
                        if not table_line.strip().startswith('|'): continue
                        
                        parts = [p.strip() for p in table_line.split('|') if p.strip()]
                        if len(parts) >= 4 and '---' not in parts[0]:
                            sphere_candidate = parts[0]
                            # Ищем, к какой сфере относится строка
                            for config in SPHERES_CONFIG:
                                if config['key'] in sphere_candidate or config['emoji'] in sphere_candidate:
                                    metrics_data.append({
                                        'sphere': config['key'],
                                        'metric': parts[1],
                                        'current': parts[2],
                                        'target': parts[3]
                                    })
                                    # Не прерываем, чтобы найти все метрики для всех сфер
                    all_pro_data[section_title] = metrics_data
                    logging.info(f"Для секции '{section_title}' извлечены метрики: {metrics_data}")
                else:
                    # Стандартная обработка для остальных секций
                    section_data = {}
                    current_sphere_key = None
                    for table_line in lines[i+1:]:
                        if table_line.strip().startswith('###'): break
                        if not table_line.strip().startswith('|'): continue

                        parts = [p.strip() for p in table_line.split('|') if p.strip()]
                        if len(parts) >= 2:
                            sphere_candidate = parts[0]
                            answer = parts[1]
                            final_answer = answer if answer and answer.lower() not in ['нет', ''] else "Нет данных"

                            # Проверяем, новая ли это сфера
                            found_sphere = False
                            for config in SPHERES_CONFIG:
                                if config['key'] in sphere_candidate or config['emoji'] in sphere_candidate:
                                    current_sphere_key = config['key']
                                    section_data[current_sphere_key] = final_answer
                                    found_sphere = True
                                    break # Нашли сферу, выходим из внутреннего цикла
                            
                            # Если сфера не найдена в первой колонке, используем предыдущую
                            # (для многострочных ответов в одной сфере)
                            if not found_sphere and current_sphere_key and section_data.get(current_sphere_key) != "Нет данных":
                               section_data[current_sphere_key] += f"\\n{final_answer}"

                    all_pro_data[section_title] = section_data
                    logging.info(f"Для секции '{section_title}' извлечены следующие данные: {section_data}")
                
                break # Переходим к следующей PRO-секции
    
    logging.info(f"Парсинг PRO-секций завершен.")
    return all_pro_data

def run_injector():
    """
    Главная функция: находит черновик, парсит его и полностью пересоздает дашборд.
    """
    logging.info("--- 🚀 Запуск AI Dashboard Injector (метод регенерации) ---")

    latest_draft = find_latest_draft()
    if not latest_draft:
        logging.critical("Работа прервана: не найден актуальный черновик.")
        return

    logging.info(f"Чтение содержимого из файла: {latest_draft}")
    try:
        with open(latest_draft, 'r', encoding='utf-8') as f:
            draft_content = f.read()
    except FileNotFoundError:
        logging.critical(f"Файл черновика не найден по пути: {latest_draft}")
        return
    except Exception as e:
        logging.critical(f"Не удалось прочитать файл черновика: {e}", exc_info=True)
        return

    pro_data = parse_pro_data(draft_content)
    
    # Загружаем стандартные метрики из БД
    standard_metrics = parse_questions_database()

    reports_history = collect_reports_history()
    
    # --- Генерация графика тренда ---
    trend_chart_path = generate_trend_chart(reports_history)
    if not trend_chart_path:
        trend_chart_path = "hpi/docs/images/trend_placeholder.png"
        logging.warning("Не удалось создать график тренда, будет использована заглушка.")
        
    # --- Определение путей к последним графикам ---
    latest_report_date_str = ""
    if reports_history:
        latest_report_date_str = reports_history[-1]['date'].strftime('%Y-%m-%d')
    
    radar_chart_path = f"reports_final/images/{latest_report_date_str}_radar.png" if latest_report_date_str else "hpi/docs/images/radar_placeholder.png"

    # --- Таблица истории HPI ---
    hpi_history_rows = []
    if reports_history:
        for report in sorted(reports_history, key=lambda x: x['date'], reverse=True):
            hpi = report.get('hpi', 0.0)
            emoji = get_score_emoji(hpi, is_hpi=True)
            hpi_history_rows.append(f"| {report['date'].strftime('%Y-%m-%d')} | {hpi:.1f} | {emoji} |")
    
    # --- Таблица истории по сферам ---
    spheres_history_rows = []
    if reports_history:
        for report in sorted(reports_history, key=lambda x: x['date'], reverse=True):
            row = f"| {report['date'].strftime('%Y-%m-%d')} "
            for sphere_config in SPHERES_CONFIG:
                score = report.get('scores', {}).get(sphere_config['key'], '-')
                row += f"| {score} "
            row += "|"
            spheres_history_rows.append(row)

    hpi_history_table = "\n".join(hpi_history_rows) if hpi_history_rows else "| Нет данных для отображения. | | |"
    
    spheres_header = "| Дата | " + " | ".join([s['emoji'] for s in SPHERES_CONFIG]) + " |\n|:---|:" + "---:|:" * (len(SPHERES_CONFIG)-1) + "---:|"
    spheres_history_table = spheres_header + "\n" + "\n".join(spheres_history_rows) if spheres_history_rows else "| Нет данных |" + " |" * len(SPHERES_CONFIG)
    
    # --- AI Рекомендации ---
    recommendations = generate_dummy_recommendations(pro_data)
    
    # --- Сборка дашборда ---
    dashboard_content = []

    # Заголовок
    hpi_score = reports_history[-1]['hpi'] if reports_history else 0
    hpi_emoji = get_score_emoji(hpi_score, is_hpi=True)
    dashboard_content.append(f"# HPI Дашборд")
    dashboard_content.append(f"🚀 **Ваш текущий Human Performance Index:** {hpi_score} {hpi_emoji}")

    # --- Динамика HPI (график + таблица) ---
    dinamika_content = []
    dinamika_content.append(f"![Динамика HPI](../../{trend_chart_path.replace(os.path.sep, '/')})")
    if hpi_history_table:
        dinamika_content.append("\n" + hpi_history_table)
    
    # Форматируем контент для callout
    dinamika_formatted = "\n> ".join("\n".join(dinamika_content).split("\n"))
    dashboard_content.append(f'\n> [!note]- 📈 Динамика HPI\n> {dinamika_formatted}')

    # --- Баланс по сферам (график + таблица) ---
    balans_content = []
    balans_content.append(f"![Баланс по сферам](../../{radar_chart_path.replace(os.path.sep, '/')})")
    if spheres_history_table:
        balans_content.append("\n" + spheres_history_table)

    # Форматируем контент для callout
    balans_formatted = "\n> ".join("\n".join(balans_content).split("\n"))
    dashboard_content.append(f'\n> [!note]- ⚖️ Баланс по сферам\n> {balans_formatted}')

    dashboard_content.append("\n---\n")
    dashboard_content.append("## PRO-разделы")

    # --- Генерация PRO-секций с другим стилем ---
    pro_section_callout_type = "example" # Используем другой тип для визуального отличия

    # Мои проблемы
    if pro_data.get('Мои проблемы'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📝🔴 Мои проблемы')
        dashboard_content.append("> | Сфера | Проблема |")
        dashboard_content.append("> |:---|:---|")
        for sphere in SPHERES_CONFIG:
            problem = pro_data.get('Мои проблемы', {}).get(sphere['key'], 'Нет данных')
            if problem != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} {sphere['key']} | {problem} |")

    # Мои цели
    if pro_data.get('Мои цели'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📝🎯 Мои цели')
        dashboard_content.append("> | Сфера | Цель |")
        dashboard_content.append("> |:---|:---|")
        for sphere in SPHERES_CONFIG:
            goal = pro_data.get('Мои цели', {}).get(sphere['key'], 'Нет данных')
            if goal != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} {sphere['key']} | {goal} |")

    # Мои блокеры
    if pro_data.get('Мои блокеры'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📝🚧 Мои блокеры')
        dashboard_content.append("> | Сфера | Блокер |")
        dashboard_content.append("> |:---|:---|")
        for sphere in SPHERES_CONFIG:
            blocker = pro_data.get('Мои блокеры', {}).get(sphere['key'], 'Нет данных')
            if blocker != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} {sphere['key']} | {blocker} |")
    
    # Мои достижения
    if pro_data.get('Мои достижения'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📝🏆 Мои достижения')
        dashboard_content.append("> | Сфера | Достижение |")
        dashboard_content.append("> |:---|:---|")
        for sphere in SPHERES_CONFIG:
            achievement = pro_data.get('Мои достижения', {}).get(sphere['key'], 'Нет данных')
            if achievement != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} {sphere['key']} | {achievement} |")

    # Мои метрики
    if pro_data.get('Мои метрики') or standard_metrics:
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📝📊 Мои метрики')
        dashboard_content.append("> | Сфера | Метрика | Текущее значение | Целевое значение |")
        dashboard_content.append("> |:---|:---|:---:|:---:|")
        
        # Получаем фактические данные из черновика
        actual_metrics_list = pro_data.get('Мои метрики', [])
        # Преобразуем их в словарь для быстрого доступа: {(сфера, название): {данные}}
        actual_metrics_map = {(m['sphere'], m['metric']): m for m in actual_metrics_list}

        # Итерируемся по стандартным метрикам из БД
        for sphere_config in SPHERES_CONFIG:
            sphere_key = sphere_config['key']
            sphere_emoji = sphere_config['emoji']
            
            # Проходим по всем стандартным метрикам для данной сферы
            for metric_name in standard_metrics.get(sphere_key, []):
                # Ищем фактические данные для этой стандартной метрики
                metric_data = actual_metrics_map.get((sphere_key, metric_name))
                
                current = metric_data['current'] if metric_data else "-"
                target = metric_data['target'] if metric_data else "-"

                dashboard_content.append(f"> | {sphere_emoji} {sphere_key} | {metric_name} | {current} | {target} |")

    # --- Рекомендации AI ---
    if recommendations:
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🤖 AI рекомендации')
        dashboard_content.append("> | Сфера | Рекомендация |")
        dashboard_content.append("> |:---|:---|")
        for sphere_key, rec in recommendations.items():
            sphere_emoji = next((s['emoji'] for s in SPHERES_CONFIG if s['key'] == sphere_key), '')
            dashboard_content.append(f"> | {sphere_emoji} {sphere_key} | {rec} |")

    # Записываем контент в файл
    dashboard_path = os.path.join(INTERFACES_DIR, 'dashboard.md')
    try:
        with open(dashboard_path, 'w', encoding='utf-8-sig') as f:
            f.write("\n".join(dashboard_content))
        logging.info(f"Дашборд успешно сгенерирован и сохранен в: {dashboard_path}")
    except Exception as e:
        logging.critical(f"Не удалось записать в файл дашборда: {e}", exc_info=True)

    logging.info("--- ✅ AI Dashboard Injector завершил работу ---")


if __name__ == '__main__':
    # Настройка логирования для прямого запуска
    log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Вывод в консоль
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(log_formatter)
    
    # Корень логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(console)

    run_injector() 