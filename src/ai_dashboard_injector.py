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
from typing import Dict

# --- Принудительное использование UTF-8 ---
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        print("Warning: Could not set locale to UTF-8. Emoji support might be limited.")
# --- Конец принудительного использования UTF-8 ---

# --- Пути к папкам ---
# Определяем корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DRAFTS_DIR = os.path.join(PROJECT_ROOT, "reports_draft")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports_final")
INTERFACES_DIR = os.path.join(PROJECT_ROOT, "interfaces")
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "app.log")

# Маппинг сфер и emoji
SPHERES = [
    ("💖", "Отношения с любимыми"),
    ("🏡", "Отношения с родными"),
    ("🤝", "Друзья"),
    ("💼", "Карьера"),
    ("♂️", "Физическое здоровье"),
    ("🧠", "Ментальное здоровье"),
    ("🎨", "Хобби и увлечения"),
    ("💰", "Благосостояние")
]

# --- Справочник синонимов сфер (название, emoji, сокращения) ---
SPHERE_SYNONYMS = {
    'Отношения с любимыми': ['Отношения с любимыми', '💖'],
    'Отношения с родными': ['Отношения с родными', '🏡'],
    'Друзья': ['Друзья', '🤝'],
    'Карьера': ['Карьера', '💼'],
    'Физическое здоровье': ['Физическое здоровье', '♂️'],
    'Ментальное здоровье': ['Ментальное здоровье', '🧠'],
    'Хобби и увлечения': ['Хобби и увлечения', 'Хобби', '🎨'],
    'Благосостояние': ['Благосостояние', '💰'],
}

# Варианты позитивных и поддерживающих фраз
POSITIVE_PHRASES = [
    "Вы на правильном пути!",
    "Продолжайте в том же духе!",
    "Ваш прогресс вдохновляет!",
    "Маленькие шаги ведут к большим результатам!"
]

# Варианты мотивации для сложных ситуаций
MOTIVATION_PHRASES = [
    "Даже маленькое действие — уже победа.",
    "Не бойтесь просить поддержки у близких.",
    "Каждый шаг — вклад в ваше благополучие.",
    "Важно заботиться о себе, даже если кажется, что нет сил."
]

# Варианты для SMART-целей
SMART_PHRASES = [
    "Отлично, что ваша цель конкретна и измерима!",
    "SMART-цели — залог успеха. Продолжайте!",
    "Чёткая цель помогает двигаться вперёд."
]

# Варианты для поздравления с достижениями
ACHIEVE_PHRASES = [
    "Поздравляем с достижением!",
    "Ваш успех — отличный пример!",
    "Здорово, что вы отмечаете свои победы!"
]

# Варианты для профилактики
PREVENT_PHRASES = [
    "Даже если сейчас всё хорошо, подумайте, что поможет сохранить баланс.",
    "Профилактика — лучший способ избежать проблем в будущем.",
    "Ищите новые точки роста, даже если нет явных трудностей."
]

# Примеры конкретных шагов по сферам
SPHERE_EXAMPLES = {
    'Отношения с любимыми': [
        "Проведите вечер вместе без гаджетов.",
        "Сделайте небольшой сюрприз или напишите тёплое сообщение.",
        "Обсудите планы на выходные или совместный отдых."
    ],
    'Отношения с родными': [
        "Позвоните близкому человеку и поинтересуйтесь его делами.",
        "Запланируйте семейный ужин или прогулку.",
        "Поблагодарите родных за поддержку."
    ],
    'Друзья': [
        "Напишите другу, с которым давно не общались.",
        "Организуйте встречу или совместное занятие.",
        "Поддержите друга в его начинаниях."
    ],
    'Карьера': [
        "Поставьте небольшую рабочую цель на неделю.",
        "Попросите обратную связь у коллеги.",
        "Освойте новый навык или инструмент."
    ],
    'Физическое здоровье': [
        "Сделайте короткую зарядку или прогулку.",
        "Проверьте режим сна и питания.",
        "Запишитесь на профилактический осмотр."
    ],
    'Ментальное здоровье': [
        "Выделите 10 минут на медитацию или дыхательные упражнения.",
        "Поговорите с близким о своих чувствах.",
        "Сделайте паузу для отдыха и восстановления."
    ],
    'Хобби и увлечения': [
        "Посвятите время любимому занятию хотя бы 30 минут.",
        "Попробуйте что-то новое или вернитесь к старому хобби.",
        "Поделитесь своим увлечением с друзьями."
    ],
    'Благосостояние': [
        "Проверьте расходы за неделю и выделите небольшую сумму на себя.",
        "Поставьте финансовую мини-цель.",
        "Изучите новую стратегию сбережений."
    ]
}

