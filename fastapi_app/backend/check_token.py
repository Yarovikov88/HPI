#!/usr/bin/env python3
"""
Скрипт для проверки токена Telegram бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем токен
token = os.getenv('TELEGRAM_BOT_TOKEN')

if token:
    print(f"✅ TELEGRAM_BOT_TOKEN найден: {token[:10]}...")
    print(f"Длина токена: {len(token)} символов")
else:
    print("❌ TELEGRAM_BOT_TOKEN не найден!")
    print("\nДля установки токена:")
    print("1. Создайте файл .env в папке backend")
    print("2. Добавьте строку: TELEGRAM_BOT_TOKEN=your_bot_token_here")
    print("3. Замените your_bot_token_here на реальный токен вашего бота")
    
    # Показываем все переменные окружения для отладки
    print("\nДоступные переменные окружения:")
    for key, value in os.environ.items():
        if 'TELEGRAM' in key or 'BOT' in key:
            print(f"  {key}: {value}") 