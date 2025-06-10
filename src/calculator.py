"""
HPI Calculator
Version: 0.3
Release Date: 2024-03-20
Status: Development

Основной модуль расчета Human Performance Index (HPI).
"""

import os
import re
import shutil
from typing import Dict, List, Optional, Tuple
from radar import create_radar_chart
from datetime import datetime
import sys
import traceback

# Constants
MIN_ANSWER = 1
MAX_ANSWER = 4
QUESTIONS_PER_SPHERE = 6

# --- Пути к папкам ---
# Определяем корень проекта (папка 'HPI v.0.3')
# __file__ -> src/calculator.py
# os.path.dirname(__file__) -> src/
# os.path.dirname(...) -> корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Папки для отчетов и интерфейсов
DRAFT_FOLDER = os.path.join(PROJECT_ROOT, "reports_draft")
FINAL_FOLDER = os.path.join(PROJECT_ROOT, "reports_final")
INTERFACES_FOLDER = os.path.join(PROJECT_ROOT, "interfaces")

# Нелинейная шкала Фибоначчи для преобразования ответов
FIBONACCI_SCORES = {
    1: 1.0,  # Базовый уровень
    2: 2.0,  # Средний уровень
    3: 3.0,  # Хороший уровень
    4: 5.0   # Отличный уровень
}

# Sphere weights (равные веса для всех сфер)
SPHERE_WEIGHTS = {
    "1": 0.125,  # Отношения с любимыми
    "2": 0.125,  # Отношения с родными
    "3": 0.125,  # Друзья
    "4": 0.125,  # Карьера
    "5": 0.125,  # Физическое здоровье
    "6": 0.125,  # Ментальное здоровье
    "7": 0.125,  # Хобби
    "8": 0.125   # Благосостояние
}

# Sphere configuration
SPHERE_CONFIG = [
    {"number": "1", "name": "Отношения с любимыми", "emoji": "💖"},
    {"number": "2", "name": "Отношения с родными", "emoji": "🏡"},
    {"number": "3", "name": "Друзья", "emoji": "🤝"},
    {"number": "4", "name": "Карьера", "emoji": "💼"},
    {"number": "5", "name": "Физическое здоровье", "emoji": "♂️"},
    {"number": "6", "name": "Ментальное здоровье", "emoji": "🧠"},
    {"number": "7", "name": "Хобби и увлечения", "emoji": "🎨"},
    {"number": "8", "name": "Благосостояние", "emoji": "💰"}
]

# Создаем обратный справочник из emoji в имя сферы
EMOJI_TO_SPHERE_NAME = {s['emoji'].strip(): s['name'] for s in SPHERE_CONFIG}

# Синонимы сфер для парсинга метрик
SPHERE_SYNONYMS = {
    "Хобби": "Хобби и увлечения",
    # можно добавить другие варианты при необходимости
}

def apply_fibonacci_score(answer: int, inverse: bool = False) -> float:
    """Применяет нелинейное преобразование Фибоначчи к ответу."""
    if inverse:
        answer = MAX_ANSWER - answer + 1
    return FIBONACCI_SCORES[answer]

def normalize_sphere_score(raw_score: float) -> float:
    """Нормализация оценки сферы в шкалу 1-10."""
    min_possible = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[MIN_ANSWER]  # 6 * 1.0 = 6.0
    max_possible = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[MAX_ANSWER]  # 6 * 5.0 = 30.0
    
    normalized = ((raw_score - min_possible) / (max_possible - min_possible)) * 9 + 1
    return round(max(1.0, min(10.0, normalized)), 1)

def calculate_sphere_score(answers: List[int], inverse_questions: List[bool] = None) -> Tuple[float, float]:
    """Расчет сырого и нормализованного счета для сферы."""
    if len(answers) != QUESTIONS_PER_SPHERE:
        raise ValueError(f"Требуется ровно {QUESTIONS_PER_SPHERE} ответов")
    
    if not all(MIN_ANSWER <= a <= MAX_ANSWER for a in answers):
        raise ValueError(f"Все ответы должны быть числами от {MIN_ANSWER} до {MAX_ANSWER}")
    
    if inverse_questions is None:
        inverse_questions = [False] * QUESTIONS_PER_SPHERE
    
    # Применяем шкалу Фибоначчи к каждому ответу
    raw_score = sum(apply_fibonacci_score(a, inv) for a, inv in zip(answers, inverse_questions))
    normalized_score = normalize_sphere_score(raw_score)
    
    return raw_score, normalized_score

