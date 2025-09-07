#!/usr/bin/env python3
"""
Скрипт для проверки ответов сферы family
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_family_answers():
    try:
        async with engine.begin() as conn:
            # Проверяем ответы для сферы family (sphere=2)
            result = await conn.execute(text("SELECT question_id, answer FROM answers WHERE sphere = 2 AND date = '2025-08-30' ORDER BY question_id"))
            rows = result.fetchall()
            
            print("🏡 Ответы для сферы family (sphere=2):")
            for row in rows:
                print(f"  {row[0]}: {row[1]}")
            
            print(f"\n📊 Всего ответов для сферы family: {len(rows)}")
            
            # Проверяем, какие вопросы должны быть в сфере family
            result = await conn.execute(text("SELECT question_id FROM questions WHERE sphere = 'family' AND type = 'basic' AND language = 'ru' ORDER BY question_id"))
            expected_questions = [row[0] for row in result.fetchall()]
            
            print(f"\n📝 Ожидаемые вопросы для сферы family: {expected_questions}")
            
            # Проверяем, какие вопросы отвечены
            answered_questions = [row[0] for row in rows]
            missing_questions = [q for q in expected_questions if q not in answered_questions]
            
            print(f"\n❌ Отсутствующие ответы: {missing_questions}")
            
            if len(missing_questions) == 0:
                print("✅ Сфера family полностью завершена!")
            else:
                print(f"❌ Сфера family не завершена - отсутствует {len(missing_questions)} ответов")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_family_answers()) 