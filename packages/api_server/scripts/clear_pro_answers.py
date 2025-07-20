import argparse
import logging
import os
import sys
import importlib
from sqlalchemy.orm import Session

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Динамический импорт
database = importlib.import_module("api-server.database")
models = importlib.import_module("api-server.models")
SessionLocal = database.SessionLocal

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_pro_user_data(db: Session, user_id: int):
    """
    Удаляет все данные Pro-диагностики для указанного пользователя.
    """
    logging.info(f"Начинаем удаление Pro-данных для пользователя с ID: {user_id}")

    models_to_clear = [
        models.Problem,
        models.Goal,
        models.Blocker,
        models.Achievement,
        models.Metric
    ]

    total_deleted = 0
    for model in models_to_clear:
        table_name = model.__tablename__
        try:
            # Используем .user_id для фильтрации
            deleted_rows = db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
            logging.info(f"Удалено {deleted_rows} записей из таблицы '{table_name}'.")
            total_deleted += deleted_rows
        except Exception as e:
            logging.error(f"Ошибка при удалении данных из таблицы '{table_name}': {e}")

    db.commit()
    logging.info(f"Операция завершена. Всего удалено {total_deleted} записей Pro-ответов для пользователя ID {user_id}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Удаление всех данных Pro-диагностики для конкретного пользователя.")
    parser.add_argument("user_id", type=int, help="ID пользователя, чьи данные нужно удалить.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        clear_pro_user_data(db, args.user_id)
    finally:
        db.close() 