def calculate_total_hpi(sphere_scores: Dict[str, float]) -> float:
    """Расчет итогового HPI с учетом весов сфер."""
    total_weighted_score = 0
    total_weight = 0

    for sphere, score in sphere_scores.items():
        weight = SPHERE_WEIGHTS.get(sphere)
        if weight is not None and isinstance(score, (int, float)):
            total_weighted_score += score * weight
            total_weight += weight

    if total_weight == 0:
        raise ValueError("Не найдены веса для сфер")

    # Преобразование взвешенного среднего (1-10) в шкалу 20-100
    hpi_score = ((total_weighted_score / total_weight - 1) * (80/9)) + 20
    return round(max(20.0, min(100.0, hpi_score)), 1)

def extract_answers_from_section(content: str, section_name: str) -> Optional[List[int]]:
    """Извлекает ответы из секции отчета."""
    try:
        # Убираем ### из названия секции
        clean_section_name = section_name.replace("### ", "")
        
        # Ищем секцию по номеру и названию, допуская любые символы (включая emoji) между ними
        number = clean_section_name.split('.')[0]
        name = '.'.join(clean_section_name.split('.')[1:]).strip()
        section_pattern = rf"##\s*{number}\.\s*.*?\s*{re.escape(name)}.*?(\n\|[\s\S]*?)(?=\n##|\Z)"

        print(f"Ищем по шаблону: {section_pattern}")
        section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not section_match:
            print(f"Секция не найдена: {clean_section_name}")
            return None
            
        section_content = section_match.group(1)
        print(f"Найдено содержимое секции: {section_content[:100]}...")
        
        # Извлекаем все ответы из таблицы
        answers = []
        for line in section_content.split('\n'):
            if '|' in line and not line.startswith('|--') and not line.startswith('| Вопрос'):  # Пропускаем заголовки и разделители
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                print(f"Обработка строки: {cells}")
                if len(cells) >= 3:  # Должно быть минимум 3 ячейки: вопрос, варианты, ответ
                    answer = cells[-1]  # Последняя ячейка - ответ
                    if answer.isdigit():
                        answers.append(int(answer))
        
        print(f"Извлечены ответы: {answers}")
        return answers if answers else None
        
    except Exception as e:
        print(f"Ошибка при извлечении ответов из секции {section_name}: {str(e)}")
        return None

