#!/usr/bin/env python3
"""
Скрипт для тестирования исправления PRO вопросов категории problems
"""
import asyncio
import json
from sqlalchemy import text as sa_text
from app.db import engine

def extract_question_from_fields(fields_json):
    """Извлекает реальный вопрос из JSON fields"""
    try:
        if not fields_json:
            return "Опишите подробно"
        
        fields = json.loads(fields_json) if isinstance(fields_json, str) else fields_json
        
        # Для metrics - особый случай с несколькими полями
        if 'goal' in fields and 'name' in fields:
            # Проверяем, есть ли дополнительные поля для метрик
            metric_fields = []
            if 'name' in fields:
                metric_fields.append(fields['name'].get('question', 'Название метрики'))
            if 'goal' in fields:
                metric_fields.append(fields['goal'].get('question', 'Желаемое значение'))
            if 'type' in fields:
                metric_fields.append(fields['type'].get('question', 'Тип метрики'))
            if 'unit' in fields:
                metric_fields.append(fields['unit'].get('question', 'Единица измерения'))
            if 'value' in fields:
                metric_fields.append(fields['value'].get('question', 'Текущее значение'))
            
            # Объединяем все поля метрики
            if len(metric_fields) >= 2:
                return f"{metric_fields[0]} и {metric_fields[1]}"
            elif len(metric_fields) == 1:
                return metric_fields[0]
            else:
                return "Опишите метрику"
        
        # Для остальных - ищем text.question
        if 'text' in fields and isinstance(fields['text'], dict):
            return fields['text'].get('question', 'Опишите подробно')
        
        # Если не нашли question, возвращаем первый text
        for field_name, field_data in fields.items():
            if isinstance(field_data, dict) and 'question' in field_data:
                return field_data['question']
        
        # Если fields содержит простую структуру без question, используем description или заглушку
        if 'text' in fields:
            return "Опишите подробно"
        
        return "Опишите подробно"
    except:
        return "Опишите подробно"

async def test_problems_fix():
    try:
        async with engine.begin() as conn:
            # Получаем вопросы категории problems
            result = await conn.execute(sa_text("""
                SELECT id, sphere, text, description, fields
                FROM questions 
                WHERE type = 'pro' AND category = 'problems'
                ORDER BY sphere, id
            """))
            
            rows = result.fetchall()
            
            print("🔧 Тестирование исправления для вопросов problems:")
            print("=" * 60)
            
            for row in rows:
                question_id, sphere, text, description, fields = row
                
                # Старый способ (extract_question_from_fields)
                old_question = extract_question_from_fields(fields)
                
                # Новый способ (использование description)
                new_question = description if description else f"Опишите problems"
                
                print(f"ID: {question_id}, Сфера: {sphere}")
                print(f"  Старый способ: {old_question}")
                print(f"  Новый способ:  {new_question}")
                print(f"  Description:   {description}")
                print("  ---")
            
            print(f"\n✅ Всего вопросов problems: {len(rows)}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_problems_fix()) 