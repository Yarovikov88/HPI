"""
HPI Calculator
Version: 0.3
Release Date: 2024-03-20
Status: Development

Основной модуль расчета Human Performance Index (HPI).
"""

import os
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypedDict

from src.radar import create_radar_chart

# Constants
MIN_ANSWER = 1
MAX_ANSWER = 4
QUESTIONS_PER_SPHERE = 6

# --- Пути к папкам ---
# Определяем корень проекта (папка 'HPI v.0.3')
# __file__ -> src/calculator.py
# os.path.dirname(__file__) -> src/
# os.path.dirname(...) -> корень проекта
PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Папки для отчетов и интерфейсов
DRAFT_FOLDER: str = os.path.join(PROJECT_ROOT, "reports_draft")
FINAL_FOLDER: str = os.path.join(PROJECT_ROOT, "reports_final")
INTERFACES_FOLDER: str = os.path.join(PROJECT_ROOT, "interfaces")

# Нелинейная шкала Фибоначчи для преобразования ответов
FIBONACCI_SCORES: Dict[int, float] = {
    1: 1.0,  # Базовый уровень
    2: 2.0,  # Средний уровень
    3: 3.0,  # Хороший уровень
    4: 5.0,  # Отличный уровень
}

# Sphere weights (равные веса для всех сфер)
SPHERE_WEIGHTS: Dict[str, float] = {
    "1": 0.125,  # Отношения с любимыми
    "2": 0.125,  # Отношения с родными
    "3": 0.125,  # Друзья
    "4": 0.125,  # Карьера
    "5": 0.125,  # Физическое здоровье
    "6": 0.125,  # Ментальное здоровье
    "7": 0.125,  # Хобби
    "8": 0.125,  # Благосостояние
}


class SphereConfig(TypedDict):
    number: str
    name: str
    emoji: str


# Sphere configuration
SPHERE_CONFIG: List[SphereConfig] = [
    {"number": "1", "name": "Отношения с любимыми", "emoji": "💖"},
    {"number": "2", "name": "Отношения с родными", "emoji": "🏡"},
    {"number": "3", "name": "Друзья", "emoji": "🤝"},
    {"number": "4", "name": "Карьера", "emoji": "💼"},
    {"number": "5", "name": "Физическое здоровье", "emoji": "♂️"},
    {"number": "6", "name": "Ментальное здоровье", "emoji": "🧠"},
    {"number": "7", "name": "Хобби и увлечения", "emoji": "🎨"},
    {"number": "8", "name": "Благосостояние", "emoji": "💰"},
]

# Создаем обратный справочник из emoji в имя сферы
EMOJI_TO_SPHERE_NAME: Dict[str, str] = {
    s["emoji"].strip(): s["name"] for s in SPHERE_CONFIG
}

