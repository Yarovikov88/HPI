#!/usr/bin/env python3
"""
Скрипт для импорта вопросов из файла questions.md
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
    # Исключаем метаданные и ищем только заголовки с эмодзи
    pattern = re.compile(r'## (💖|🏡|🤝|💼|♂️|🧠|🎨|💰) (.*?)\n```json\n(.*?)```', re.DOTALL)
    for match in pattern.finditer(md_text):
        emoji = match.group(1)
        sphere_title = match.group(2).strip()
        json_block = match.group(3).strip()
        # Определяем ключ сферы по эмодзи
        sphere_key = SPHERE_MAP.get(emoji, emoji)
        try:
            questions = json.loads(json_block)
        except Exception as e:
            print(f'Ошибка парсинга JSON для сферы {sphere_title}: {e}')
            continue
        results.append((sphere_key, questions))
    return results

async def import_questions_from_file():
    """Импортирует вопросы из файла questions.md"""
    try:
        # Читаем файл с вопросами
        with open('database/questions.md', 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        all_questions = extract_json_blocks(md_text)
        
        async with engine.begin() as conn:
            print("📝 Импорт вопросов из файла questions.md...")
            
            # Очищаем таблицу вопросов
            await conn.execute(text("DELETE FROM questions"))
            print("🗑️ Таблица questions очищена")
            
            total_imported = 0
            
            for sphere_key, questions in all_questions:
                print(f"📊 Импорт сферы: {sphere_key}")
                sphere_count = 0
                
                for question in questions:
                    # Извлекаем данные вопроса
                    question_id = question.get('id', None)
                    q_type = question.get('type', 'basic')
                    q_text = question.get('text', '')
                    q_options = question.get('options', [])
                    q_scores = question.get('scores', [])
                    q_inverse = question.get('inverse', False)
                    q_category = question.get('category', None)
                    q_description = question.get('description', None)
                    q_fields = question.get('fields', None)
                    
                    # Для вопросов метрик используем поле metrics как fields
                    if q_category == 'metrics' and question.get('metrics'):
                        q_fields = {'metrics': question.get('metrics')}
                    
                    # Пропускаем вопросы без ID
                    if not question_id:
                        continue
                    
                    # Вставляем вопрос в базу
                    await conn.execute(text("""
                        INSERT INTO questions (question_id, sphere, type, text, options, scores, inverse, category, description, fields, language)
                        VALUES (:question_id, :sphere, :type, :text, :options, :scores, :inverse, :category, :description, :fields, :language)
                    """), {
                        "question_id": question_id,
                        "sphere": sphere_key,
                        "type": q_type,
                        "text": q_text,
                        "options": json.dumps(q_options) if q_options else None,
                        "scores": json.dumps(q_scores) if q_scores else None,
                        "inverse": q_inverse,
                        "category": q_category,
                        "description": q_description,
                        "fields": json.dumps(q_fields) if q_fields else None,
                        "language": "ru"
                    })
                    
                    sphere_count += 1
                    total_imported += 1
                
                print(f"  ✅ Импортировано {sphere_count} вопросов")
            
            print(f"\n🎉 Всего импортировано: {total_imported} вопросов")
            
            # Проверяем результат
            result = await conn.execute(text("SELECT COUNT(*) FROM questions"))
            count = result.scalar()
            print(f"📊 Всего вопросов в базе: {count}")
            
            # Проверяем по типам
            result = await conn.execute(text("SELECT type, COUNT(*) FROM questions GROUP BY type"))
            types = result.fetchall()
            print("\n📝 Вопросы по типам:")
            for q_type, count in types:
                print(f"  - {q_type}: {count} вопросов")
            
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")

if __name__ == "__main__":
    asyncio.run(import_questions_from_file()) 