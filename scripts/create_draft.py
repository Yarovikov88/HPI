import os
import sys
from datetime import datetime

# Определение корня проекта
# __file__ -> scripts/create_draft.py
# os.path.dirname(...) -> scripts/
# os.path.dirname(...) -> hpi/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT_FOLDER = os.path.join(PROJECT_ROOT, "reports_draft")

# Шаблон вопросов для каждой сферы
QUESTION_TEMPLATE = """| Вопрос | Варианты | Ответ |
|:---|:---|:---:|
| 1. ... | 1-4 | |
| 2. ... | 1-4 | |
| 3. ... | 1-4 | |
| 4. ... | 1-4 | |
| 5. ... | 1-4 | |
| 6. ... | 1-4 | |
"""

# Шаблон для PRO-разделов
PRO_TEMPLATE = """| Сфера жизни | Ваши ответы |
|:---|:---|
| 💖 Отношения с любимыми | |
| 🏡 Отношения с родными | |
| 🤝 Друзья | |
| 💼 Карьера | |
| ♂️ Физическое здоровье | |
| 🧠 Ментальное здоровье | |
| 🎨 Хобби и увлечения | |
| 💰 Благосостояние | |
"""

# Шаблон для раздела "Мои метрики"
METRICS_TEMPLATE = """| Сфера жизни | Метрика | Текущее | Целевое |
|:---|:---|:---:|:---:|
| 💖 Отношения с любимыми | (пример: кол-во свиданий в неделю) | | |
| 🏡 Отношения с родными | (пример: кол-во звонков родителям) | | |
| 🤝 Друзья | (пример: кол-во встреч с друзьями) | | |
| 💼 Карьера | (пример: % выполнения плана) | | |
| ♂️ Физическое здоровье | (пример: среднее кол-во шагов в день) | | |
| 🧠 Ментальное здоровье | (пример: оценка уровня стресса 1-10) | | |
| 🎨 Хобби и увлечения | (пример: часов на хобби в неделю) | | |
| 💰 Благосостояние | (пример: % сбережений от дохода) | | |
"""

# Основной шаблон черновика
DRAFT_TEMPLATE = f"""
# HPI Отчет

> [!NOTE]
> Дата: {datetime.now().strftime('%Y-%m-%d')}
> Заполните все таблицы ниже. Для вопросов по сферам используйте шкалу от 1 до 4.

---

## 1. 💖 Отношения с любимыми
{QUESTION_TEMPLATE}
## 2. 🏡 Отношения с родными
{QUESTION_TEMPLATE}
## 3. 🤝 Друзья
{QUESTION_TEMPLATE}
## 4. 💼 Карьера
{QUESTION_TEMPLATE}
## 5. ♂️ Физическое здоровье
{QUESTION_TEMPLATE}
## 6. 🧠 Ментальное здоровье
{QUESTION_TEMPLATE}
## 7. 🎨 Хобби и увлечения
{QUESTION_TEMPLATE}
## 8. 💰 Благосостояние
{QUESTION_TEMPLATE}

---

# HPI PRO

### 1. 🛑 Мои проблемы
{PRO_TEMPLATE}
### 2. 🎯 Мои цели
{PRO_TEMPLATE}
### 3. 🚧 Мои блокеры
{PRO_TEMPLATE}
### 4. 📊 Мои метрики
{METRICS_TEMPLATE}
### 5. 🏆 Мои достижения
{PRO_TEMPLATE}
"""

def create_draft_report():
    """
    Создает файл черновика HPI на сегодняшнюю дату.
    """
    # Принудительно устанавливаем кодировку UTF-8
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except TypeError:
            pass

    os.makedirs(DRAFT_FOLDER, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    draft_filename = f"{today_str}_draft.md"
    draft_filepath = os.path.join(DRAFT_FOLDER, draft_filename)

    if os.path.exists(draft_filepath):
        print(f"🟡 Черновик на сегодня ({draft_filename}) уже существует.")
        print("Чтобы создать новый, удалите старый файл.")
        return

    try:
        with open(draft_filepath, 'w', encoding='utf-8') as f:
            f.write(DRAFT_TEMPLATE.strip())
        print(f"✅ Успешно создан черновик: {draft_filepath}")
        print("Пожалуйста, откройте файл и заполните его.")
    except Exception as e:
        print(f"🔴 Ошибка при создании черновика: {e}", file=sys.stderr)

if __name__ == "__main__":
    create_draft_report() 