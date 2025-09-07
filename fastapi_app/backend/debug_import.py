#!/usr/bin/env python3
"""
Скрипт для отладки импорта вопросов
"""

import asyncio
import json
import re
from sqlalchemy import text
from app.db import engine

# Сопоставление эмодзи и ключа сферы
SPHERE_MAP = {
    '💖': 'love',
    '🏡': 'family',
    '🤝': 'friends',
    '💼': 'career',
    '♂️': 'physical',
    '🧠': 'mental',
    '🎨': 'hobby',
    '💰': 'wealth',
}

def extract_json_blocks(md_text):
    """
    Извлекает JSON блоки с вопросами из markdown файла
    """
    results = []
    # Находим все заголовки сферы и следующий за ними JSON-блок
    pattern = re.compile(r'## (.*?)\n```json\n(.*?)```', re.DOTALL)
    for match in pattern.finditer(md_text):
        sphere_title = match.group(1).strip()
        json_block = match.group(2).strip()
        # Определяем ключ сферы по эмодзи
        emoji = sphere_title.split()[0]
        sphere_key = SPHERE_MAP.get(emoji, emoji)
        print(f"🔍 Найдена сфера: '{sphere_title}' -> эмодзи: '{emoji}' -> ключ: '{sphere_key}'")
        try:
            questions = json.loads(json_block)
            print(f"  📝 Вопросов в сфере: {len(questions)}")
        except Exception as e:
            print(f'❌ Ошибка парсинга JSON для сферы {sphere_title}: {e}')
            continue
        results.append((sphere_key, questions))
    return results

async def debug_import():
    """Отлаживает импорт вопросов"""
    try:
        # Читаем файл с вопросами
        with open('database/questions.md', 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        print("📖 Анализ файла questions.md...")
        all_questions = extract_json_blocks(md_text)
        
        print(f"\n📊 Всего найдено сфер: {len(all_questions)}")
        for sphere_key, questions in all_questions:
            print(f"  - {sphere_key}: {len(questions)} вопросов")
            
        # Проверяем, что в базе
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT DISTINCT sphere FROM questions WHERE type = 'basic' AND language = 'ru' ORDER BY sphere"))
            db_spheres = [row[0] for row in result.fetchall()]
            print(f"\n🗄️ Сферы в базе данных: {db_spheres}")
            
            # Проверяем сферу love
            result = await conn.execute(text("SELECT COUNT(*) FROM questions WHERE sphere = 'love' AND type = 'basic' AND language = 'ru'"))
            love_count = result.scalar()
            print(f"💖 Вопросов сферы 'love' в базе: {love_count}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(debug_import()) 