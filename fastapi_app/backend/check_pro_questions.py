#!/usr/bin/env python3
"""
Скрипт для проверки PRO вопросов в базе данных
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_pro_questions():
    try:
        async with engine.begin() as conn:
            # Проверяем PRO вопросы в базе
            result = await conn.execute(text("SELECT sphere, category, question_id, text FROM questions WHERE type = 'pro' AND language = 'ru' ORDER BY sphere, category"))
            rows = result.fetchall()
            
            print("🚀 PRO вопросы в базе данных:")
            for row in rows:
                print(f"  Сфера: {row[0]}, Категория: {row[1]}, ID: {row[2]}, Текст: {row[3][:50]}...")
            
            print(f"\n📊 Всего PRO вопросов: {len(rows)}")
            
            # Группируем по сферам
            spheres = {}
            for row in rows:
                sphere = row[0]
                if sphere not in spheres:
                    spheres[sphere] = {}
                category = row[1]
                if category not in spheres[sphere]:
                    spheres[sphere][category] = []
                spheres[sphere][category].append(row[2])
            
            print(f"\n📋 PRO вопросы по сферам:")
            for sphere, categories in spheres.items():
                print(f"  {sphere}:")
                for category, questions in categories.items():
                    print(f"    {category}: {len(questions)} вопросов - {questions}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_pro_questions()) 