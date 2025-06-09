"""
HPI AI Dashboard Injector
Генерирует файл AI_Recommendations.md с актуальными рекомендациями для дашборда HPI.
"""
import os
import re
import datetime
from ai_recommendations import HPIRecommendationEngine
import random
import sys

# --- Пути к папкам ---
# Определяем корень проекта (папка 'HPI v.0.3')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DRAFTS_DIR = os.path.join(PROJECT_ROOT, "reports_draft")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports_final")
INTERFACES_DIR = os.path.join(PROJECT_ROOT, "interfaces")
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "hpi.log")

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
    drafts = [os.path.join(DRAFTS_DIR, f) for f in os.listdir(DRAFTS_DIR) if f.endswith("_report.md")]
    if not drafts:
        return None
    latest_draft = max(drafts, key=os.path.getmtime)
    return latest_draft

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

def analyze_and_generate_recommendations_v2(answers, md_content, pro_data):
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
        # Приоритет признаков (новая шкала)
        if very_low_metric or (has_problem and has_blocker):
            priority = 9.5
        elif has_problem or has_blocker:
            priority = 8.5
        elif low_metric or disbalance or hyperfocus:
            priority = 7.0
        else:
            priority = 5.0
        # Формируем развернутую рекомендацию
        lines = []
        # 1. Критически низкая метрика
        if very_low_metric:
            lines.append(f"Внимание! Оценка по этой сфере — {metric}. Это критически низкий уровень.")
            lines.append(random.choice(MOTIVATION_PHRASES))
        # 2. Проблемы и блокеры
        if has_problem or has_blocker:
            lines.append(f"Вы отметили трудности: {problem if has_problem else ''} {blocker if has_blocker else ''}".strip())
            lines.append("Рекомендуем проанализировать причины и выделить время для поиска решений.")
            if has_blocker:
                lines.append("Попробуйте разделить препятствия на внешние и внутренние, и для каждого найти хотя бы один способ преодоления.")
        # 3. Просто низкая метрика
        if low_metric and not very_low_metric:
            lines.append(f"Текущая оценка по этой сфере — {metric}. Это ниже рекомендуемого уровня.")
            lines.append("Сделайте маленький шаг: " + random.choice(SPHERE_EXAMPLES.get(sphere, ["Выберите простое действие для этой сферы."])))
        # 4. SMART-цели
        if goal:
            if smart_goal:
                lines.append(random.choice(SMART_PHRASES) + f" Ваша цель: {goal}")
            else:
                lines.append(f"Цель по этой сфере не соответствует SMART: {goal}. Попробуйте сделать её более конкретной, измеримой и достижимой.")
        # 5. Достижения
        if has_achievement:
            lines.append(random.choice(ACHIEVE_PHRASES) + f" ({achievement}) Закрепите успех — отметьте, что помогло вам добиться результата.")
        # 6. Дисбаланс/гиперфокус
        if disbalance:
            lines.append("Обнаружен дисбаланс между сферами жизни. Важно уделять внимание не только сильным, но и слабым областям.")
        if hyperfocus:
            lines.append("Видим гиперфокус на одной сфере при низких оценках остальных. Это может привести к стрессу и выгоранию. Постарайтесь распределять ресурсы более равномерно.")
        # 7. Расхождения
        if mismatch:
            lines.append("Обнаружено расхождение между вашими количественными и качественными ответами. Рекомендуем провести саморефлексию: возможно, вы недооцениваете или переоцениваете ситуацию.")
        # 8. Профилактика/развитие
        if not lines:
            lines.append(random.choice(PREVENT_PHRASES))
            lines.append(random.choice(POSITIVE_PHRASES))
        # Собираем текст рекомендации
        rec_text = '\n'.join(lines[:6])  # максимум 6 строк
        # --- Логирование для отладки ---
        print(f"[DEBUG] {sphere}: metric={metric}, problem={problem}, blocker={blocker}, low_metric={low_metric}, has_problem={has_problem}, has_blocker={has_blocker}")
        print(f"[DEBUG] Recommendation text: {rec_text}\n---")
        recommendations.append(Recommendation(
            recommendation_id=f"rec_{random.randint(1000,9999)}",
            timestamp=datetime.datetime.now(),
            sphere=sphere,
            type=RecommendationType.IMMEDIATE if priority >= 8 else RecommendationType.SHORT_TERM,
            priority=priority,
            data=RecommendationData(
                title=rec_text,
                description=rec_text,
                action_steps=[],
                metrics=None,
                related_spheres=[],
                evidence=None
            )
        ))
    return recommendations, sphere_metrics

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
    """Appends a timestamped message to the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\n")

def main():
    """Основная функция, которая запускает весь процесс."""
    # Принудительно устанавливаем кодировку UTF-8 для вывода в консоль
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    try:
        # Определяем пути внутри main
        dashboard_path = os.path.join(INTERFACES_DIR, "dashboard.md")
        ai_recommendations_path = os.path.join(INTERFACES_DIR, "ai_recommendations.md")

        log_to_file("--- 🤖 Запуск AI Dashboard Injector ---")
        
        # --- 1. Поиск последнего черновика ---
        latest_draft_path = find_latest_draft()
        if not latest_draft_path:
            log_to_file("ПРЕДУПРЕЖДЕНИЕ: Не найдены черновики отчетов в папке 'reports_draft'.", "WARNING")
            return

        with open(latest_draft_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        # 2. Определить дату
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", latest_draft_path)
        report_date = date_match.group(1) if date_match else datetime.date.today().isoformat()
        # 3. Извлечь ответы по сферам
        answers = extract_answers_by_sphere(md_content)
        # 3.1. Извлечь PRO-данные
        def parse_pro_table(section_title):
            result = {}
            in_section = False
            for line in md_content.split('\n'):
                if section_title in line:
                    in_section = True
                elif in_section and line.strip().startswith('|') and not line.lower().startswith('| сфера') and not set(line.strip()) <= {'|', '-', ' '}:
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if len(cells) >= 2:
                        key = find_sphere_key(cells[0])
                        value = cells[1]
                        result[key] = value
                elif in_section and not line.strip().startswith('|'):
                    break  # закончили таблицу
            return result
        pro_data = {
            'problems': parse_pro_table('Мои проблемы'),
            'goals': parse_pro_table('Мои цели'),
            'blockers': parse_pro_table('Мои блокеры'),
            'achievements': parse_pro_table('Мои достижения'),
        }
        # 4. Генерировать рекомендации по сферам (расширенный анализ)
        engine = HPIRecommendationEngine()
        engine.recommendations, sphere_metrics = analyze_and_generate_recommendations_v2(answers, md_content, pro_data)
        # 5. Сопоставить рекомендации со сферами
        rec_map = {rec.sphere: rec for rec in engine.recommendations}
        # 6. Сформировать Markdown-таблицу
        header = f"# 🤖 AI рекомендации ({report_date})\n\n| Сфера | Рекомендация | Приоритет |\n|:------:|--------------|:---------:|\n"
        rows = ""
        for emoji, sphere in SPHERES:
            rec = rec_map.get(sphere)
            metric = sphere_metrics.get(sphere, None)
            metric_str = f"{metric:.1f}" if metric is not None else '—'
            sphere_cell = f"{emoji}<br>{metric_str}"
            if rec:
                # Удаляем все строки, содержащие 'оценка' или 'уровень' (case-insensitive)
                lines = rec.data.title.split('\n')
                filtered_lines = [line for line in lines if not re.search(r'(оценка|уровень)', line, re.IGNORECASE)]
                text = '<br>'.join(filtered_lines).strip()
                priority = priority_to_text(rec.priority)
            else:
                text = "Нет рекомендаций"
                priority = "—"
            rows += f"| {sphere_cell} | {text} | {priority} |\n"
        content = header + rows
        # 7. Сохранить финальный отчет
        output_file = os.path.join(REPORTS_DIR, f"{report_date} AI_Recommendations.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        # 8. Вставить блок в дашборд
        # Формируем markdown-блок для вставки (без дублирующего заголовка)
        content_lines = content.split('\n')
        # Пропускаем первую строку (заголовок) и пустую строку после него
        table_lines = content_lines[2:] if content_lines[1].strip() == '' else content_lines[1:]
        ai_block = f"> [!info]- 🤖 AI рекомендации\n>\n" + '\n'.join([f"> {line}" if (i < 2 or not line.startswith('|')) else line for i, line in enumerate(table_lines)]) + '\n'
        temp_ai_block_path = os.path.join(REPORTS_DIR, "_temp_ai_block.md")
        with open(temp_ai_block_path, "w", encoding="utf-8") as f:
            f.write(ai_block)
        insert_ai_block_to_dashboard(temp_ai_block_path, dashboard_path)
        os.remove(temp_ai_block_path)
        # 9. Логирование
        log_message = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] AI рекомендации успешно сохранены в {output_file} и добавлены в дашборд ({len(engine.recommendations)} рекомендаций)\n"
        log_to_file(log_message)
        print(f"AI рекомендации успешно сохранены в {output_file} и добавлены в дашборд")

    except Exception as e:
        # Log critical error
        import traceback
        error_message = f"Критическая ошибка в HPI_AI_Dashboard_Injector: {str(e)}\n{traceback.format_exc()}"
        log_to_file(error_message, "CRITICAL")
        print(error_message)

if __name__ == "__main__":
    main() 