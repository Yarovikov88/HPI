#!/usr/bin/env python3
"""
Скрипт для проверки PRO данных в базе
"""
import asyncio
from sqlalchemy import text
from app.db import engine

async def check_pro_data():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM problems"))
            problems_count = result.scalar()
            print(f"📋 Проблемы: {problems_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM goals"))
            goals_count = result.scalar()
            print(f"🎯 Цели: {goals_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM blockers"))
            blockers_count = result.scalar()
            print(f"🚫 Блокеры: {blockers_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM metrics"))
            metrics_count = result.scalar()
            print(f"📊 Метрики: {metrics_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM achievements"))
            achievements_count = result.scalar()
            print(f"🏆 Достижения: {achievements_count}")
            
            total_pro = problems_count + goals_count + blockers_count + metrics_count + achievements_count
            print(f"\n📈 Всего PRO записей: {total_pro}")
            
            if total_pro == 0:
                print("❌ PRO данные отсутствуют - галочка не должна показываться!")
            else:
                print("✅ PRO данные есть - галочка может показываться")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_pro_data()) 