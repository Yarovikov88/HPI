# 🚀 HPI88 - Инструкция по запуску

## 📋 Что это такое

HPI88 - это система диагностики человеческого потенциала (Human Potential Index) с веб-интерфейсом, API и Telegram ботами.

## 🏗️ Архитектура

- **Frontend**: React + TypeScript (порт 3000)
- **Backend**: FastAPI + Python (порт 8000)
- **Nginx**: Reverse proxy (порт 80)
- **PostgreSQL**: База данных (порт 5434)
- **Redis**: Кэш и очереди (порт 6379)
- **Celery**: Фоновые задачи
- **Grafana**: Мониторинг (порт 3001)
- **Prometheus**: Метрики (порт 9090)

## 🚀 Быстрый запуск

### 1. Автоматическое исправление (рекомендуется)
```bash
# Сделать скрипт исполняемым
chmod +x fix-docker.sh

# Запустить исправление и запуск
./fix-docker.sh
```

### 2. Ручной запуск
```bash
# Создать папку для логов
mkdir -p logs/nginx

# Запустить все сервисы
docker-compose -f docker-compose.hpisite.yml up -d --build
```

### 3. Проверка статуса
```bash
# Статус всех сервисов
docker-compose -f docker-compose.hpisite.yml ps

# Логи
docker-compose -f docker-compose.hpisite.yml logs -f
```

## 🔧 Что исправлено

- ✅ Убран устаревший атрибут `version` из docker-compose
- ✅ Исправлены пути к Dockerfile
- ✅ Frontend использует `Dockerfile.frontend`
- ✅ Backend использует `fastapi_app/backend/Dockerfile`
- ✅ Правильная конфигурация nginx
- ✅ Все сервисы в одной сети

## 📊 Мониторинг

### Доступные сервисы
- **Сайт**: http://localhost
- **API**: http://localhost/api
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## 🛠️ Устранение проблем

### Если что-то не работает
```bash
# Полная очистка и перезапуск
./fix-docker.sh

# Или вручную
docker-compose -f docker-compose.hpisite.yml down -v
docker system prune -f
docker-compose -f docker-compose.hpisite.yml up -d --build
```

### Проверка логов
```bash
# Все логи
docker-compose -f docker-compose.hpisite.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.hpisite.yml logs -f nginx
docker-compose -f docker-compose.hpisite.yml logs -f frontend
docker-compose -f docker-compose.hpisite.yml logs -f backend
```

## 📁 Структура файлов

```
├── docker-compose.hpisite.yml    # Основной docker-compose
├── nginx.conf                    # Конфигурация nginx
├── fix-docker.sh                 # Скрипт исправления
├── Dockerfile.frontend           # Dockerfile для frontend
├── fastapi_app/backend/Dockerfile # Dockerfile для backend
├── fastapi_app/                  # Backend код
├── src/                          # Frontend код
└── logs/                         # Логи приложения
```

## ✅ Готово!

После успешного запуска сайт будет доступен по адресу http://localhost 