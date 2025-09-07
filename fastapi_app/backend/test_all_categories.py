#!/usr/bin/env python3
"""
Скрипт для тестирования исправления всех PRO категорий
"""
import asyncio
from sqlalchemy import text as sa_text
from app.db import engine

async def test_all_categories():
    try:
        async with engine.begin() as conn:
            categories = ['problems', 'goals', 'blockers', 'metrics', 'achievements']
            
            print("🔧 Тестирование исправления для всех PRO категорий:")
            print("=" * 70)
            
            for category in categories:
                result = await conn.execute(sa_text(f"""
                    SELECT id, sphere, text, description, fields
                    FROM questions 
                    WHERE type = 'pro' AND category = '{category}'
                    ORDER BY sphere, id
                """))
                
                rows = result.fetchall()
                
                print(f"\n📋 Категория: {category}")
                print(f"   Количество вопросов: {len(rows)}")
                
                if rows:
                    # Показываем первый вопрос как пример
                    question_id, sphere, text, description, fields = rows[0]
                    print(f"   Пример вопроса:")
                    print(f"     ID: {question_id}, Сфера: {sphere}")
                    print(f"     Text: {text}")
                    print(f"     Description: {description}")
                    print(f"     Fields: {fields}")
                else:
                    print(f"   ❌ Нет вопросов!")
                
                print("   " + "-" * 50)
            
            print(f"\n✅ Тестирование завершено для {len(categories)} категорий")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_categories()) 