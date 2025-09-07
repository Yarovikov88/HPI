#!/usr/bin/env python3
"""
Скрипт для инициализации локальной SQLite базы данных HPI
"""

import asyncio
import sys
import os
import json
import re
from sqlalchemy import text as sa_text
from app.db import engine, Base
from app.models import User, Answer, Problem, Goal, Blocker, Metric, Achievement, AIRecommendation, Question

async def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(sa_text("SELECT sqlite_version()"))
            version = result.scalar()
            print(f"✅ Подключение к SQLite успешно: {version}")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

async def create_tables():
    """Создает все таблицы"""
    try:
        async with engine.begin() as conn:
            print("🔨 Создаю таблицы...")
            
            # Создаем все таблицы из моделей
            await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Все таблицы созданы успешно!")
            return True
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False

async def verify_tables():
    """Проверяет, что таблицы созданы"""
    try:
        async with engine.begin() as conn:
            # Проверяем основные таблицы
            tables = ['users', 'questions', 'answers', 'problems', 'goals', 'blockers', 'metrics', 'achievements', 'ai_recommendations']
            
            for table in tables:
                result = await conn.execute(sa_text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📊 Таблица {table}: {count} записей")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка проверки таблиц: {e}")
        return False

async def import_questions_from_file(file_path: str, language: str = 'ru'):
    """Импортирует вопросы из JSON файла"""
    try:
        print(f"📖 Импортирую вопросы из {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        print(f"🔍 Загружено {len(questions_data)} вопросов из JSON файла")
        
        questions_imported = 0
        
        async with engine.begin() as conn:
            for question in questions_data:
                if 'text' in question and 'type' in question:
                    print(f"    Обрабатываю вопрос: {question.get('id', 'N/A')} - {question.get('sphere', 'unknown')}")
                    
                    # Определяем сферу из поля sphere
                    sphere = question.get('sphere', 'unknown')
                    
                    # Вставляем вопрос
                    await conn.execute(sa_text("""
                        INSERT OR IGNORE INTO questions 
                        (question_id, sphere, type, text, options, scores, inverse, category, description, fields, language)
                        VALUES (:question_id, :sphere, :type, :text, :options, :scores, :inverse, :category, :description, :fields, :language)
                    """), {
                        'question_id': question.get('id', ''),
                        'sphere': sphere,
                        'type': question.get('type', 'basic'),
                        'text': question.get('text', ''),
                        'options': json.dumps(question.get('options', [])) if question.get('options') else None,
                        'scores': json.dumps(question.get('scores', [])) if question.get('scores') else None,
                        'inverse': question.get('inverse', False),
                        'category': question.get('category'),
                        'description': question.get('description'),
                        'fields': json.dumps(question.get('fields', {})) if question.get('fields') else None,
                        'language': language
                    })
                    questions_imported += 1
        
        print(f"✅ Импортировано {questions_imported} вопросов для языка {language}")
        return questions_imported
        
    except Exception as e:
        print(f"❌ Ошибка импорта вопросов: {e}")
        return 0

async def create_sample_data():
    """Создает тестовые данные"""
    try:
        async with engine.begin() as conn:
            print("📝 Создаю тестовые данные...")
            
            # Создаем тестового пользователя
            await conn.execute(sa_text("""
                INSERT OR IGNORE INTO users (id, email, username, first_name, is_pro, has_password) 
                VALUES (1, 'test@example.com', 'testuser', 'Test User', true, false)
            """))
            
            # Создаем тестовые ответы
            await conn.execute(sa_text("""
                INSERT OR IGNORE INTO answers (user_id, sphere, question_id, answer, date) 
                VALUES (1, 1, '1.1', '3', '2024-01-01')
            """))
            
            await conn.execute(sa_text("""
                INSERT OR IGNORE INTO answers (user_id, sphere, question_id, answer, date) 
                VALUES (1, 2, '2.1', '4', '2024-01-01')
            """))
            
            print("✅ Тестовые данные созданы!")
            return True
    except Exception as e:
        print(f"❌ Ошибка создания тестовых данных: {e}")
        return False

async def main():
    """Основная функция"""
    print("🚀 Запуск скрипта инициализации локальной БД...")
    
    # Проверяем подключение
    if not await test_connection():
        print("❌ Не удалось подключиться к базе данных")
        sys.exit(1)
    
    # Создаем таблицы
    if not await create_tables():
        print("❌ Не удалось создать таблицы")
        sys.exit(1)
    
    # Импортируем вопросы
    questions_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    if os.path.exists(questions_file):
        await import_questions_from_file(questions_file, 'ru')
    else:
        print(f"⚠️ Файл с вопросами не найден: {questions_file}")
    
    # Для английского языка пока используем тот же файл
    questions_en_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    if os.path.exists(questions_en_file):
        await import_questions_from_file(questions_en_file, 'en')
    else:
        print(f"⚠️ Файл с английскими вопросами не найден: {questions_en_file}")
    
    # Создаем тестовые данные
    if not await create_sample_data():
        print("❌ Не удалось создать тестовые данные")
        sys.exit(1)
    
    # Проверяем результат
    if not await verify_tables():
        print("❌ Ошибка при проверке таблиц")
        sys.exit(1)
    
    print("🎉 Локальная база данных инициализирована успешно!")
    print("📁 Файл БД: hpi_local.db")

if __name__ == "__main__":
    asyncio.run(main()) 