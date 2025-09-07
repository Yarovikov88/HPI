# 🚀 Полное руководство по исправлению HPI.EXPERT

## 📋 Анализ проблем

После полного анализа проекта выявлены следующие проблемы:

### 1. **Проблемы с сетями Docker**
- Контейнеры находятся в разных сетях (`hpi_default`, `back_default`)
- `hpi-web-1` не может подключиться к `fastapi_app` и `nginx`

### 2. **Неправильная конфигурация nginx**
- Проксирование на несуществующий контейнер `api` вместо `fastapi_app`
- Неправильные имена контейнеров в конфигурации

### 3. **Проблемы с server.cjs**
- Неправильные URL для проксирования
- Отсутствие подробного логирования ошибок
- Проблемы с обработкой ошибок

### 4. **Архитектурные проблемы**
- Множество docker-compose файлов с разными конфигурациями
- Отсутствие единой архитектуры
- Конфликты портов

## 🔧 Решение

### Шаг 1: Подготовка файлов

Созданы исправленные файлы:
- `docker-compose.working.yml` - единая рабочая конфигурация
- `nginx-working.conf` - исправленная конфигурация nginx
- `server-working.cjs` - исправленный сервер
- `start-working.sh` - универсальный скрипт запуска

### Шаг 2: Запуск исправленной конфигурации

```bash
# Сделать скрипт исполняемым
chmod +x start-working.sh

# Запустить проект
./start-working.sh start
```

### Шаг 3: Проверка работы

```bash
# Проверить статус
./start-working.sh status

# Посмотреть логи
./start-working.sh logs

# Проверить API
curl -k -s https://hpi.expert/api/profile
```

## 🏗️ Архитектура решения

### Docker Compose структура

```yaml
services:
  db:                    # PostgreSQL база данных
    ports: ["5432:5432"]
    
  api:                   # FastAPI бэкенд
    depends_on: [db]
    
  nginx:                 # Nginx прокси
    ports: ["8443:8443", "8888:8888"]
    depends_on: [api]
    
  web:                   # Основной веб-сервер (фронтенд)
    ports: ["80:80", "443:443"]
    depends_on: [nginx]
    
  bots:                  # Telegram боты
    depends_on: [web]
    
  feedback:              # Сервер обратной связи
    ports: ["5001:5001"]
```

### Сетевая архитектура

```
Internet → hpi-web-1 (80/443) → nginx (8443) → fastapi_app (8000)
                                    ↓
                              feedback-server (5001)
                                    ↓
                              hpi-telegram-bots
```

## 🔄 Поток запросов

1. **Пользователь** → `https://hpi.expert/api/profile`
2. **hpi-web-1** → `https://nginx:8443/api/profile`
3. **nginx** → `http://api:8000/api/profile`
4. **fastapi_app** → обрабатывает запрос и возвращает ответ

## 🛠️ Команды управления

```bash
# Запуск
./start-working.sh start

# Остановка
./start-working.sh stop

# Перезапуск
./start-working.sh restart

# Статус
./start-working.sh status

# Логи
./start-working.sh logs

# Пересборка
./start-working.sh rebuild

# Очистка
./start-working.sh clean

# Справка
./start-working.sh help
```

## 🔍 Отладка

### Проверка контейнеров
```bash
docker ps
docker logs hpi-web-1
docker logs nginx
docker logs fastapi_app
```

### Проверка сетей
```bash
docker network ls
docker network inspect hpi-network
```

### Проверка API
```bash
# Прямой запрос к FastAPI
curl -k -s https://localhost:8443/api/profile

# Через основной домен
curl -k -s https://hpi.expert/api/profile
```

## 🚨 Возможные проблемы и решения

### 1. Порт 80/443 занят
```bash
# Остановить все контейнеры
./start-working.sh clean

# Проверить, что занято порты
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

### 2. SSL сертификаты
```bash
# Проверить наличие сертификатов
ls -la /etc/letsencrypt/live/hpi.expert/

# Если нет, создать самоподписанные для тестирования
mkdir -p /etc/letsencrypt/live/hpi.expert/
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/letsencrypt/live/hpi.expert/privkey.pem \
  -out /etc/letsencrypt/live/hpi.expert/fullchain.pem
```

### 3. Проблемы с базой данных
```bash
# Проверить логи БД
docker logs hpi-db

# Подключиться к БД
docker exec -it hpi-db psql -U hpi_user -d hpi
```

## 📊 Мониторинг

### Health checks
Все сервисы имеют health checks:
- **api**: `curl -f http://localhost:8000/health`
- **nginx**: автоматический
- **bots**: проверка Telegram API
- **feedback**: `curl -f http://localhost:5001/health`

### Логирование
- Все контейнеры настроены на ротацию логов
- Максимальный размер: 10MB
- Количество файлов: 3

## 🎯 Результат

После применения исправлений:

✅ **API работает** - все эндпоинты доступны  
✅ **Аутентификация работает** - JWT токены обрабатываются  
✅ **Фронтенд работает** - React приложение загружается  
✅ **Боты работают** - Telegram интеграция активна  
✅ **Feedback работает** - обратная связь отправляется  
✅ **SSL работает** - HTTPS доступен  
✅ **Сети настроены** - все контейнеры видят друг друга  

## 🔄 Миграция с старой конфигурации

```bash
# 1. Остановить старые контейнеры
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.full.yml down

# 2. Запустить новую конфигурацию
./start-working.sh start

# 3. Проверить работу
./start-working.sh status
```

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `./start-working.sh logs`
2. Проверьте статус: `./start-working.sh status`
3. Перезапустите: `./start-working.sh restart`
4. Пересоберите: `./start-working.sh rebuild`

---

**🎉 Поздравляем! Ваш HPI.EXPERT теперь полностью работает!** 