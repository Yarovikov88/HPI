#!/usr/bin/env python3
"""
Скрипт для проверки структуры таблицы problems
"""

import asyncio
from sqlalchemy import text
from app.db import engine

async def check_table_structure():
    """Проверяет структуру таблицы problems"""
    try:
        async with engine.begin() as conn:
            print("🔍 Проверка структуры таблицы problems...")
            
            # Получаем информацию о колонках
            result = await conn.execute(text("PRAGMA table_info(problems)"))
            columns = result.fetchall()
            
            print("📋 Колонки в таблице problems:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure()) 