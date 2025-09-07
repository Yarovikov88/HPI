#!/usr/bin/env python3
"""
🔐 Простой скрипт для получения токена HPI API
Запуск: python simple_token_getter.py
"""

import requests
import json

# Настройки
API_URL = "https://hpi.expert:8443/api/telegram_auth"
TELEGRAM_ID = "1014395380"

def get_token():
    """Получает токен через Telegram авторизацию"""
    
    print("🚀 Получаем токен для HPI API...")
    print("=" * 50)
    
    # Данные для авторизации
    data = {
        "id": int(TELEGRAM_ID),
        "first_name": "Test",
        "last_name": "User", 
        "username": "testuser",
        "photo_url": None
    }
    
    try:
        # Отправляем запрос
        response = requests.post(API_URL, json=data)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            
            if token:
                print("✅ Токен получен успешно!")
                print("=" * 60)
                print(token)
                print("=" * 60)
                
                # Тестируем токен
                test_token(token)
                
                return token
            else:
                print("❌ Токен не найден в ответе")
                return None
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📝 {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_token(token):
    """Тестирует полученный токен"""
    
    print("\n🧪 Тестируем токен...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://hpi.expert:8443/api/answers', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Токен работает! Получено ответов: {len(data)}")
        else:
            print(f"⚠️ Токен получен, но есть проблемы с API: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Ошибка тестирования: {e}")

def main():
    """Главная функция"""
    
    print("🔐 HPI Token Getter")
    print("=" * 50)
    
    token = get_token()
    
    if token:
        print("\n📋 ИНСТРУКЦИЯ:")
        print("1. Скопируйте токен выше")
        print("2. Отправьте токен мне")
        print("3. Используйте токен для работы с API")
        print("\n✅ Готово!")
    else:
        print("\n❌ Не удалось получить токен")
        print("💡 Попробуйте еще раз или обратитесь за помощью")

if __name__ == "__main__":
    main() 