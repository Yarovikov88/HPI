#!/usr/bin/env python3
"""
Скрипт для мониторинга ответов в базе данных
"""

import asyncio
import time
from sqlalchemy import text
from app.db import engine

async def monitor_answers():
    """Мониторит ответы в базе данных"""
    print("🔍 Мониторинг ответов в базе данных...")
    print("Нажмите Ctrl+C для остановки\n")
    
    last_count = 0
    
    while True:
        try:
            async with engine.begin() as conn:
                # Проверяем количество ответов
                result = await conn.execute(text("SELECT COUNT(*) FROM answers"))
                answers_count = result.scalar()
                
                # Проверяем количество проблем
                result = await conn.execute(text("SELECT COUNT(*) FROM problems"))
                problems_count = result.scalar()
                
                # Проверяем количество целей
                result = await conn.execute(text("SELECT COUNT(*) FROM goals"))
                goals_count = result.scalar()
                
                # Проверяем количество блокеров
                result = await conn.execute(text("SELECT COUNT(*) FROM blockers"))
                blockers_count = result.scalar()
                
                # Проверяем количество метрик
                result = await conn.execute(text("SELECT COUNT(*) FROM metrics"))
                metrics_count = result.scalar()
                
                # Проверяем количество достижений
                result = await conn.execute(text("SELECT COUNT(*) FROM achievements"))
                achievements_count = result.scalar()
                
                # Проверяем количество AI рекомендаций
                result = await conn.execute(text("SELECT COUNT(*) FROM ai_recommendations"))
                ai_count = result.scalar()
                
                # Если есть новые записи, показываем их
                if answers_count > last_count:
                    print(f"🆕 Новые ответы! Было: {last_count}, стало: {answers_count}")
                    
                    # Показываем последние ответы
                    result = await conn.execute(text("""
                        SELECT a.id, a.user_id, a.sphere, a.question_id, a.answer, a.date, a.created_at
                        FROM answers a
                        ORDER BY a.created_at DESC
                        LIMIT 5
                    """))
                    recent_answers = result.fetchall()
                    
                    print("📝 Последние ответы:")
                    for answer in recent_answers:
                        print(f"  - ID: {answer[0]}, Пользователь: {answer[1]}, Сфера: {answer[2]}, Вопрос: {answer[3]}, Ответ: {answer[4]}")
                
                # Показываем текущее состояние
                print(f"\r📊 Состояние БД: Ответы: {answers_count} | Проблемы: {problems_count} | Цели: {goals_count} | Блокеры: {blockers_count} | Метрики: {metrics_count} | Достижения: {achievements_count} | AI: {ai_count}", end="")
                
                last_count = answers_count
                
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
        
        # Ждем 2 секунды перед следующей проверкой
        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_answers())
    except KeyboardInterrupt:
        print("\n\n👋 Мониторинг остановлен") 