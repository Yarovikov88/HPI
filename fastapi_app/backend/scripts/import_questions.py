# import psycopg2  # Временно отключено из-за проблем с асинхронностью
import json
import re
import datetime
from src.telegram_bot_multi.db_async import save_hpi_history
import sys

# --- Параметры подключения к БД ---
DB_HOST = '83.147.192.188'
DB_PORT = 5433
DB_NAME = 'hpi_db'           # или твое имя базы
DB_USER = 'hpi_user'      # или твой пользователь
DB_PASSWORD = 'hpi_password_2024'  # твой пароль

# --- Путь к файлу с вопросами ---
QUESTIONS_MD = 'database/questions.md'
QUESTIONS_MD_EN = 'database/questions_en.md'

# --- Сопоставление эмодзи и ключа сферы ---
SPHERE_MAP = {
    '💖': 'love',
    '🏡': 'family',
    '🤝': 'friends',
    '💼': 'career',
    '♂️': 'physical',
    '🧠': 'mental',
    '🎨': 'hobby',
    '💰': 'wealth',
}

# --- Чтение и парсинг markdown ---
def extract_json_blocks(md_text):
    """
    Возвращает список кортежей (sphere_key, json_list) для каждой сферы.
    """
    results = []
    # Находим все заголовки сферы и следующий за ними JSON-блок
    pattern = re.compile(r'## (.*?)\n```json\n(.*?)```', re.DOTALL)
    for match in pattern.finditer(md_text):
        sphere_title = match.group(1).strip()
        json_block = match.group(2).strip()
        # Определяем ключ сферы по эмодзи
        emoji = sphere_title.split()[0]
        sphere_key = SPHERE_MAP.get(emoji, emoji)
        try:
            questions = json.loads(json_block)
        except Exception as e:
            print(f'Ошибка парсинга JSON для сферы {sphere_title}: {e}')
            continue
        results.append((sphere_key, questions))
    return results


# def main():
#     # Позволяем выбрать файл через аргумент
#     if len(sys.argv) > 1 and sys.argv[1] == 'en':
#         questions_file = QUESTIONS_MD_EN
#         table_name = 'questions_en'
#         print('Импорт английских вопросов из', questions_file)
#     else:
#         questions_file = QUESTIONS_MD
#         table_name = 'questions'
#         print('Импорт русских вопросов из', questions_file)
#     # Читаем файл
#     with open(questions_file, 'r', encoding='utf-8') as f:
#         md_text = f.read()
#     all_questions = extract_json_blocks(md_text)
# 
#     # Подключаемся к БД
#     conn = psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD
#     )
#     inserted = 0
#     for sphere_key, questions in all_questions:
#         for q in questions:
#             q_id = q.get('id', None)
#             if not q_id:
#                 continue  # пропускаем вопросы без id
#             q_type = q.get('type', None)
#             q_category = q.get('category', None)
#             q_text = q.get('text', None)
#             q_options = q.get('options', None)
#             q_scores = q.get('scores', None)
#             q_fields = q.get('fields', None)
#             q_metrics = q.get('metrics', None)
#             q_description = q.get('description', None)
#             q_inverse = q.get('inverse', False)
# 
#             # Преобразуем массивы для Postgres
#             options_pg = q_options if q_options else None
#             scores_pg = q_scores if q_scores else None
#             fields_pg = json.dumps(q_fields) if q_fields else None
#             metrics_pg = json.dumps(q_metrics) if q_metrics else None
# 
#             with conn.cursor() as cur:
#                 cur.execute(f'''
#                     INSERT INTO {table_name} (id, sphere, type, category, text, options, scores, fields, metrics, description, inverse)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     ON CONFLICT (id) DO NOTHING
#                 ''', (
#                     q_id,
#                     sphere_key,
#                     q_type,
#                     q_category,
#                     q_text,
#                     options_pg,
#                     scores_pg,
#                     fields_pg,
#                     metrics_pg,
#                     q_description,
#                     q_inverse
#                 ))
#                 inserted += 1
#         conn.commit()
#     conn.close()
#     print(f'Импортировано {inserted} вопросов!')

def main():
    print("Функция main() временно отключена из-за проблем с psycopg2")
    pass

async def fill_hpi_history_for_user1():
    user_id = 1
    # Примерные даты и значения HPI
    data = [
        (64.7, '2025-06-09 12:00:00'),
        (64.7, '2025-06-11 13:00:00'),
        (49.4, '2025-06-13 14:00:00'),
        (72.0, '2025-06-15 15:00:00'),
        (58.3, '2025-06-17 16:00:00'),
        (25.0, '2025-06-19 17:00:00'),
        (75.1, '2025-06-21 18:00:00'),
        (48.8, '2025-06-23 19:00:00'),
    ]
    for hpi, dt in data:
        await save_hpi_history(user_id, hpi, dt)
        print(f"Добавлено: user_id={user_id}, hpi={hpi}, date={dt}")

if __name__ == '__main__':
    import asyncio
    main()
    asyncio.run(fill_hpi_history_for_user1()) 