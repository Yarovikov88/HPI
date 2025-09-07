# src/telegram_bot_multi/db.py
# Универсальный модуль работы с БД для мультиязычного Telegram-бота HPI

import os
import json
# import psycopg2  # Временно отключено из-за проблем с асинхронностью
# from psycopg2.extras import RealDictCursor  # Временно отключено из-за проблем с асинхронностью
from dotenv import load_dotenv

load_dotenv()

# def get_connection():
#     """Создает соединение с PostgreSQL"""
#     # Сначала пробуем использовать DATABASE_URL
#     database_url = os.getenv('DATABASE_URL')
#     if database_url:
#         return psycopg2.connect(database_url)
#     
#     # Если DATABASE_URL нет, используем отдельные параметры
#     return psycopg2.connect(
#         host=os.getenv('DB_HOST', 'localhost'),
#         database=os.getenv('DB_NAME', 'hpi_db'),
#         user=os.getenv('DB_USER', 'postgres'),
#         password=os.getenv('DB_PASSWORD', ''),
#         port=os.getenv('DB_PORT', '5432')
#     )

# def get_user_id_by_telegram_id(telegram_id):
#     """Получает ID пользователя по Telegram ID"""
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
#     result = cur.fetchone()
#     cur.close()
#     conn.close()
#     if result and len(result) > 0:
#         return result[0]
#     return None

# def save_user(telegram_id, username=None, first_name=None, last_name=None):
#     """Сохраняет пользователя в БД"""
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (%s, %s, %s, %s) ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username, first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name RETURNING user_id",
#         (telegram_id, username, first_name, last_name)
#     )
#     result = cur.fetchone()
#     if result and len(result) > 0:
#         user_id = result[0]
#     else:
#         user_id = None
#     conn.commit()
#     cur.close()
#     conn.close()
#     return user_id

# Все функции временно отключены из-за проблем с psycopg2
# Используйте db_async.py для асинхронных версий

def save_answer(user_id, sphere, question_id, answer):
    """Заглушка - используйте db_async.save_answer"""
    pass

def get_user_answers(user_id):
    """Заглушка - используйте db_async.get_user_answers"""
    return []

def save_problem(user_id, sphere, description, status, severity, date_noticed):
    """Заглушка - используйте db_async.save_problem"""
    pass

def save_goal(user_id, sphere, description, target_date, priority, status):
    """Заглушка - используйте db_async.save_goal"""
    pass

def save_blocker(user_id, sphere, description, impact_level, status, resolution_plan):
    """Заглушка - используйте db_async.save_blocker"""
    pass

def save_metric(user_id, sphere, metric_name, current_value, target_value, metric_type):
    """Заглушка - используйте db_async.save_metric"""
    pass

def save_achievement(user_id, sphere, description, impact_areas, date_achieved):
    """Заглушка - используйте db_async.save_achievement"""
    pass

def get_user_problems(user_id):
    """Заглушка - используйте db_async.get_user_problems"""
    return []

def get_user_goals(user_id):
    """Заглушка - используйте db_async.get_user_goals"""
    return []

def get_user_blockers(user_id):
    """Заглушка - используйте db_async.get_user_blockers"""
    return []

def get_user_metrics(user_id):
    """Заглушка - используйте db_async.get_user_metrics"""
    return []

def get_user_achievements(user_id):
    """Заглушка - используйте db_async.get_user_achievements"""
    return []

def get_hpi_history(user_id):
    """Заглушка - используйте db_async.get_hpi_history"""
    return []

def save_hpi_history(user_id, hpi_value, scores=None):
    """Заглушка - используйте db_async.save_hpi_history"""
    pass 