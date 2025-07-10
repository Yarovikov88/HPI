import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import config

logger = logging.getLogger(__name__)

engine = create_engine(config.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Зависимость для получения сессии БД ---
def get_db():
    logger.info("--- Creating DB Session ---")
    db = SessionLocal()
    try:
        yield db
        logger.info("--- DB Session yielded successfully ---")
    finally:
        logger.info("--- Closing DB Session ---")
        db.close() 