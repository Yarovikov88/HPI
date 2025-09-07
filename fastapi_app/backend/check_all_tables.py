#!/usr/bin/env python3
"""
Скрипт для проверки всех таблиц в базе данных
"""

import asyncio
from sqlalchemy import text
from app.db import engine

async def check_all_tables():
    """Проверяет все таблицы в базе данных"""
    try:
        async with engine.begin() as conn:
            print("🔍 Проверка всех таблиц в базе данных...")
            
            # Получаем список всех таблиц
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            
            print("📋 Все таблицы:")
            for table in tables:
                table_name = table[0]
                print(f"\n📊 Таблица: {table_name}")
                
                # Получаем структуру каждой таблицы
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = result.fetchall()
                
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # Получаем количество записей
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"  📈 Записей: {count}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_all_tables()) 