# --- Функция для поиска сферы по синониму ---
def find_sphere_key(name):
    for key, synonyms in SPHERE_SYNONYMS.items():
        for syn in synonyms:
            if syn.strip().lower() == name.strip().lower():
                return key
    return name  # если не найдено, вернуть как есть

def parse_pro_section(md_content: str, section_title: str) -> Dict[str, str]:
    """
    Извлекает данные из таблицы в указанном PRO-разделе.
    Функция ищет заголовок раздела, а затем построчно анализирует таблицу.
    """
    answers = {}
    in_section = False
    
    # Сначала найдем все синонимы для более гибкого поиска
    all_spheres_synonyms = {}
    for sphere, synonyms in SPHERE_SYNONYMS.items():
        for synonym in synonyms:
             all_spheres_synonyms[synonym.lower()] = sphere

    lines = md_content.split('\n')
    
    for i, line in enumerate(lines):
        # Ищем начало нужной секции
        if section_title in line and line.strip().startswith('###'):
            in_section = True
            # Пропускаем сам заголовок и шапку таблицы
            # и начинаем поиск со следующей строки
            for table_line in lines[i+1:]:
                # Если дошли до следующей секции или конца файла - выходим
                if table_line.strip().startswith('###'):
                    break
                
                # Ищем строку таблицы
                if table_line.strip().startswith('|'):
                    parts = [p.strip() for p in table_line.split('|') if p.strip()]
                    if len(parts) >= 2:
                        sphere_candidate = parts[0].lower()
                        # Ищем сферу по синонимам
                        sphere_key = find_sphere_key(sphere_candidate)
                        if sphere_key:
                            answer = parts[1]
                            answers[sphere_key] = answer if answer.lower() not in ['нет', 'нет данных'] else "Нет данных"
            break # Выходим из основного цикла, т.к. секция найдена и обработана
            
    # Убедимся, что все сферы имеют значение
    for sphere_key in SPHERE_SYNONYMS:
        if sphere_key not in answers:
            answers[sphere_key] = "Нет данных"
            
    log_to_file(f"Результаты парсинга секции '{section_title}': {answers}", "DEBUG")
    return answers

# Функция для преобразования числового приоритета в текст
def priority_to_text(priority: float) -> str:
    if priority >= 9.0:
        return "Критический"
    elif priority >= 8.0:
        return "Высокий"
    elif priority >= 6.0:
        return "Средний"
    else:
        return "Низкий"

def find_latest_draft():
    """Находит последний по дате изменения черновик в папке."""
    try:
        if not os.path.exists(DRAFTS_DIR):
            log_to_file(f"Папка с черновиками не найдена: {DRAFTS_DIR}", "WARNING")
            return None

        # Ищем файлы по новому стандарту: YYYY-MM-DD_draft.md
        drafts = [os.path.join(DRAFTS_DIR, f) for f in os.listdir(DRAFTS_DIR) if f.endswith("_draft.md") and re.match(r"\d{4}-\d{2}-\d{2}", f)]
        
        if not drafts:
            log_to_file("Черновики по стандарту 'YYYY-MM-DD_draft.md' не найдены.", "INFO")
            return None
            
        latest_draft = max(drafts, key=os.path.getmtime)
        return latest_draft
    except Exception as e:
        log_to_file(f"Ошибка при поиске последнего черновика: {e}", "ERROR")
        return None

def extract_answers_by_sphere(md_content):
    # Извлекает ответы по сферам из секции PRO ("Мои проблемы")
    answers = {}
    for emoji, sphere in SPHERES:
        pat = rf"\|\s*{re.escape(sphere)}\s*\|([^|]*)\|"
        m = re.search(pat, md_content)
        answers[sphere] = m.group(1).strip() if m else "Нет данных"
    return answers

def is_smart_goal(goal_text):
    """Базовая проверка SMART: наличие числа, срока, конкретики."""
    import re
    if not goal_text or goal_text.strip() == '' or goal_text.lower() in ['нет', 'нет данных']:
        return False
    # Признаки SMART: есть число, срок, конкретика
    has_number = bool(re.search(r'\d', goal_text))
    has_time = any(word in goal_text.lower() for word in ['недел', 'месяц', 'год', 'квартал', 'день'])
    has_action = any(word in goal_text.lower() for word in ['организовать', 'запланировать', 'увеличить', 'создать', 'начать', 'закончить', 'пройти', 'выделить', 'достичь'])
    return has_number and has_time and has_action