def process_hpi_report(file_path: str) -> Dict[str, float]:
    """Обработка файла отчета и расчет всех показателей."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Ошибка чтения файла: {e}")

    sphere_scores = {}
    all_data_valid = True

    # Обработка каждой сферы
    for sphere in SPHERE_CONFIG:
        try:
            # Ищем секцию в формате "## 1. Отношения с любимыми"
            section_name = f"{sphere['number']}. {sphere['name']}"
            answers = extract_answers_from_section(content, section_name)
            
            if answers and len(answers) == QUESTIONS_PER_SPHERE:
                # Определяем, какие вопросы инвертированы
                inverse_questions = [False] * QUESTIONS_PER_SPHERE
                if sphere["number"] in ["4", "6", "8"]:  # Сферы с инвертированными вопросами
                    inverse_questions[-1] = True  # Последний вопрос инвертирован
                
                _, normalized_score = calculate_sphere_score(answers, inverse_questions)
                sphere_scores[sphere["number"]] = normalized_score
            else:
                print(f"Предупреждение: В сфере '{section_name}' не все ответы заполнены")
                sphere_scores[sphere["number"]] = 0.0
                all_data_valid = False
        except Exception as e:
            print(f"Ошибка расчета для сферы {section_name}: {e}")
            sphere_scores[sphere["number"]] = 0.0
            all_data_valid = False

    # Расчет итогового HPI
    try:
        hpi_total = calculate_total_hpi(sphere_scores)
        sphere_scores["HPI"] = hpi_total
    except Exception as e:
        print(f"Ошибка расчета итогового HPI: {e}")
        sphere_scores["HPI"] = 0.0
        all_data_valid = False

    return sphere_scores

def get_score_emoji(score: float, is_hpi: bool = False) -> str:
    """Convert score to emoji indicator.
    
    Args:
        score: The score to convert
        is_hpi: Whether this is the overall HPI score (uses 20-100 scale) or sphere score (uses 1-10 scale)
    """
    if is_hpi:
        # Шкала для общего HPI (20-100)
        if score >= 80:
            return "🟢"  # Excellent
        elif score >= 60:
            return "🔵"  # Good
        elif score >= 40:
            return "🟡"  # Satisfactory
        else:
            return "🔴"  # Needs attention
    else:
        # Шкала для сфер (1-10)
        if score >= 8.0:
            return "🟢"  # Excellent
        elif score >= 6.0:
            return "🔵"  # Good
        elif score >= 4.0:
            return "🟡"  # Satisfactory
        else:
            return "🔴"  # Needs attention

def get_number_emoji(number: str) -> str:
    """Convert number to emoji digits."""
    # Format the number to ensure it has one decimal place
    try:
        formatted_number = f"{float(number):.1f}"
    except (ValueError, TypeError):
        return str(number)
    
    emoji_map = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
        ".": "."
    }
    return "".join(emoji_map.get(char, char) for char in formatted_number)

def find_latest_draft() -> Optional[str]:
    """Находит самый свежий черновик в папке DRAFT_FOLDER."""
    try:
        if not os.path.exists(DRAFT_FOLDER):
            print(f"Папка с черновиками не найдена: {DRAFT_FOLDER}")
            return None

        # Ищем файлы по новому стандарту: YYYY-MM-DD_draft.md
        drafts = [os.path.join(DRAFT_FOLDER, f) for f in os.listdir(DRAFT_FOLDER) if f.endswith("_draft.md") and re.match(r"\d{4}-\d{2}-\d{2}", f)]
        
        if not drafts:
            print("Черновики по стандарту 'YYYY-MM-DD_draft.md' не найдены.")
            return None
            
        latest_draft = max(drafts, key=os.path.getmtime)
        return latest_draft
    except Exception as e:
        print(f"Ошибка при поиске последнего черновика: {e}")
        return None

def create_final_report(draft_path: str, scores: Dict[str, float]) -> None:
    """Создает финальную версию отчета с добавленными расчетами."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    final_report_name = f"{today_str}_report.md"
    final_report_path = os.path.join(FINAL_FOLDER, final_report_name)
    
    # Копируем черновик в финальную папку
    shutil.copy(draft_path, final_report_path)

    # 5. Создать радарную диаграмму для финального отчета
    today_str = datetime.now().strftime("%Y-%m-%d")
    images_dir = os.path.join(FINAL_FOLDER, "images")
    os.makedirs(images_dir, exist_ok=True)
    radar_chart_path = os.path.join(images_dir, f"{today_str}_radar.png")
    create_radar_chart(scores, radar_chart_path, is_dashboard=False)
    print(f"🎨 Создана радарная диаграмма для отчета: {radar_chart_path}")

    # Добавляем в конец файла блок с итоговыми оценками и диаграммой
    with open(final_report_path, 'a', encoding='utf-8') as f:
        f.write("\n\n---\n\n")
        f.write("## 🏆 Итоговые оценки HPI\n\n")
        f.write(f"![Радарная диаграмма](./images/{os.path.basename(radar_chart_path)})\n\n")
        f.write("| Сфера | Оценка (1-10) | Индикатор |\n")
        f.write("|:---|:---:|:---:|\n")
        
        # Добавляем оценки по сферам
        for sphere in SPHERE_CONFIG:
            score = scores.get(sphere['number'], 0.0)
            emoji = get_score_emoji(score)
            f.write(f"| {sphere['name']} | {score} | {emoji} |\n")
        
        # Добавляем итоговый HPI
        hpi_score = scores.get('HPI', 0.0)
        hpi_emoji = get_score_emoji(hpi_score, is_hpi=True)
        f.write(f"| **Итоговый HPI** | **{hpi_score}** | {hpi_emoji} |\n")
    
    print(f"✅ Финальный отчет сохранен: {final_report_path}")

