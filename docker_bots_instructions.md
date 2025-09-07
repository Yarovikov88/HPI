# Запуск Telegram-ботов в Docker

## 🐳 Быстрый старт

### 1. Сборка и запуск
```bash
# Собрать и запустить оба бота в одном контейнере
docker-compose -f docker-compose.bots.yml up -d

# Посмотреть логи
docker-compose -f docker-compose.bots.yml logs -f

# Остановить ботов
docker-compose -f docker-compose.bots.yml down
```

### 2. Проверка статуса
```bash
# Статус контейнера
docker-compose -f docker-compose.bots.yml ps

# Проверка логов
docker-compose -f docker-compose.bots.yml logs hpi-bots
```

## 📁 Структура файлов

```
├── dashboard_bot.py          # Бот для генерации дашбордов
├── channel_bot.py            # Бот для канала
├── start_bots.py             # Скрипт запуска обоих ботов
├── Dockerfile.bots           # Docker образ для ботов
├── docker-compose.bots.yml   # Docker Compose конфигурация
├── requirements.txt          # Python зависимости
└── logs/                     # Папка для логов (создается автоматически)
```

## ⚙️ Конфигурация

### Переменные окружения

Боты используют переменные окружения из `docker-compose.bots.yml`:

- `DASHBOARD_BOT_TOKEN` - токен Dashboard Bot
- `CHANNEL_BOT_TOKEN` - токен Channel Bot  
- `API_BASE_URL` - URL вашего API
- `CHANNEL_ID` - ID канала
- `ADMIN_CHAT_ID` - ID чата админа (опционально)

### Изменение конфигурации

1. Отредактируйте `docker-compose.bots.yml`
2. Перезапустите контейнер:
```bash
docker-compose -f docker-compose.bots.yml down
docker-compose -f docker-compose.bots.yml up -d
```

## 🔍 Мониторинг

### Просмотр логов
```bash
# Все логи
docker-compose -f docker-compose.bots.yml logs

# Логи в реальном времени
docker-compose -f docker-compose.bots.yml logs -f

# Логи с временными метками
docker-compose -f docker-compose.bots.yml logs -t
```

### Проверка статуса
```bash
# Статус контейнера
docker-compose -f docker-compose.bots.yml ps

# Проверка здоровья
docker-compose -f docker-compose.bots.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## 🛠️ Разработка

### Пересборка после изменений
```bash
# Пересобрать образ
docker-compose -f docker-compose.bots.yml build

# Перезапустить с новой сборкой
docker-compose -f docker-compose.bots.yml up -d --build
```

### Отладка
```bash
# Запуск в интерактивном режиме
docker-compose -f docker-compose.bots.yml run --rm hpi-bots python start_bots.py

# Вход в контейнер
docker exec -it hpi-telegram-bots bash

# Запуск отдельных ботов для тестирования
docker exec -it hpi-telegram-bots python dashboard_bot.py
docker exec -it hpi-telegram-bots python channel_bot.py
```

## 🔧 Настройка API интеграции

### Dashboard Bot
Нужно реализовать функцию `get_user_token()` в `dashboard_bot.py`:

```python
def get_user_token(self, user_id: str):
    # Подключение к вашей базе данных
    # return database.get_user_token(user_id)
    pass
```

### Channel Bot  
Нужно настроить админский токен в `channel_bot.py`:

```python
headers={"Authorization": "Bearer YOUR_ADMIN_TOKEN"}
```

## 🚀 Продакшн

### Автозапуск
```bash
# Добавить в systemd (Linux)
sudo systemctl enable docker
sudo systemctl start docker

# Добавить в автозапуск
echo "docker-compose -f /path/to/docker-compose.bots.yml up -d" >> ~/.bashrc
```

### Безопасность
1. Используйте секреты Docker для токенов
2. Ограничьте права контейнера
3. Настройте файрвол
4. Регулярно обновляйте образы

### Мониторинг
```bash
# Создать скрипт мониторинга
cat > monitor_bots.sh << 'EOF'
#!/bin/bash
if ! docker-compose -f docker-compose.bots.yml ps | grep -q "Up"; then
    echo "Боты остановлены, перезапускаю..."
    docker-compose -f docker-compose.bots.yml up -d
fi
EOF

chmod +x monitor_bots.sh

# Добавить в cron
echo "*/5 * * * * /path/to/monitor_bots.sh" | crontab -
```

## 🐛 Устранение неполадок

### Бот не отвечает
```bash
# Проверить логи
docker-compose -f docker-compose.bots.yml logs hpi-bots

# Проверить токен
curl "https://api.telegram.org/bot/YOUR_TOKEN/getMe"
```

### Ошибки API
```bash
# Проверить доступность API
curl "https://hpi.expert/api/profile"

# Проверить сеть контейнера
docker exec hpi-telegram-bots ping hpi.expert
```

### Проблемы с каналом
1. Убедитесь, что Channel Bot добавлен в канал как администратор
2. Проверьте права бота на чтение сообщений
3. Убедитесь, что канал публичный или бот имеет доступ

## ✨ Преимущества единого контейнера

- **Простота управления** - один контейнер вместо двух
- **Синхронизированный запуск** - оба бота запускаются одновременно
- **Единое логирование** - все логи в одном месте
- **Меньше ресурсов** - один процесс вместо двух
- **Graceful shutdown** - корректное завершение обоих ботов 