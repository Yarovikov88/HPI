#!/usr/bin/env python3
"""
Скрипт для создания таблиц в базе данных HPI
"""

import asyncio
import sys
import os
from sqlalchemy import text
from app.db import engine, Base
from app.models import User, Answer, Problem, Goal, Blocker, Metric, Achievement, AIRecommendation

async def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            print(f"✅ Подключение к SQLite успешно: {version}")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

async def create_tables():
    """Создает все таблицы"""
    try:
        async with engine.begin() as conn:
            print("🔨 Создаю таблицы...")
            
            # Создаем все таблицы из моделей
            await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Все таблицы созданы успешно!")
            return True
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False

async def verify_tables():
    """Проверяет, что таблицы созданы"""
    try:
        async with engine.begin() as conn:
            # Проверяем основные таблицы
            tables = ['users', 'answers', 'problems', 'goals', 'blockers', 'metrics', 'achievements', 'ai_recommendations']
            
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📊 Таблица {table}: {count} записей")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка проверки таблиц: {e}")
        return False

async def main():
    """Основная функция"""
    print("🚀 Запуск скрипта создания таблиц...")
    
    # Проверяем подключение
    if not await test_connection():
        print("❌ Не удалось подключиться к базе данных")
        sys.exit(1)
    
    # Создаем таблицы
    if not await create_tables():
        print("❌ Не удалось создать таблицы")
        sys.exit(1)
    
    # Проверяем результат
    if not await verify_tables():
        print("❌ Ошибка при проверке таблиц")
        sys.exit(1)
    
    print("🎉 Все таблицы созданы и проверены успешно!")

if __name__ == "__main__":
    asyncio.run(main()) 