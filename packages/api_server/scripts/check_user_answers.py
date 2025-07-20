import argparse
import logging
import os
import sys
import importlib
from sqlalchemy.orm import Session
from sqlalchemy import inspect

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Динамический импорт из-за дефиса в имени папки
database = importlib.import_module("api-server.database")
models = importlib.import_module("api-server.models")
SessionLocal = database.SessionLocal

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def object_as_dict(obj):
    """Преобразует объект SQLAlchemy в словарь."""
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def check_user_data(db: Session, user_id: int):
    """
    Читает и выводит все данные диагностики для указанного пользователя.
    """
    logging.info(f"--- Проверка данных для пользователя с ID: {user_id} ---")

    # Список моделей для проверки
    models_to_check = [
        models.Answer,
        models.Problem,
        models.Goal,
        models.Blocker,
        models.Achievement,
        models.Metric
    ]

    found_data = False
    for model in models_to_check:
        table_name = model.__tablename__
        try:
            results = db.query(model).filter(model.user_id == user_id).all()
            if results:
                found_data = True
                logging.info(f"\n[+] Найдены данные в таблице '{table_name}' ({len(results)} записей):")
                for result in results:
                    print(object_as_dict(result))
            else:
                logging.warning(f"\n[-] В таблице '{table_name}' данные для пользователя {user_id} не найдены.")
        except Exception as e:
            logging.error(f"Ошибка при чтении данных из таблицы '{table_name}': {e}")
    
    if not found_data:
        logging.info("\nНикаких данных для указанного пользователя не найдено.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Проверка всех данных диагностики для конкретного пользователя.")
    parser.add_argument("user_id", type=int, help="ID пользователя, чьи данные нужно проверить.")

    args = parser.parse_args()

    db = SessionLocal()
    try:
        check_user_data(db, args.user_id)
    finally:
        db.close() 