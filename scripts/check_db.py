import sqlalchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Ошибка: Переменная окружения DATABASE_URL не установлена.")
    exit()

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    connection = engine.connect()
    print("✅ Успешное подключение к базе данных.")
except Exception as e:
    print(f"❌ Ошибка подключения к базе данных: {e}")
    exit()

def check_sphere(sphere_id):
    """Проверяет наличие базовых вопросов для указанной сферы."""
    print(f"\n--- Проверка сферы: {sphere_id} ---")
    
    # Ищем вопросы с непустым полем 'options'
    query = text("SELECT id, text, options FROM questions WHERE sphere_id = :sphere_id AND options IS NOT NULL AND jsonb_array_length(options) > 0")
    
    try:
        result = connection.execute(query, {'sphere_id': sphere_id})
        rows = result.fetchall()
        
        if not rows:
            print("❗ Базовые вопросы (с вариантами ответов) НЕ НАЙДЕНЫ.")
        else:
            print(f"✅ Найдено {len(rows)} базовых вопросов:")
            for row in rows:
                print(f"  - ID: {row[0]}, Текст: {row[1][:30]}...")
                
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса для сферы '{sphere_id}': {e}")


# --- Запускаем проверки ---
spheres_to_check = ['friends', 'physical', 'mental']
for sphere in spheres_to_check:
    check_sphere(sphere)

# --- Закрываем соединение ---
connection.close()
print("\n--- Проверка завершена. Соединение с БД закрыто. ---") 