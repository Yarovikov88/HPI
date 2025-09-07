from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text as sa_text
import os

# Оптимизированная конфигурация БД
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./hpi_local.db"  # Локальная SQLite для разработки
)

# Убеждаемся, что используется правильный драйвер
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("sqlite://"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Redis для кэширования
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Оптимизированный движок с connection pooling
if "sqlite" in DATABASE_URL:
    # Конфигурация для SQLite
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Отключаем логирование в продакшене
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
else:
    # Конфигурация для PostgreSQL
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Отключаем логирование в продакшене
        pool_size=20,  # Размер пула соединений
        max_overflow=30,  # Максимальное количество дополнительных соединений
        pool_pre_ping=True,  # Проверка соединений перед использованием
        pool_recycle=3600,  # Пересоздание соединений каждый час
        pool_timeout=30,  # Таймаут ожидания соединения
    )

# Оптимизированная сессия
SessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# Функция для создания индексов (выполняется при запуске)
async def create_indexes():
    """Создает необходимые индексы для оптимизации запросов"""
    try:
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
            
            # Составные индексы для сложных запросов
            await conn.execute(
                sa_text("CREATE INDEX IF NOT EXISTS idx_answers_composite ON answers(user_id, date, sphere)")
            )
    except Exception as e:
        print(f"⚠️ Ошибка создания индексов: {e}")
        # Для SQLite некоторые индексы могут уже существовать 