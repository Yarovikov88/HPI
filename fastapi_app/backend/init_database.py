#!/usr/bin/env python3
"""
Скрипт для полной инициализации базы данных HPI
"""

import asyncio
import sys
import os
from sqlalchemy import text
from app.db import engine, SessionLocal
from app.models import User, Answer, Problem, Goal, Blocker, Metric, Achievement, AIRecommendation
from passlib.context import CryptContext

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_basic_data():
    """Создает базовые данные для тестирования"""
    try:
        async with SessionLocal() as session:
            print("🔨 Создаю базовые данные...")
            
            # Проверяем, есть ли уже пользователи
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            
            if user_count == 0:
                # Создаем тестового пользователя
                test_user = User(
                    email="test@example.com",
                    hashed_password=pwd_context.hash("test123"),
                    username="testuser",
                    first_name="Test",
                    last_name="User",
                    is_pro=False
                )
                session.add(test_user)
                await session.commit()
                print("✅ Создан тестовый пользователь: test@example.com / test123")
            else:
                print(f"📊 В базе уже есть {user_count} пользователей")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка создания базовых данных: {e}")
        return False

async def main():
    """Основная функция инициализации"""
    print("🚀 Инициализация базы данных HPI...")
    
    try:
        # Создаем таблицы
        from create_tables import main as create_tables_main
        await create_tables_main()
        
        # Создаем базовые данные
        if not await create_basic_data():
            print("❌ Не удалось создать базовые данные")
            sys.exit(1)
        
        print("🎉 База данных инициализирована успешно!")
        print("📋 Тестовые данные:")
        print("   Email: test@example.com")
        print("   Password: test123")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 