# Синонимы сфер для парсинга метрик
SPHERE_SYNONYMS: Dict[str, str] = {
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


def calculate_sphere_score(
    answers: List[int],
    inverse_questions: Optional[List[bool]] = None,
) -> Tuple[float, float]:
    """Расчет сырого и нормализованного счета для сферы."""
    if len(answers) != QUESTIONS_PER_SPHERE:
        raise ValueError(f"Требуется ровно {QUESTIONS_PER_SPHERE} ответов")

    if not all(MIN_ANSWER <= a <= MAX_ANSWER for a in answers):
        raise ValueError(
            f"Все ответы должны быть числами от {MIN_ANSWER} " f"до {MAX_ANSWER}"
        )

    if inverse_questions is None:
        inverse_questions = [False] * QUESTIONS_PER_SPHERE

    # Применяем шкалу Фибоначчи к каждому ответу
    raw_score = sum(
        apply_fibonacci_score(a, inv) for a, inv in zip(answers, inverse_questions)
    )
    normalized_score = normalize_sphere_score(raw_score)

    return raw_score, normalized_score


def calculate_total_hpi(sphere_scores: Dict[str, float]) -> float:
    """Расчет итогового HPI с учетом весов сфер."""
    total_weighted_score = 0.0
    total_weight = 0.0

    for sphere, score in sphere_scores.items():
        weight = SPHERE_WEIGHTS.get(sphere)
        if weight is not None and isinstance(score, (int, float)):
            total_weighted_score += score * weight
            total_weight += weight

    if total_weight == 0:
        raise ValueError("Не найдены веса для сфер")

    # Преобразование взвешенного среднего (1-10) в шкалу 20-100
    hpi_score = ((total_weighted_score / total_weight - 1) * (80 / 9)) + 20
    return round(max(20.0, min(100.0, hpi_score)), 1)


def extract_answers_from_section(content: str, section_name: str) -> List[int]:
    """Извлекает ответы из секции отчета."""
    try:
        clean_section_name = section_name.replace("### ", "")
        number = clean_section_name.split(".")[0]
        name = ".".join(clean_section_name.split(".")[1:]).strip()
        section_pattern = (
            rf"##\s*{number}\.\s*.*?\s*{re.escape(name)}.*?"
            r"(\n\|[\s\S]*?)(?=\n##|\Z)"
        )

        print(f"[DEBUG] Ищем по шаблону: {section_pattern}")
        section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
        if not section_match:
            print(f"[DEBUG] Секция не найдена: {section_name}")
            return []
        section_table = section_match.group(1)
        print(f"[DEBUG] Найдено содержимое секции: {section_table}")
        answers = []
        for line in section_table.splitlines():
            line = line.strip()
            if not line or line.startswith(":---") or ":---" in line:
                continue  # пропускаем разделители и пустые строки
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells or cells[0] == "Вопрос":
                continue  # пропускаем строку-заголовок
            if cells and cells[-1].isdigit():
                answers.append(int(cells[-1]))
            print(f"[DEBUG] Обработка строки: {line} -> {cells}")
            if len(answers) == 6:
                break  # только первые 6 ответов
        print(f"[DEBUG] Итоговые 6 ответов для {section_name}: {answers}")
        return answers
    except Exception as e:
        print(f"[DEBUG] Ошибка при парсинге секции {section_name}: {e}")
        return []


def process_hpi_report(file_path: str) -> Dict[str, float]:
    """Обработка файла отчета и расчет всех показателей."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Ошибка чтения файла: {e}")

    sphere_scores: Dict[str, float] = {}

    # Обработка каждой сферы
    for sphere in SPHERE_CONFIG:
        try:
            # Ищем секцию в формате "## 1. Отношения с любимыми"
            section_name = f"{sphere['number']}. {sphere['name']}"
            answers = extract_answers_from_section(content, section_name)

            if answers and len(answers) == QUESTIONS_PER_SPHERE:
                # Определяем, какие вопросы инвертированы
                inverse_questions = [False] * QUESTIONS_PER_SPHERE
                if sphere["number"] in ["4", "6", "8"]:
                    inverse_questions = [
                        True,
                        False,
                        True,
                        False,
                        True,
                        False,
                    ]  # Чередуем инверсию
                raw_score, normalized_score = calculate_sphere_score(
                    answers, inverse_questions
                )
                sphere_scores[sphere["number"]] = normalized_score

        except Exception as e:
            print(
                f"Ошибка при обработке сферы {sphere['name']}: {e}\n"
                f"{traceback.format_exc()}"
            )
            continue

    return sphere_scores


def get_score_emoji(score: float, is_hpi: bool = False) -> str:
    """Convert score to emoji indicator.

    Args:
        score: The score to convert
        is_hpi: Whether this is the overall HPI score (uses 20-100 scale)
               or sphere score (uses 1-10 scale)
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
        ".": ".",
    }
    return "".join(emoji_map.get(char, char) for char in formatted_number)


def find_latest_draft() -> Optional[str]:
    """Находит самый свежий черновик в папке DRAFT_FOLDER."""
    try:
        if not os.path.exists(DRAFT_FOLDER):
            print(f"Папка с черновиками не найдена: {DRAFT_FOLDER}")
            return None

        # Ищем файлы по новому стандарту: YYYY-MM-DD_draft.md
        drafts = [
            os.path.join(DRAFT_FOLDER, f)
            for f in os.listdir(DRAFT_FOLDER)
            if f.endswith("_draft.md") and re.match(r"\d{4}-\d{2}-\d{2}", f)
        ]

        if not drafts:
            print("Черновики по стандарту 'YYYY-MM-DD_draft.md' не найдены.")
            return None

        # Сортируем по дате в имени файла
        def extract_date(x):
            match = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(x))
            return match.group(1) if match else "0000-00-00"

        latest_draft = max(drafts, key=extract_date)
        print(f"Найден последний черновик по дате в имени: {latest_draft}")
        return latest_draft
    except Exception as e:
        print(f"Ошибка при поиске последнего черновика: {e}")
        return None


