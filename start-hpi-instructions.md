# 🚀 Запуск всего проекта HPI.EXPERT одной командой

## 📋 Варианты запуска

### Вариант 1: Только боты (если сайт уже работает)
```bash
# Запустить только Telegram ботов
./start-hpi.sh start

# Или напрямую через docker-compose
docker-compose -f docker-compose.bots-only.yml up -d
```

### Вариант 2: Полный проект (сайт + боты + БД)
```bash
# Запустить всё (сайт + боты + база данных)
docker-compose -f docker-compose.full.yml up -d
```

## 🛠️ Универсальный скрипт управления

Создан скрипт `start-hpi.sh` для удобного управления всем проектом:

### Установка (Linux/Mac)
```bash
chmod +x start-hpi.sh
```

### Использование
```bash
# Запустить проект
./start-hpi.sh start

# Остановить проект
./start-hpi.sh stop

# Перезапустить проект
./start-hpi.sh restart

# Проверить статус
./start-hpi.sh status

# Посмотреть логи
./start-hpi.sh logs

# Пересобрать проект
./start-hpi.sh rebuild

# Показать справку
./start-hpi.sh help
```

## 🐳 Docker Compose файлы

### `docker-compose.bots-only.yml`
- **Назначение**: Только Telegram боты
- **Использование**: Когда сайт уже работает отдельно
- **Команда**: `docker-compose -f docker-compose.bots-only.yml up -d`

### `docker-compose.full.yml`
- **Назначение**: Полный проект (фронтенд + бэкенд + БД + боты)
- **Использование**: Для полного развертывания
- **Команда**: `docker-compose -f docker-compose.full.yml up -d`

### `docker-compose.bots.yml`
- **Назначение**: Только боты (старая версия)
- **Использование**: Для совместимости
- **Команда**: `docker-compose -f docker-compose.bots.yml up -d`

## 📊 Структура проекта

```
HPI88/
├── start-hpi.sh                    # Универсальный скрипт управления
├── docker-compose.full.yml         # Полный проект
├── docker-compose.bots-only.yml    # Только боты
├── docker-compose.bots.yml         # Только боты (старая версия)
├── Dockerfile.bots                 # Образ для ботов
├── dashboard_bot.py                # Dashboard Bot
├── channel_bot.py                  # Channel Bot
├── start_bots.py                   # Скрипт запуска ботов
├── requirements.txt                # Python зависимости
└── logs/                           # Логи ботов
```

## 🔧 Настройка

### Переменные окружения
Создайте файл `.env` в корне проекта:

```env
# Токены ботов
DASHBOARD_BOT_TOKEN=8479171638:AAEsGz-TcfxbDkfiJ4a5D4Fr24BUdQmarmM
CHANNEL_BOT_TOKEN=8371425767:AAHE31OsvZSftj2YNxFa8oaSV7YShvdPk6w

# API конфигурация
API_BASE_URL=https://hpi.expert/api

# Канал
CHANNEL_ID=@hpi_expert_chat
CHANNEL_LINK=https://t.me/hpi_expert_chat

# Админ (опционально)
ADMIN_CHAT_ID=

# База данных (для полного проекта)
DATABASE_URL=postgresql://user:password@db:5432/hpi
SECRET_KEY=your-secret-key
```

## 🚀 Быстрый старт

### 1. Только боты (рекомендуется)
```bash
# Если сайт уже работает
./start-hpi.sh start
```

### 2. Полный проект
```bash
# Если нужно запустить всё с нуля
docker-compose -f docker-compose.full.yml up -d
```

### 3. Проверка
```bash
# Проверить статус
./start-hpi.sh status

# Посмотреть логи
./start-hpi.sh logs
```

## 🔍 Мониторинг

### Проверка работы ботов
```bash
# Проверить Dashboard Bot
curl "https://api.telegram.org/bot8479171638:AAEsGz-TcfxbDkfiJ4a5D4Fr24BUdQmarmM/getMe"

# Проверить Channel Bot
curl "https://api.telegram.org/bot8371425767:AAHE31OsvZSftj2YNxFa8oaSV7YShvdPk6w/getMe"
```

### Логи
```bash
# Все логи
./start-hpi.sh logs

# Логи конкретного сервиса
docker-compose -f docker-compose.bots-only.yml logs hpi-bots
```

## 🛠️ Устранение неполадок

### Боты не запускаются
```bash
# Проверить логи
./start-hpi.sh logs

# Пересобрать
./start-hpi.sh rebuild

# Проверить токены
curl "https://api.telegram.org/bot/YOUR_TOKEN/getMe"
```

### Сайт не доступен
```bash
# Проверить статус всех контейнеров
./start-hpi.sh status

# Проверить порты
netstat -tulpn | grep :80
netstat -tulpn | grep :443
```

## 📝 Примеры использования

### Разработка
```bash
# Запустить только боты для разработки
./start-hpi.sh start

# Смотреть логи в реальном времени
./start-hpi.sh logs
```

### Продакшн
```bash
# Запустить полный проект
docker-compose -f docker-compose.full.yml up -d

# Настроить автозапуск
echo "cd /path/to/HPI88 && ./start-hpi.sh start" >> ~/.bashrc
```

### Обновление
```bash
# Остановить проект
./start-hpi.sh stop

# Пересобрать и запустить
./start-hpi.sh rebuild
```

## ✨ Преимущества

- **Одна команда** для запуска всего проекта
- **Автоматический выбор** конфигурации
- **Цветной вывод** для удобства
- **Graceful shutdown** для корректного завершения
- **Мониторинг здоровья** контейнеров
- **Логирование** в файлы
- **Простота управления** через единый скрипт 