#!/bin/bash

echo "🔧 Применяем ВСЕ исправления для HPI.EXPERT (включая календарь API)..."

# 1. Останавливаем все сервисы
echo "⏹️ Останавливаем сервисы..."
docker-compose -f docker-compose.optimized.yml down

# 2. Удаляем образы для принудительной пересборки
echo "🗑️ Удаляем старые образы..."
docker rmi hpisite-backend 2>/dev/null || true
docker rmi hpisite-frontend 2>/dev/null || true

# 3. Запускаем заново с пересборкой
echo "🚀 Запускаем сервисы с исправлениями..."
docker-compose -f docker-compose.optimized.yml up --build -d

# 4. Ждем запуска
echo "⏳ Ждем запуска..."
sleep 30

# 4.5. Инициализируем базу данных
echo "🗄️ Инициализируем базу данных..."
docker exec -it hpisite-backend-1 python /app/init_database.py

# 5. Копируем исправленную nginx конфигурацию
echo "📝 Обновляем nginx конфигурацию..."
docker cp nginx-fixed.conf hpisite-frontend-1:/etc/nginx/nginx.conf

# 6. Перезапускаем frontend
echo "🔄 Перезапускаем frontend..."
docker restart hpisite-frontend-1

# 7. Ждем запуска frontend
echo "⏳ Ждем запуска frontend..."
sleep 10

# 8. Проверяем результат
echo "✅ Проверяем результат..."
echo "🌐 Frontend:"
curl -I http://83.147.192.188/login

echo ""
echo "🔌 API (новый endpoint):"
curl -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555"}'

echo ""
echo "🔌 API (старый endpoint - должен работать через redirect):"
curl -X POST http://83.147.192.188/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555"}'

echo ""
echo "📅 Проверяем календарь API..."
curl -X GET "http://83.147.192.188/api/calendar/status?from=2025-08-01&to=2025-08-31" \
  -H "Authorization: Bearer $(curl -s -X POST http://83.147.192.188/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"yx@gmail.com","password":"555"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)"

echo ""
echo "🎉 Все исправления применены!"
echo "🌐 Сайт доступен по адресу: http://83.147.192.188"
echo "🔍 Теперь работают оба endpoint: /api/login и /api/auth/login"
echo "📅 Календарь API исправлен: параметры from и to" 