def analyze_and_generate_recommendations_v2(md_content, pro_data):
    """
    Расширенный анализ по всем сферам: метрики, дисбаланс, гиперфокус, SMART-цели, расхождения, блокеры, достижения.
    Возвращает список Recommendation.
    """
    from ai_recommendations import Recommendation, RecommendationType, RecommendationData, ActionStep, Metrics, Evidence
    recommendations = []
    # --- Новый парсер метрик по строкам таблицы (устойчивый к пустым строкам) ---
    sphere_metrics = {}
    in_metrics = False
    table_started = False
    last_sphere = None
    for line in md_content.split('\n'):
        if 'Мои метрики' in line:
            in_metrics = True
            continue
        if in_metrics:
            if line.strip().startswith('|'):
                table_started = True
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(cells) >= 4:
                    if cells[0]:
                        last_sphere = cells[0]
                    elif last_sphere:
                        cells[0] = last_sphere
                    else:
                        continue
                    key = find_sphere_key(cells[0])
                    try:
                        # Принимаем только значения в шкале от 1 до 10
                        value = float(cells[2])
                        if 1.0 <= value <= 10.0:
                            sphere_metrics[key] = value
                    except (ValueError, IndexError):
                        # Игнорируем, если не число или нет ячейки
                        continue
            elif table_started and not line.strip().startswith('|'):
                break  # закончили таблицу
    # --- Дисбаланс и гиперфокус ---
    metric_values = list(sphere_metrics.values())
    min_val = min(metric_values) if metric_values else 0
    max_val = max(metric_values) if metric_values else 0
    disbalance = (max_val - min_val) >= 3
    hyperfocus = max_val >= 9 and all(v <= 6 for v in metric_values if v != max_val)
    # --- Анализ по каждой сфере ---
    for emoji, sphere in SPHERES:
        # Данные PRO
        problem = pro_data['problems'].get(sphere, '') or pro_data['problems'].get(find_sphere_key(sphere), '')
        goal = pro_data['goals'].get(sphere, '') or pro_data['goals'].get(find_sphere_key(sphere), '')
        blocker = pro_data['blockers'].get(sphere, '') or pro_data['blockers'].get(find_sphere_key(sphere), '')
        achievement = pro_data['achievements'].get(sphere, '') or pro_data['achievements'].get(find_sphere_key(sphere), '')
        problem = problem.strip()
        goal = goal.strip()
        blocker = blocker.strip()
        achievement = achievement.strip()
        # Метрика
        metric = sphere_metrics.get(sphere, None)
        # Признаки
        low_metric = metric is not None and metric < 6
        very_low_metric = metric is not None and metric < 3
        smart_goal = is_smart_goal(goal)
        has_problem = problem and problem.lower() not in ['нет', 'нет данных']
        has_blocker = blocker and blocker.lower() not in ['нет', 'нет данных']
        has_achievement = achievement and achievement.lower() not in ['нет', 'нет данных']
        # Расхождение: если метрика >=7, но есть проблема/блокер, или наоборот
        mismatch = (metric is not None and metric >= 7 and (has_problem or has_blocker)) or (metric is not None and metric < 6 and not has_problem and not has_blocker)
        
        # --- Логика генерации рекомендаций ---
        # Эта часть кода является упрощенной версией. Здесь можно добавить сложную логику.
        rec_data = RecommendationData(
            title=f"Рекомендация для сферы '{sphere}'",
            description="",
            action_steps=[],
            metrics=Metrics(target_improvement=0, timeframe="", success_criteria=[]),
            related_spheres=[],
            evidence=Evidence(data_points=[], correlations=[], historical_success=0)
        )
        recommendations.append(Recommendation(
            recommendation_id=f"rec_{random.randint(1000,9999)}",
            timestamp=datetime.now(),
            sphere=sphere,
            type=RecommendationType.IMMEDIATE,
            priority=5.0, # Placeholder
            data=rec_data
        ))

    return recommendations

def insert_ai_block_to_dashboard(ai_block_path, dashboard_path):
    """
    Вставляет или обновляет блок AI рекомендаций в дашборде после блока 'Мои достижения'.
    """
    with open(ai_block_path, "r", encoding="utf-8") as f:
        ai_block = f.read().strip()
    with open(dashboard_path, "r", encoding="utf-8") as f:
        dashboard = f.read()
    # Найти конец блока 'Мои достижения'
    pattern = r'(> \[!info\]- 🏆 Мои достижения[\s\S]+?\n\n)'
    match = re.search(pattern, dashboard)
    if match:
        insert_pos = match.end()
        # Удалить старый блок AI рекомендаций, если есть
        ai_pat = r'(> \[!info\]- 🤖 AI рекомендации[\s\S]+?)(?=\n> \[!info\]-|\Z)'
        dashboard_wo_ai = re.sub(ai_pat, '', dashboard[insert_pos:], count=1)
        new_dashboard = dashboard[:insert_pos] + '\n' + ai_block + '\n' + dashboard_wo_ai
    else:
        # Если не найден блок достижений — добавить в конец
        new_dashboard = dashboard + '\n' + ai_block + '\n'
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(new_dashboard)

