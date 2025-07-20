import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

# --- Конфигурация ---
# URL для подключения к базе данных (скопировано из config.py)
DATABASE_URL = "postgresql://hpi_user:hpi_password_2024@83.147.192.188:5433/hpi_db"
ANSWERS_TABLE_NAME = 'answers'

def clear_answers():
    """
    Подключается к БД и удаляет все записи из таблицы 'answers'.
    """
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print(f"Clearing all records from table: '{ANSWERS_TABLE_NAME}'")
        
        metadata = MetaData()
        answers_table = Table(ANSWERS_TABLE_NAME, metadata, autoload_with=engine)
        
        num_deleted = db.query(answers_table).delete()
        db.commit()
        
        print(f"Successfully deleted {num_deleted} rows.")
        
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        print("Rollback performed.")
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    clear_answers() 