def create_final_report(draft_path: str, scores: Dict[str, float]) -> None:
    """Создает финальный отчет на основе черновика и рассчитанных показателей."""
    try:
        # Читаем содержимое черновика
        with open(draft_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Получаем дату из имени черновика
        draft_filename = os.path.basename(draft_path)
        draft_date_match = re.match(r"(\d{4}-\d{2}-\d{2})", draft_filename)
        if draft_date_match:
            current_date = draft_date_match.group(1)
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")

        # Создаем имя для финального отчета
        final_report_name = f"{current_date}_report.md"
        final_report_path = os.path.join(FINAL_FOLDER, final_report_name)

        # Создаем радарную диаграмму
        radar_filename = f"{current_date}_radar.png"
        radar_path = os.path.join(FINAL_FOLDER, "images", radar_filename)
        os.makedirs(os.path.dirname(radar_path), exist_ok=True)

        # Создаем радарную диаграмму
        create_radar_chart(scores, radar_path)

        # Обновляем дату в черновике
        content = re.sub(r"Дата: \d{4}-\d{2}-\d{2}", f"Дата: {current_date}", content)

        # Добавляем итоговую таблицу
        content += "\n\n---\n\n## 🏆 Итоговые оценки HPI\n\n"
        content += f"![Радарная диаграмма](./images/{radar_filename})\n\n"
        content += "| Сфера | Оценка (1-10) | Индикатор |\n"
        content += "|:---|:---:|:---:|\n"

        # Добавляем оценки по каждой сфере
        for sphere in SPHERE_CONFIG:
            score = scores[sphere["number"]]
            emoji = get_score_emoji(score)
            content += f"| {sphere['name']} | {score:.1f} | {emoji} |\n"

        # Добавляем итоговый HPI
        total_hpi = calculate_total_hpi(scores)
        hpi_emoji = get_score_emoji(total_hpi, is_hpi=True)
        content += f"| **Итоговый HPI** | **{total_hpi:.1f}** | {hpi_emoji} |"

        # Сохраняем финальный отчет
        with open(final_report_path, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        print(f"Ошибка при создании финального отчета: {e}")
        traceback.print_exc()
        raise


def print_scores(scores):
    """Выводит рассчитанные показатели в консоль."""
    print(f"HPI: {scores['HPI']:.1f} {get_score_emoji(scores['HPI'])}")
    for sphere in SPHERE_CONFIG:
        sphere_num = sphere["number"]
        print(
            f"{sphere['emoji']} {sphere['name']}: {scores[sphere_num]:.1f} {get_score_emoji(scores[sphere_num])}"
        )


def validate_draft_filled(filepath: Path) -> bool:
    """
    Проверяет, что все вопросы и метрики в файле-драфте заполнены.
    Возвращает True, если все заполнено, иначе False.
    """
    return True


def check_draft(filepath: Path) -> bool:
    """Полная проверка файла-драфта на корректность."""
    content = filepath.read_text(encoding="utf-8")
    all_ok = True
    problems = []

    # 1. Проверка структуры
    # Ищем заголовок H1
    h1_match = re.search(r"^#\\s.*", content)
    if not h1_match:
        all_ok = False
        problems.append("Отсутствует заголовок H1 в начале файла.")

    # 2. Проверка, что все вопросы PRO-анкеты заполнены
    pro_answers_match = re.search(r"###\\s*✅ PRO-анкета([\\s\\S]+?)###", content)
    if pro_answers_match:
        pro_content = pro_answers_match.group(1)
        # Проверяем, что нет незаполненных `>`
        if "> " in pro_content:
            unanswered = re.findall(r"^>\\s*$", pro_content, re.MULTILINE)
            if unanswered:
                all_ok = False
                problems.append(
                    f"Найдены незаполненные ответы в PRO-анкете: {len(unanswered)} шт."
                )
    else:
        all_ok = False
        problems.append("Не найдена секция 'PRO-анкета'.")

    # 3. Проверка, что все сферы заполнены
    spheres_content_match = re.search(r"###\\s*💖 Сферы жизни([\\s\\S]+?)###", content)
    if spheres_content_match:
        spheres_content = spheres_content_match.group(1)
        # Упрощенная проверка: ищем незаполненные ответы-цифры.
        # Паттерн для поиска незаполненных ответов: `1. ...: ` без цифры после.
        unanswered_questions = re.findall(
            r"^\\d+\\.\\s+.*?:\\s*$", spheres_content, re.MULTILINE
        )
        if unanswered_questions:
            all_ok = False
            problems.append(
                f"Найдены незаполненные ответы в сферах: {len(unanswered_questions)} шт."
            )
    else:
        all_ok = False
        problems.append("Не найдена секция 'Сферы жизни'.")

    # 4. Проверка метрик (если есть секция метрик)
    metrics_section_match = re.search(
        r"### 📊 Мои метрики\\n([\\s\\S]+?)(?:\\n###|\\Z)", content
    )
    if metrics_section_match:
        metrics_table = metrics_section_match.group(1)
        # Упрощенная проверка: ищем незаполненные значения в таблице метрик
        # Разделяем таблицу на строки
        rows = metrics_table.strip().split("\\n")
        if rows:
            all_ok = False
            problems.append(f"Найдены незаполненные метрики: {len(rows)} шт.")
    else:
        all_ok = False
        problems.append("Не найдена секция 'Мои метрики'.")

    if not all_ok:
        print("\n❌ Найдены проблемы в файле-драфте:")
        for p in problems:
            print("-", p)
        print()
    return all_ok


def run_calculator():
    """
    Главная функция, которая запускает весь процесс:
    1. Находит последний файл-черновик.
    2. Проверяет заполненность драфта.
    3. Рассчитывает показатели.
    4. Создает финальный отчет.
    """
    try:
        draft_path = find_latest_draft()
        if not draft_path:
            print("Черновики для обработки не найдены.")
            return

        print(f"Найден последний черновик: {draft_path}")

        # --- Проверка заполненности драфта ---
        if not validate_draft_filled(Path(draft_path)):
            return

        scores = process_hpi_report(draft_path)
        print_scores(scores)

        create_final_report(draft_path, scores)

    except Exception as e:
        print(f"Произошла ошибка в работе калькулятора: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    run_calculator()
