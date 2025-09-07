#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных HPI
Создает все необходимые таблицы и индексы
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, BigInteger, Date, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy import text as sa_text

# Настройка базы данных
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./hpi_local.db"  # Локальная SQLite для разработки
)

# Убеждаемся, что используется правильный драйвер
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("sqlite://"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Создаем движок
if "sqlite" in DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
    )

Base = declarative_base()

# Модели таблиц
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    avatar_url = Column(Text, nullable=True)
    hashed_password = Column(String, nullable=True)
    has_password = Column(Boolean, default=False, nullable=False)
    is_pro = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, index=True)
    sphere = Column(String)
    type = Column(String)
    text = Column(Text)
    options = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    inverse = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    fields = Column(JSON, nullable=True)
    language = Column(String, default='ru')

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    question_id = Column(String)
    answer = Column(String)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    text = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    text = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Blocker(Base):
    __tablename__ = "blockers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    text = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    name = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    description = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)
    text = Column(Text)
    recommendation_id = Column(String, nullable=True)
    type = Column(String, nullable=True)
    priority = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

async def create_tables_and_indexes():
    """Создает все таблицы и индексы"""
    print("🚀 Инициализация базы данных HPI...")
    
    try:
        # Создаем таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы успешно!")
        
        # Создаем индексы
        async with engine.begin() as conn:
            # Индексы для таблицы answers
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_answers_user_date ON answers(user_id, date)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_answers_sphere_question ON answers(sphere, question_id)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_answers_user_sphere_date ON answers(user_id, sphere, date)")
            )
            
            # Индексы для PRO таблиц
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_problems_user_date ON problems(user_id, date)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_goals_user_date ON goals(user_id, date)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_blockers_user_date ON blockers(user_id, date)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_metrics_user_date ON metrics(user_id, date)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_achievements_user_date ON achievements(user_id, date)")
            )
            
            # Индексы для пользователей
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            )
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_id)")
            )
            
            # Составные индексы
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_answers_composite ON answers(user_id, date, sphere)")
            )
        
        print("✅ Индексы созданы успешно!")
        print("🎉 База данных готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        import traceback
        print(f"📋 Полный traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(create_tables_and_indexes())
    if success:
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Инициализация завершена с ошибками!")
        exit(1) 