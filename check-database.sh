#!/bin/bash

echo "🔍 Проверяем базу данных HPI..."

# 1. Проверяем подключение к PostgreSQL
echo "📊 Проверяем подключение к PostgreSQL..."
docker exec -it hpisite-postgres-1 psql -U hpi_user -d hpi_db -c "SELECT version();"

# 2. Проверяем таблицы
echo ""
echo "📋 Проверяем таблицы..."
docker exec -it hpisite-postgres-1 psql -U hpi_user -d hpi_db -c "\dt"

# 3. Проверяем пользователей
echo ""
echo "👥 Проверяем пользователей..."
docker exec -it hpisite-postgres-1 psql -U hpi_user -d hpi_db -c "SELECT user_id, email, username, is_pro FROM users;"

# 4. Проверяем пароль пользователя test@example.com
echo ""
echo "🔐 Проверяем пароль пользователя test@example.com..."
docker exec -it hpisite-postgres-1 psql -U hpi_user -d hpi_db -c "SELECT user_id, email, username, hashed_password IS NOT NULL as has_password FROM users WHERE email = 'test@example.com';"

# 5. Создаем тестового пользователя если его нет
echo ""
echo "🔨 Создаем тестового пользователя..."
docker exec -it hpisite-backend-1 python /app/init_database.py

# 6. Проверяем результат
echo ""
echo "✅ Проверяем результат..."
docker exec -it hpisite-postgres-1 psql -U hpi_user -d hpi_db -c "SELECT user_id, email, username, is_pro FROM users WHERE email = 'test@example.com';"

echo ""
echo "🎯 Теперь тестируем API логин..."
curl -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' 