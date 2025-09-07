#!/usr/bin/env python3
"""
Скрипт для тестирования API endpoint всех PRO категорий
"""
import asyncio
from app.routers.pro import load_pro_questions_from_db, get_db

async def test_api_all_categories():
    try:
        categories = ['problems', 'goals', 'blockers', 'metrics', 'achievements']
        
        print("🚀 Тестирование API endpoint для всех PRO категорий:")
        print("=" * 70)
        
        async for db in get_db():
            for category in categories:
                questions_by_sphere = await load_pro_questions_from_db(category, db)
                
                print(f"\n📋 Категория: {category}")
                print(f"   Сфер с вопросами: {len(questions_by_sphere)}")
                
                if questions_by_sphere:
                    total_questions = sum(len(questions) for questions in questions_by_sphere.values())
                    print(f"   Всего вопросов: {total_questions}")
                    
                    # Показываем примеры вопросов
                    for sphere_key, sphere_questions in list(questions_by_sphere.items())[:2]:
                        print(f"   Сфера {sphere_key}: {len(sphere_questions)} вопросов")
                        if sphere_questions:
                            q = sphere_questions[0]
                            print(f"     Пример: {q['text']}")
                else:
                    print(f"   ❌ Нет вопросов!")
                
                print("   " + "-" * 50)
            break
        
        print(f"\n✅ Тестирование завершено для {len(categories)} категорий")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_all_categories()) 