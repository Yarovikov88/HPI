#!/usr/bin/env python3
"""
Скрипт для генерации API ключей
"""
import uuid
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def generate_api_key():
    """Генерирует новый API ключ"""
    api_key = str(uuid.uuid4())
    print(f"🔑 Сгенерирован новый API ключ: {api_key}")
    print(f"\nДобавьте в .env файл:")
    print(f"API_KEY={api_key}")
    return api_key

def check_api_key():
    """Проверяет текущий API ключ"""
    api_key = os.getenv('API_KEY')
    if api_key:
        print(f"✅ API ключ найден: {api_key[:10]}...")
        return api_key
    else:
        print("❌ API ключ не найден в .env файле")
        return None

if __name__ == "__main__":
    print("🔧 Генератор API ключей")
    print("=" * 40)
    
    # Проверяем текущий ключ
    current_key = check_api_key()
    
    if not current_key:
        print("\nСоздать новый API ключ? (y/n): ", end="")
        response = input().lower()
        if response == 'y':
            generate_api_key()
        else:
            print("❌ API ключ не создан")
    else:
        print("\nСоздать новый API ключ? (y/n): ", end="")
        response = input().lower()
        if response == 'y':
            generate_api_key()
        else:
            print("✅ Используется существующий API ключ") 