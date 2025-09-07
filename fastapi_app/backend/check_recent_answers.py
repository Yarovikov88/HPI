#!/usr/bin/env python3
"""
Скрипт для проверки последних ответов
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_recent_answers():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT user_id, sphere, question_id, answer, date FROM answers ORDER BY created_at DESC LIMIT 10"))
            rows = result.fetchall()
            
            print("📝 Последние 10 ответов:")
            for i, row in enumerate(rows, 1):
                print(f"  {i}. Пользователь: {row[0]}, Сфера: {row[1]}, Вопрос: {row[2]}, Ответ: {row[3]}, Дата: {row[4]}")
            
            if not rows:
                print("❌ Ответов нет!")
            else:
                print(f"\n✅ Всего ответов в базе: {len(rows)}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_recent_answers()) 