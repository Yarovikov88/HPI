import sys
import os
import logging
from sqlalchemy import create_engine, inspect

# Настройка пути для импорта 'config'
# Это гарантирует, что мы можем запустить скрипт из корневой папки проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    from config import DATABASE_URL
except ImportError:
    print(f"Ошибка: Не удалось импортировать DATABASE_URL из config.py.")
    print(f"Убедитесь, что файл 'config.py' существует в папке '{src_path}'.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def discover_schema():
    """Подключается к базе данных и выводит ее схему."""
    if not DATABASE_URL:
        logger.error("Переменная DATABASE_URL не установлена в config.py.")
        return

    logger.info("Подключение к базе данных...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            logger.info("Соединение успешно установлено.")
            inspector = inspect(engine)
            
            # Получаем все схемы
            schemas = inspector.get_schema_names()
            logger.info(f"Доступные схемы: {schemas}")

            # Проходим по всем схемам, кроме системных
            for schema in schemas:
                if schema.startswith('pg_') or schema == 'information_schema':
                    continue
                
                print(f"\n--- Схема: {schema} ---")
                tables = inspector.get_table_names(schema=schema)
                
                if not tables:
                    print("  В этой схеме таблицы не найдены.")
                    continue

                for table_name in tables:
                    print(f"\n  [Таблица: {table_name}]")
                    
                    # Колонки
                    columns = inspector.get_columns(table_name, schema=schema)
                    for column in columns:
                        # Собираем информацию о колонке в одну строку
                        col_info = f"    - {column['name']} ({column['type']}"
                        if not column.get('nullable', True):
                            col_info += ", NOT NULL"
                        if column.get('primary_key'):
                            col_info += ", PRIMARY KEY"
                        if column.get('autoincrement'):
                            col_info += ", AUTOINCREMENT"
                        col_info += ")"
                        print(col_info)
                    
                    # Внешние ключи
                    fks = inspector.get_foreign_keys(table_name, schema=schema)
                    if fks:
                        print("    Внешние ключи:")
                        for fk in fks:
                            print(f"      - {fk['constrained_columns']} -> {fk['referred_schema']}.{fk['referred_table']}.{fk['referred_columns']}")

                    # Индексы
                    indexes = inspector.get_indexes(table_name, schema=schema)
                    if indexes:
                        print("    Индексы:")
                        for index in indexes:
                            print(f"      - {index['name']} (на колонках: {index['column_names']})")

    except Exception as e:
        logger.error(f"Произошла ошибка при подключении к базе данных: {e}", exc_info=True)

if __name__ == "__main__":
    discover_schema() 