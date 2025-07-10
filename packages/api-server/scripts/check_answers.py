import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer
from sqlalchemy.orm import sessionmaker

# --- Конфигурация ---
# URL для подключения к базе данных (скопировано из config.py)
DATABASE_URL = "postgresql://hpi_user:hpi_password_2024@83.147.192.188:5433/hpi_db"
ANSWERS_TABLE_NAME = 'answers'
USER_ID_TO_CHECK = 179

def check_user_answers():
    """
    Подключается к БД и считает количество ответов для заданного user_id.
    """
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print(f"Checking answers for user_id: {USER_ID_TO_CHECK}")
        
        metadata = MetaData()
        answers_table = Table(
            ANSWERS_TABLE_NAME, 
            metadata, 
            Column('user_id', Integer), # Указываем столбец для фильтрации
            autoload_with=engine
        )
        
        answer_count = db.query(answers_table).filter(answers_table.c.user_id == USER_ID_TO_CHECK).count()
        
        print(f"Found {answer_count} answer(s) for user_id {USER_ID_TO_CHECK}.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    check_user_answers() 