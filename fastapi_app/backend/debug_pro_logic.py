#!/usr/bin/env python3
"""
Скрипт для отладки логики PRO
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def debug_pro_logic():
    try:
        async with engine.begin() as conn:
            # Проверяем PRO вопросы
            result = await conn.execute(text("SELECT COUNT(*) FROM questions WHERE type = 'pro'"))
            pro_questions_count = result.scalar()
            print(f"📋 PRO вопросов в базе: {pro_questions_count}")
            
            if pro_questions_count > 0:
                result = await conn.execute(text("SELECT DISTINCT category FROM questions WHERE type = 'pro'"))
                categories = [row[0] for row in result.fetchall()]
                print(f"📂 Категории PRO вопросов: {categories}")
                
                for category in categories:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM questions WHERE type = 'pro' AND category = '{category}'"))
                    count = result.scalar()
                    print(f"  - {category}: {count} вопросов")
            else:
                print("❌ PRO вопросов нет в базе!")
                
            # Проверяем PRO ответы
            result = await conn.execute(text("SELECT COUNT(*) FROM problems"))
            problems_count = result.scalar()
            result = await conn.execute(text("SELECT COUNT(*) FROM goals"))
            goals_count = result.scalar()
            result = await conn.execute(text("SELECT COUNT(*) FROM blockers"))
            blockers_count = result.scalar()
            result = await conn.execute(text("SELECT COUNT(*) FROM metrics"))
            metrics_count = result.scalar()
            result = await conn.execute(text("SELECT COUNT(*) FROM achievements"))
            achievements_count = result.scalar()
            
            print(f"\n📊 PRO ответы:")
            print(f"  - Проблемы: {problems_count}")
            print(f"  - Цели: {goals_count}")
            print(f"  - Блокеры: {blockers_count}")
            print(f"  - Метрики: {metrics_count}")
            print(f"  - Достижения: {achievements_count}")
            
            total_pro_answers = problems_count + goals_count + blockers_count + metrics_count + achievements_count
            print(f"\n📈 Всего PRO ответов: {total_pro_answers}")
            
            if total_pro_answers == 0 and pro_questions_count > 0:
                print("🔍 Проблема: Есть PRO вопросы, но нет ответов - галочка не должна показываться!")
            elif total_pro_answers == 0 and pro_questions_count == 0:
                print("🔍 Проблема: Нет PRO вопросов - возможно, они не загружены в frontend!")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pro_logic()) 