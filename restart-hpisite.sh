#!/bin/bash

echo "🔄 Перезапуск системы HPI88..."

# Остановка и удаление старых контейнеров
echo "⏹️  Остановка старых контейнеров..."
docker stop hpisite-frontend-1 hpisite-backend-1 hpisite-postgres-1 hpisite-redis-1 hpisite-celery-1 hpisite-celery-beat-1 hpisite-grafana-1 hpisite-prometheus-1 hpi_nginx 2>/dev/null || true

echo "🗑️  Удаление старых контейнеров..."
docker rm hpisite-frontend-1 hpisite-backend-1 hpisite-postgres-1 hpisite-redis-1 hpisite-celery-1 hpisite-celery-beat-1 hpisite-grafana-1 hpisite-prometheus-1 hpi_nginx 2>/dev/null || true

# Удаление старых образов
echo "🧹 Очистка старых образов..."
docker rmi hpisite-frontend hpisite-backend hpisite-celery hpisite-celery-beat 2>/dev/null || true

# Создание папки для логов
echo "📁 Создание папки для логов..."
mkdir -p logs/nginx

# Сборка и запуск новых контейнеров
echo "🏗️  Сборка и запуск новых контейнеров..."
docker-compose -f docker-compose.hpisite.yml up -d --build

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 30

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
docker-compose -f docker-compose.hpisite.yml ps

echo "✅ Система HPI88 перезапущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   - Сайт: http://localhost"
echo "   - API: http://localhost/api"
echo "   - Grafana: http://localhost:3001 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo ""
echo "📊 Логи:"
echo "   docker-compose -f docker-compose.hpisite.yml logs -f" 