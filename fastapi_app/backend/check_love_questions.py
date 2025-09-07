#!/usr/bin/env python3
"""
Скрипт для проверки всех вопросов сферы love
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_love_questions():
    try:
        async with engine.begin() as conn:
            # Проверяем все вопросы сферы love
            result = await conn.execute(text("SELECT question_id, text, type FROM questions WHERE sphere = 'love' AND language = 'ru' ORDER BY question_id"))
            rows = result.fetchall()
            
            print(f"💖 Все вопросы сферы 'love': {len(rows)}")
            for i, row in enumerate(rows, 1):
                print(f"  {i}. ID: {row[0]}, Тип: {row[2]}, Текст: {row[1][:50]}...")
            
            # Проверяем только базовые вопросы
            result = await conn.execute(text("SELECT question_id, text FROM questions WHERE sphere = 'love' AND type = 'basic' AND language = 'ru' ORDER BY question_id"))
            basic_rows = result.fetchall()
            
            print(f"\n📝 Базовые вопросы сферы 'love': {len(basic_rows)}")
            for i, row in enumerate(basic_rows, 1):
                print(f"  {i}. ID: {row[0]}, Текст: {row[1][:50]}...")
                
            # Проверяем PRO вопросы
            result = await conn.execute(text("SELECT question_id, text, category FROM questions WHERE sphere = 'love' AND type = 'pro' AND language = 'ru' ORDER BY question_id"))
            pro_rows = result.fetchall()
            
            print(f"\n🚀 PRO вопросы сферы 'love': {len(pro_rows)}")
            for i, row in enumerate(pro_rows, 1):
                print(f"  {i}. ID: {row[0]}, Категория: {row[2]}, Текст: {row[1][:50]}...")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_love_questions()) 