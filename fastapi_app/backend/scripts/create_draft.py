import os
import sys
from datetime import datetime
import json
import re
from typing import Dict, List, Any
import logging

# Определение корня проекта
# __file__ -> scripts/create_draft.py
# os.path.dirname(...) -> scripts/
# os.path.dirname(...) -> hpi/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT_FOLDER = os.path.join(PROJECT_ROOT, "reports_draft")
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'questions.md')

# Конфигурация сфер для сохранения правильного порядка и названий
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

def parse_question_database() -> Dict[str, Dict[str, List[Any]]]:
    """
    Парсит questions.md и извлекает полную структуру вопросов и метрик.
    """
    if not os.path.exists(DB_PATH):
        logging.error(f"Файл базы данных вопросов не найден: {DB_PATH}")
        sys.exit(1)

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    all_data = {sphere['key']: {'basic': [], 'metrics': []} for sphere in SPHERES_CONFIG}
    
    # Обновленный паттерн, который ищет emoji и название в конфигурации, а не пытается парсить их
    for sphere_config in SPHERES_CONFIG:
        sphere_key = sphere_config['key']
        sphere_emoji = sphere_config['emoji']
        
        # Создаем паттерн для конкретной сферы
        pattern = re.compile(rf"##\s*{re.escape(sphere_emoji)}\s*{re.escape(sphere_key)}\n```json\n([\s\S]+?)\n```", re.DOTALL)
        match = pattern.search(content)
        
        if not match:
            logging.warning(f"Не найден JSON-блок для сферы '{sphere_key}'")
            continue
        
        try:
            items = json.loads(match.group(1))
            for item in items:
                if item.get("type") == "basic":
                    all_data[sphere_key]['basic'].append(item)
                elif item.get("category") == "metrics" and "metrics" in item:
                    all_data[sphere_key]['metrics'].extend(item["metrics"])
        except json.JSONDecodeError:
            logging.error(f"Ошибка декодирования JSON для сферы '{sphere_key}'")
            continue
            
    return all_data

def generate_draft_content(db_data: Dict[str, Dict[str, List[Any]]]) -> str:
    """
    Генерирует полное содержимое файла черновика на основе данных из БД.
    """
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # --- Собираем HPI секции (вопросы 1-8) ---
    hpi_sections = []
    for i, sphere_config in enumerate(SPHERES_CONFIG, 1):
        sphere_key = sphere_config['key']
        sphere_emoji = sphere_config['emoji']
        sphere_title = f"## {i}. {sphere_emoji} {sphere_key}"
        
        table_header = "| Вопрос | Варианты | Ответ |\n|:---|:---|:---:|"
        
        questions = db_data.get(sphere_key, {}).get('basic', [])
        
        table_rows = []
        for q in questions:
            options_list = q.get('options', [])
            # Форматируем варианты в одну строку: "1. Вариант; 2. Вариант; ..."
            formatted_options = "; ".join([f"{i+1}. {opt}" for i, opt in enumerate(options_list)])
            table_rows.append(f"| {q.get('text', 'Нет текста')} | {formatted_options} | |")
        
        hpi_sections.append(f"{sphere_title}\n{table_header}\n" + "\n".join(table_rows))
        
    # --- Собираем PRO секции ---
    pro_sections_map = {
        'Мои проблемы': '🛑',
        'Мои цели': '🎯',
        'Мои блокеры': '🚧',
        'Мои достижения': '🏆'
    }
    pro_sections = []
    for title, emoji in pro_sections_map.items():
        section_title = f"### {emoji} {title}"
        table_header = "| Сфера жизни | Ваши ответы |\n|:---|:---|"
        table_rows = [f"| {s['emoji']} {s['key']} | |" for s in SPHERES_CONFIG]
        pro_sections.append(f"{section_title}\n{table_header}\n" + "\n".join(table_rows))

    # --- Собираем секцию "Мои метрики" ---
    metrics_header = "| Сфера жизни | Метрика | Текущее | Целевое |\n|:---|:---|:---:|:---:|"
    metrics_rows = []
    for sphere_config in SPHERES_CONFIG:
        sphere_key = sphere_config['key']
        sphere_emoji = sphere_config['emoji']
        metrics = db_data.get(sphere_key, {}).get('metrics', [])
        for metric in metrics:
            metrics_rows.append(f"| {sphere_emoji} {sphere_key} | {metric.get('name', 'Нет названия')} | | |")
    metrics_section = f"### 📊 Мои метрики\n{metrics_header}\n" + "\n".join(metrics_rows)
    
    # --- Собираем всё вместе ---
    final_content = f"""# HPI Отчет

> [!NOTE]
> Дата: {date_str}
> Заполните все таблицы ниже. Для вопросов по сферам используйте шкалу от 1 до 4.

---

{"\n\n".join(hpi_sections)}

---

# HPI PRO

{"\n\n".join(pro_sections)}

{metrics_section}
"""
    return final_content.strip()

def create_draft_report():
    """
    Создает файл черновика HPI на сегодняшнюю дату на основе questions.md.
    """
    os.makedirs(DRAFT_FOLDER, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    draft_filename = f"{today_str}_draft.md"
    draft_filepath = os.path.join(DRAFT_FOLDER, draft_filename)

    if os.path.exists(draft_filepath):
        logging.warning(f"Черновик на сегодня ({draft_filename}) уже существует.")
        return

    try:
        logging.info("Парсинг базы данных вопросов...")
        db_data = parse_question_database()
        logging.info("Генерация нового черновика...")
        draft_content = generate_draft_content(db_data)
        
        with open(draft_filepath, 'w', encoding='utf-8') as f:
            f.write(draft_content)
            
        logging.info(f"Успешно создан черновик: {draft_filepath}")
    except Exception as e:
        logging.error(f"Ошибка при создании черновика: {e}")

if __name__ == "__main__":
    create_draft_report() 