def collect_all_reports_data() -> List[Tuple[str, float, Dict[str, float]]]:
    """
    Собирает данные из всех финальных отчетов.
    Возвращает список кортежей (дата, HPI, {оценки_сфер}).
    """
    all_data = []
    try:
        if not os.path.exists(FINAL_FOLDER):
            print("Папка с финальными отчетами не найдена.")
            return []

        report_files = [f for f in os.listdir(FINAL_FOLDER) if f.startswith("HPI_Final_Report_") and f.endswith(".md")]
        
        for filename in report_files:
            try:
                # Извлекаем дату из имени файла
                date_str = filename.replace("HPI_Final_Report_", "").replace(".md", "")
                report_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Читаем файл и парсим оценки
                filepath = os.path.join(FINAL_FOLDER, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                hpi_match = re.search(r"Итоговый HPI\*\* \| \*\*([\d\.]+)\*\*", content)
                hpi_score = float(hpi_match.group(1)) if hpi_match else 0.0
                
                sphere_scores = {}
                for sphere in SPHERE_CONFIG:
                    # Ищем оценку для каждой сферы
                    pattern = rf"\| {re.escape(sphere['name'])} \| ([\d\.]+) \|"
                    match = re.search(pattern, content)
                    if match:
                        sphere_scores[sphere['name']] = float(match.group(1))
                
                all_data.append((report_date, hpi_score, sphere_scores))
            except Exception as e:
                print(f"Ошибка при обработке отчета {filename}: {e}")
                continue

    except Exception as e:
        print(f"Общая ошибка при сборе данных отчетов: {e}")

    # Сортируем данные по дате
    all_data.sort(key=lambda x: x[0])
    return all_data

def update_dashboard(scores: Dict[str, float], draft_path: str) -> None:
    """Обновляет dashboard.md актуальными данными."""
    try:
        dashboard_path = os.path.join(INTERFACES_FOLDER, "dashboard.md")
        images_folder = os.path.join(FINAL_FOLDER, "images")
        os.makedirs(images_folder, exist_ok=True)
        
        radar_dashboard_path = os.path.join(images_folder, "latest_radar.png")

        try:
            create_radar_chart(scores, radar_dashboard_path, is_dashboard=True)
            print(f"Радарная диаграмма для дашборда обновлена: {radar_dashboard_path}")
        except Exception as e:
            print(f"Ошибка при генерации радарной диаграммы для дашборда: {str(e)}")

        with open(draft_path, 'r', encoding='utf-8') as f:
            draft_content = f.read()
        
        all_reports_data = collect_all_reports_data()
        
        history_table = ""
        for date, hpi, _ in all_reports_data:
            emoji = get_score_emoji(hpi, is_hpi=True)
            history_table += f"| {date} | {hpi:.1f} | {emoji} |\n"

        emojis = [s['emoji'] for s in SPHERE_CONFIG]
        detailed_table = "| Дата | " + " | ".join(emojis) + " |\n"
        detailed_table += "|------|" + "------|" * 8 + "\n"
        for date, hpi, sphere_scores in all_reports_data:
            row = f"| {date} "
            for i in range(1, 9):
                val = sphere_scores.get(str(i), "-")
                if isinstance(val, float):
                    row += f"| {val:.1f} {get_score_emoji(val)} "
                else:
                    row += f"| {val} "
            row += "|\n"
            detailed_table += row

        sub_map = [
            ('Мои проблемы', '🛑'),
            ('Мои цели', '🎯'),
            ('Мои блокеры', '🚧'),
            ('Мои метрики', '📊'),
            ('Мои достижения', '🏆')
        ]
        dashboard_content = f"""# HPI

> [!tip]- 📊 Мой HPI {scores["HPI"]:.1f} {get_score_emoji(scores["HPI"], is_hpi=True)}
> 
> ## Динамика HPI
> ![hpi trend](../reports_final/images/latest_trend.png)
> 
> ## История измерений
> | Дата | HPI | Тренд |
> |------|-----|--------|
{history_table}

> [!tip]- ⚖️ HPI баланс
> 
> ![radar chart](../reports_final/images/latest_radar.png)
> 
> ## История по сферам
{detailed_table}

# HPI PRO

"""
        for sub, emoji in sub_map:
            if sub == 'Мои метрики':
                dashboard_content += f"\n> [!info]- {emoji} {sub}\n>\n> | Сфера | Метрика | Текущее | Целевое |\n> |:------:|---------|---------|---------|\n"
                section_pat = rf"###\s*[\d\.]+\s*.*?\s*{re.escape(sub)}.*?(\n\|[\s\S]*?)(?=\n###|\n##|\n#|\Z)"
                section_match = re.search(section_pat, draft_content, re.DOTALL | re.IGNORECASE)
                section_text = section_match.group(1) if section_match else ""
                
                table_lines = [line for line in section_text.splitlines() if line.strip().startswith('|')]
                
                rows_by_sphere = {s['name']: [] for s in SPHERE_CONFIG}
                for line in table_lines:
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if len(cells) < 4 or any(x in cells[0] for x in ['Сфера', ':---']):
                        continue
                    
                    sphere_identifier = cells[0]
                    sphere_key = EMOJI_TO_SPHERE_NAME.get(sphere_identifier, sphere_identifier)
                    sphere_key = SPHERE_SYNONYMS.get(sphere_key, sphere_key)

                    if sphere_key in rows_by_sphere:
                        rows_by_sphere[sphere_key].append(cells)

                for sphere in SPHERE_CONFIG:
                    rows = rows_by_sphere[sphere['name']]
                    if rows:
                        for cells in rows:
                            dashboard_content += f"> | {' ' + sphere['emoji'] + ' '} | {cells[1]} | {cells[2]} | {cells[3]} |\n"
                    else:
                        dashboard_content += f"> | {' ' + sphere['emoji'] + ' '} | Нет данных | | |\n"
            else:
                dashboard_content += f"\n> [!info]- {emoji} {sub}\n>\n> | Сфера | Ваши ответы |\n> |:------:|-------------|\n"
                section_pat = rf"###\s*[\d\.]+\s*.*?\s*{re.escape(sub)}.*?(\n\|[\s\S]*?)(?=\n###|\n##|\n#|\Z)"
                section_match = re.search(section_pat, draft_content, re.DOTALL | re.IGNORECASE)
                section_text = section_match.group(1) if section_match else ""
                table_lines = [line for line in section_text.splitlines() if line.strip().startswith('|')]
                answers = {}
                for line in table_lines:
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if len(cells) >= 2 and not any(x in cells[0] for x in ['Сфера', ':---']):
                        sphere_identifier = cells[0]
                        sphere_key = EMOJI_TO_SPHERE_NAME.get(sphere_identifier, sphere_identifier)
                        sphere_key = SPHERE_SYNONYMS.get(sphere_key, sphere_key)
                        answers[sphere_key] = cells[1]

                for sphere in SPHERE_CONFIG:
                    value = answers.get(sphere['name'], 'Нет данных')
                    dashboard_content += f"> | {' ' + sphere['emoji'] + ' '} | {value} |\n"
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
            
        print(f"Дашборд обновлен: {dashboard_path}")
        
        try:
            import subprocess
            trend_script = os.path.join(os.path.dirname(__file__), "trend.py")
            subprocess.run([sys.executable, trend_script], check=True)
            print("График тренда обновлен")
        except Exception as e:
            print(f"Ошибка при обновлении графика тренда: {str(e)}")
        
    except Exception as e:
        print(f"Ошибка при обновлении дашборда: {str(e)}")

def print_scores(scores):
    """Выводит рассчитанные показатели в консоль."""
    print(f"HPI: {scores['HPI']:.1f} {get_score_emoji(scores['HPI'])}")
    for sphere in SPHERE_CONFIG:
        sphere_num = sphere["number"]
        print(f"{sphere['emoji']} {sphere['name']}: {scores[sphere_num]:.1f} {get_score_emoji(scores[sphere_num])}")

def run_calculator():
    """Основная функция для запуска калькулятора."""
    try:
        draft_path = find_latest_draft()
        if not draft_path:
            print("Черновики для обработки не найдены.")
            return

        print(f"Найден последний черновик: {draft_path}")
        
        scores = process_hpi_report(draft_path)
        print_scores(scores)
        
        create_final_report(draft_path, scores)

        # Отключаем прямое обновление дашборда из калькулятора.
        # За это теперь отвечает ai_dashboard_injector.py
        # update_dashboard(scores, draft_path)

        from trend import update_trend_chart
        if update_trend_chart():
            print("График тренда обновлен")
        else:
            print("Не удалось обновить график тренда.")

    except Exception as e:
        print(f"Произошла ошибка в работе калькулятора: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_calculator() 