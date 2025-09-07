#!/bin/bash

echo "🔧 Создаем тестового пользователя yx@gmail.com..."

# 1. Проверяем, что backend работает
echo "📊 Проверяем backend..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ Backend работает"
else
    echo "❌ Backend не работает"
    exit 1
fi

# 2. Создаем тестового пользователя
echo "👤 Создаем пользователя yx@gmail.com..."
curl -X POST http://83.147.192.188/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555","full_name":"Test User"}'

echo ""
echo "🔐 Тестируем логин..."
LOGIN_RESPONSE=$(curl -s -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555"}')

echo "Ответ логина: $LOGIN_RESPONSE"

# 3. Извлекаем токен
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ Токен получен: ${TOKEN:0:20}..."
    
    # 4. Тестируем календарь API
    echo ""
    echo "📅 Тестируем календарь API..."
    CALENDAR_RESPONSE=$(curl -s -X GET "http://83.147.192.188/api/calendar/status?from=2025-08-01&to=2025-08-31" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "Ответ календаря: $CALENDAR_RESPONSE"
    
    # 5. Тестируем профиль
    echo ""
    echo "👤 Тестируем профиль..."
    PROFILE_RESPONSE=$(curl -s -X GET "http://83.147.192.188/api/profile" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "Ответ профиля: $PROFILE_RESPONSE"
    
else
    echo "❌ Токен не получен"
fi

echo ""
echo "🎯 Тестирование завершено!" 