def log_to_file(message: str, level: str = "INFO"):
    """Записывает сообщение в лог-файл."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\\n")
    except Exception as e:
        # В случае ошибки кодировки, пробуем записать без проблемных символов
        try:
            with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as logf:
                logf.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\\n [Logging Error: {e}]\\n")
        except Exception as inner_e:
             print(f"Не удалось записать в лог-файл: {inner_e}")

def main():
    """Главная функция."""
    # Используем абсолютные пути, чтобы избежать проблем с относительными путями
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # Поднимаемся на уровень выше из src
    drafts_dir = os.path.join(project_root, 'reports_draft')
    interfaces_dir = os.path.join(project_root, 'interfaces')
    reports_dir = os.path.join(project_root, 'reports_final')
    log_file = os.path.join(project_root, 'logs', 'app.log')

    def log_to_file_main(message: str, level: str = "INFO"):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8", errors="replace") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\\n")
    
    log_to_file_main("--- 🚀 Запуск AI Dashboard Injector (с абсолютными путями) ---")
    
    try:
        # --- Поиск последнего черновика ---
        drafts = [os.path.join(drafts_dir, f) for f in os.listdir(drafts_dir) if f.endswith("_draft.md")]
        if not drafts:
            log_to_file_main("Не найдены файлы черновиков.", "ERROR")
            return
        latest_draft = max(drafts, key=os.path.getmtime)
        log_to_file_main(f"Найден последний черновик: {latest_draft}")

        with open(latest_draft, 'r', encoding='utf-8') as f:
            md_content = f.read()

        pro_data = {
            'problems': parse_pro_section(md_content, 'Мои проблемы'),
            'goals': parse_pro_section(md_content, 'Мои цели'),
            'blockers': parse_pro_section(md_content, 'Мои блокеры'),
            'achievements': parse_pro_section(md_content, 'Мои достижения')
        }
        log_to_file_main(f"Данные из PRO секций извлечены: {pro_data}")

        dashboard_path = os.path.join(interfaces_dir, 'dashboard.md')
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_content = f.read()

        sections = {
            '🛑 Мои проблемы': pro_data['problems'],
            '🎯 Мои цели': pro_data['goals'],
            '🚧 Мои блокеры': pro_data['blockers'],
            '🏆 Мои достижения': pro_data['achievements']
        }

        for section_title, data in sections.items():
            section_pattern = re.compile(rf'> \[!info\]- {re.escape(section_title)}[\s\S]*?(?=> \[!info\]-|\Z)')
            new_section_content = [f"> [!info]- {section_title}", ">", "> | Сфера | Ваши ответы |", "> |:------:|-------------|"]
            sorted_spheres = sorted(SPHERE_SYNONYMS.keys(), key=lambda x: list(SPHERE_SYNONYMS.keys()).index(x))
            for sphere_name in sorted_spheres:
                synonyms = SPHERE_SYNONYMS[sphere_name]
                emoji = next((s for s in synonyms if len(s) == 2), '❓') 
                answer = data.get(sphere_name, "Нет данных")
                if not answer or answer.strip() == '':
                    answer = "Нет данных"
                new_section_content.append(f"> |  {emoji}  | {answer} |")
            new_section_text = "\\n".join(new_section_content) + "\\n"
            dashboard_content, count = section_pattern.subn(new_section_text, dashboard_content, count=1)
            if count > 0:
                log_to_file_main(f"Секция '{section_title}' успешно заменена.")
            else:
                log_to_file_main(f"Секция '{section_title}' не найдена в дашборде.", "WARNING")

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        log_to_file_main(f"Дашборд сохранен: {dashboard_path}")

        # Анализ и генерация рекомендаций
        engine = HPIRecommendationEngine()
        recommendations = analyze_and_generate_recommendations_v2(md_content, pro_data)

        # Получаем дату из имени файла черновика
        report_date_str = os.path.basename(latest_draft)[:10]

        # Сохранение рекомендаций в JSON
        recs_filepath = os.path.join(reports_dir, f"{report_date_str}_recommendations.json")
        engine.save_recommendations(recommendations, recs_filepath)
        log_to_file_main(f"AI-рекомендации сохранены в {recs_filepath}")

    except Exception as e:
        import traceback
        log_to_file_main(f"Критическая ошибка в AI Dashboard Injector: {e}\\n{traceback.format_exc()}", "ERROR")
        raise

if __name__ == "__main__":
    main() 