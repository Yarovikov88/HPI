#!/bin/bash

echo "🔧 Применяем исправления для HPI.EXPERT..."

# 1. Исправляем OAuth2 настройки
echo "🔧 Исправляем OAuth2 настройки..."
chmod +x fix-oauth2.sh
./fix-oauth2.sh

# 2. Останавливаем все сервисы
echo "⏹️ Останавливаем сервисы..."
docker-compose -f docker-compose.optimized.yml down

# 3. Удаляем образ backend для принудительной пересборки
echo "🗑️ Удаляем старый образ backend..."
docker rmi hpisite-backend 2>/dev/null || true

# 4. Запускаем заново с пересборкой
echo "🚀 Запускаем сервисы с исправлениями..."
docker-compose -f docker-compose.optimized.yml up --build -d

# 5. Ждем запуска
echo "⏳ Ждем запуска..."
sleep 30

# 6. Проверяем результат
echo "✅ Проверяем результат..."
curl -I http://83.147.192.188/login

# 7. Тестируем API
echo " Тестируем API..."
curl -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'

echo " Исправления применены!"
echo " Сайт теперь доступен по адресу: http://83.147.192.188"
echo "🔍 Теперь API авторизация должна работать!" 