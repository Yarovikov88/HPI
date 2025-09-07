#!/bin/bash

echo "🔧 Исправление проблем с Docker..."

# Остановка всех контейнеров
echo "⏹️  Остановка всех контейнеров..."
docker stop $(docker ps -aq) 2>/dev/null || true

# Удаление всех контейнеров
echo "🗑️  Удаление всех контейнеров..."
docker rm $(docker ps -aq) 2>/dev/null || true

# Очистка неиспользуемых образов
echo "🧹 Очистка образов..."
docker image prune -f

# Создание папки для логов
echo "📁 Создание папки для логов..."
mkdir -p logs/nginx

# Проверка Dockerfile
echo "🔍 Проверка Dockerfile..."
if [ ! -f "Dockerfile.frontend" ]; then
    echo "❌ Dockerfile.frontend не найден!"
    exit 1
fi

if [ ! -f "fastapi_app/backend/Dockerfile" ]; then
    echo "❌ Backend Dockerfile не найден!"
    exit 1
fi

echo "✅ Все файлы на месте!"

# Запуск системы
echo "🚀 Запуск системы HPI88..."
docker-compose -f docker-compose.hpisite.yml up -d --build

echo "✅ Система запущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   - Сайт: http://localhost"
echo "   - API: http://localhost/api"
echo "   - Grafana: http://localhost:3001 (admin/admin)"
echo "   - Prometheus: http://localhost:9090" 