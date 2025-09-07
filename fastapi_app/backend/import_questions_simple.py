#!/usr/bin/env python3
"""
Простой скрипт для импорта вопросов в базу данных
"""

import asyncio
import json
from sqlalchemy import text
from app.db import engine
from app.models import Problem

# Примеры вопросов для импорта
QUESTIONS_DATA = [
    {
        "id": 1,
        "text": "Как часто вы проводите качественное время вместе?",
        "category": "love",
        "type": "multiple_choice",
        "options": ["Редко или никогда", "Иногда", "Часто", "Регулярно и осознанно"],
        "scores": [1, 2, 3, 4],
        "description": "Оцените качество времени, проведенного с близкими"
    },
    {
        "id": 2,
        "text": "Насколько вы довольны своими отношениями?",
        "category": "love",
        "type": "multiple_choice",
        "options": ["Совсем не доволен", "Не очень доволен", "Доволен", "Очень доволен"],
        "scores": [1, 2, 3, 4],
        "description": "Общая оценка удовлетворенности отношениями"
    },
    {
        "id": 3,
        "text": "Как часто вы общаетесь с семьей?",
        "category": "family",
        "type": "multiple_choice",
        "options": ["Редко", "Иногда", "Часто", "Ежедневно"],
        "scores": [1, 2, 3, 4],
        "description": "Частота общения с членами семьи"
    },
    {
        "id": 4,
        "text": "Насколько вы удовлетворены своей карьерой?",
        "category": "career",
        "type": "multiple_choice",
        "options": ["Не удовлетворен", "Частично удовлетворен", "Удовлетворен", "Полностью удовлетворен"],
        "scores": [1, 2, 3, 4],
        "description": "Уровень удовлетворенности профессиональной деятельностью"
    },
    {
        "id": 5,
        "text": "Как часто вы занимаетесь спортом?",
        "category": "physical",
        "type": "multiple_choice",
        "options": ["Не занимаюсь", "Редко", "2-3 раза в неделю", "Ежедневно"],
        "scores": [1, 2, 3, 4],
        "description": "Регулярность физических нагрузок"
    },
    {
        "id": 6,
        "text": "Насколько вы довольны своим финансовым положением?",
        "category": "wealth",
        "type": "multiple_choice",
        "options": ["Не доволен", "Частично доволен", "Доволен", "Очень доволен"],
        "scores": [1, 2, 3, 4],
        "description": "Удовлетворенность финансовым состоянием"
    }
]

async def import_questions():
    """Импортирует вопросы в базу данных"""
    try:
        async with engine.begin() as conn:
            print("📝 Импорт вопросов в базу данных...")
            
            # Очищаем таблицу вопросов
            await conn.execute(text("DELETE FROM problems"))
            print("🗑️ Таблица вопросов очищена")
            
            # Импортируем вопросы
            for question in QUESTIONS_DATA:
                await conn.execute(text("""
                    INSERT INTO problems (id, text, category, type, options, scores, description)
                    VALUES (:id, :text, :category, :type, :options, :scores, :description)
                """), {
                    "id": question["id"],
                    "text": question["text"],
                    "category": question["category"],
                    "type": question["type"],
                    "options": json.dumps(question["options"]),
                    "scores": json.dumps(question["scores"]),
                    "description": question["description"]
                })
            
            print(f"✅ Импортировано {len(QUESTIONS_DATA)} вопросов")
            
            # Проверяем результат
            result = await conn.execute(text("SELECT COUNT(*) FROM problems"))
            count = result.scalar()
            print(f"📊 Всего вопросов в базе: {count}")
            
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")

if __name__ == "__main__":
    asyncio.run(import_questions()) 