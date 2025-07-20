import os
import sys
from datetime import datetime
import json
import re
from typing import Dict, List, Any

# Добавляем корень в sys.path для импорта из src
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from src.config import SPHERE_CONFIG

DRAFT_FOLDER = os.path.join(PROJECT_ROOT, "reports_draft")
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'questions.md')

def parse_question_database() -> Dict[str, Dict[str, List[Any]]]:
    """
    Парсит questions.md и извлекает полную структуру вопросов и метрик.
    """
    if not os.path.exists(DB_PATH):
        print(f"🔴 Ошибка: Файл базы данных вопросов не найден: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    all_data = {sphere['name']: {'basic': [], 'metrics': []} for sphere in SPHERE_CONFIG}
    
    # Обновленный паттерн, который ищет emoji и название в конфигурации, а не пытается парсить их
    for sphere_config in SPHERE_CONFIG:
        sphere_key = sphere_config['name']
        sphere_emoji = sphere_config['emoji']
        
        # Создаем паттерн для конкретной сферы
        pattern = re.compile(rf"##\s*{re.escape(sphere_emoji)}\s*{re.escape(sphere_key)}\n```json\n([\s\S]+?)\n```", re.DOTALL)
        match = pattern.search(content)
        
        if not match:
            print(f"🟡 Предупреждение: не найден JSON-блок для сферы '{sphere_key}'", file=sys.stderr)
            continue
        
        try:
            items = json.loads(match.group(1))
            for item in items:
                if item.get("type") == "basic":
                    all_data[sphere_key]['basic'].append(item)
                elif item.get("category") == "metrics" and "metrics" in item:
                    all_data[sphere_key]['metrics'].extend(item["metrics"])
        except json.JSONDecodeError:
            print(f"🔴 Ошибка декодирования JSON для сферы '{sphere_key}'", file=sys.stderr)
            continue
            
    return all_data

def generate_draft_content(db_data: Dict[str, Dict[str, List[Any]]]) -> str:
    """
    Генерирует полное содержимое файла черновика на основе данных из БД.
    """
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # --- Собираем HPI секции (вопросы 1-8) ---
    hpi_sections = []
    for i, sphere_config in enumerate(SPHERE_CONFIG, 1):
        sphere_key = sphere_config['name']
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
        table_rows = [f"| {s['emoji']} {s['name']} | |" for s in SPHERE_CONFIG]
        pro_sections.append(f"{section_title}\n{table_header}\n" + "\n".join(table_rows))

    # --- Собираем секцию "Мои метрики" ---
    metrics_header = "| Сфера жизни | Метрика | Текущее | Целевое |\n|:---|:---|:---:|:---:|"
    metrics_rows = []
    for sphere_config in SPHERE_CONFIG:
        sphere_key = sphere_config['name']
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
        print(f"🟡 Черновик на сегодня ({draft_filename}) уже существует.")
        return

    try:
        print("⚙️  Парсинг базы данных вопросов...")
        db_data = parse_question_database()
        print("📝  Генерация нового черновика...")
        draft_content = generate_draft_content(db_data)
        
        with open(draft_filepath, 'w', encoding='utf-8') as f:
            f.write(draft_content)
            
        print(f"✅ Успешно создан черновик: {draft_filepath}")
    except Exception as e:
        print(f"🔴 Ошибка при создании черновика: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Принудительно устанавливаем кодировку UTF-8 для вывода
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except TypeError:
            pass
    create_draft_report() 