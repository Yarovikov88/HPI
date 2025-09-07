#!/usr/bin/env python3
"""
Скрипт для проверки содержимого базы данных
"""

import asyncio
from sqlalchemy import text
from app.db import engine

async def check_database():
    """Проверяет содержимое базы данных"""
    try:
        async with engine.begin() as conn:
            print("📊 Проверка базы данных...")
            
            # Проверяем таблицы
            tables = ['users', 'questions', 'problems', 'answers', 'goals', 'blockers', 'metrics', 'achievements', 'ai_recommendations']
            
            for table in tables:
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"📋 Таблица {table}: {count} записей")
                except Exception as e:
                    print(f"❌ Ошибка при проверке таблицы {table}: {e}")
            
            # Проверяем вопросы по сферам
            try:
                result = await conn.execute(text("SELECT sphere, type, COUNT(*) FROM questions GROUP BY sphere, type"))
                spheres = result.fetchall()
                print("\n📝 Вопросы по сферам:")
                for sphere, q_type, count in spheres:
                    print(f"  - {sphere} ({q_type}): {count} вопросов")
            except Exception as e:
                print(f"❌ Ошибка при проверке сфер: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")

if __name__ == "__main__":
    asyncio.run(check_database()) 