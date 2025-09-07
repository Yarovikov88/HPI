#!/usr/bin/env python3
"""
Скрипт для проверки ответов сферы love
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_love_answers():
    try:
        async with engine.begin() as conn:
            # Проверяем ответы для сферы love (sphere=1)
            result = await conn.execute(text("SELECT question_id, answer FROM answers WHERE sphere = 1 AND date = '2025-08-30' ORDER BY question_id"))
            rows = result.fetchall()
            
            print("💖 Ответы для сферы love (sphere=1):")
            for row in rows:
                print(f"  {row[0]}: {row[1]}")
            
            print(f"\n📊 Всего ответов для сферы love: {len(rows)}")
            
            # Проверяем, какие вопросы должны быть в сфере love
            result = await conn.execute(text("SELECT question_id FROM questions WHERE sphere = 'love' AND type = 'basic' AND language = 'ru' ORDER BY question_id"))
            expected_questions = [row[0] for row in result.fetchall()]
            
            print(f"\n📝 Ожидаемые вопросы для сферы love: {expected_questions}")
            
            # Проверяем, какие вопросы отвечены
            answered_questions = [row[0] for row in rows]
            missing_questions = [q for q in expected_questions if q not in answered_questions]
            
            print(f"\n❌ Отсутствующие ответы: {missing_questions}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_love_answers()) 