#!/usr/bin/env python3
"""
Скрипт для проверки сферы 1
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_sphere_1():
    try:
        async with engine.begin() as conn:
            # Проверяем все сферы
            result = await conn.execute(text("SELECT sphere, COUNT(*) FROM questions WHERE type = 'basic' AND language = 'ru' GROUP BY sphere ORDER BY sphere"))
            rows = result.fetchall()
            
            print("📊 Вопросы по сферам:")
            for row in rows:
                print(f"  Сфера {row[0]}: {row[1]} вопросов")
            
            # Проверяем конкретно сферу 1
            result = await conn.execute(text("SELECT * FROM questions WHERE type = 'basic' AND language = 'ru' AND sphere = 'love' LIMIT 3"))
            sphere_1_questions = result.fetchall()
            
            print(f"\n🔍 Сфера 1 (love) - найдено {len(sphere_1_questions)} вопросов:")
            for i, q in enumerate(sphere_1_questions, 1):
                print(f"  {i}. ID: {q.question_id}, Текст: {q.text[:50]}...")
                
            # Проверяем, есть ли сфера 1 в базе
            result = await conn.execute(text("SELECT DISTINCT sphere FROM questions WHERE type = 'basic' AND language = 'ru' ORDER BY sphere"))
            spheres = [row[0] for row in result.fetchall()]
            print(f"\n📋 Все сферы в базе: {spheres}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_sphere_1()) 