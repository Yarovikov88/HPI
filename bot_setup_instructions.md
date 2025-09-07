# Инструкция по настройке Telegram-ботов для HPI.EXPERT

## Обзор системы

Система состоит из двух ботов:

1. **Dashboard Bot** (`myhpibot`) - генерирует дашборды пользователей, принимает обратную связь и автоматически выдает PRO-статус
2. **Channel Bot** (`channel_bot`) - отслеживает пересланные сообщения в канале

## Шаг 1: Создание ботов в Telegram

### Dashboard Bot
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Выберите имя: `HPI Dashboard Bot`
4. Выберите username: `myhpibot`
5. Сохраните полученный токен

### Channel Bot
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Выберите имя: `HPI Channel Bot`
4. Выберите username: `hpi_channel_bot`
5. Сохраните полученный токен

## Шаг 2: Настройка канала

1. Создайте канал `@hpi_expert_chat`
2. Добавьте Channel Bot как администратора канала
3. Дайте боту права на чтение сообщений

## Шаг 3: Установка зависимостей

```bash
pip install python-telegram-bot requests
```

## Шаг 4: Настройка конфигурации

### Dashboard Bot (`dashboard_bot.py`) - @myhpibot
Замените в файле:
```python
BOT_TOKEN = "YOUR_DASHBOARD_BOT_TOKEN"  # Ваш токен от @BotFather
API_BASE_URL = "https://hpi.expert/api"  # URL вашего API
CHANNEL_LINK = "https://t.me/hpi_expert_chat"  # Ссылка на ваш канал
```

### Channel Bot (`channel_bot.py`)
Замените в файле:
```python
BOT_TOKEN = "YOUR_CHANNEL_BOT_TOKEN"  # Ваш токен от @BotFather
CHANNEL_ID = "@hpi_expert_chat"  # ID вашего канала
API_BASE_URL = "https://hpi.expert/api"  # URL вашего API
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"  # ID чата админа для уведомлений
```

## Шаг 5: Настройка API интеграции

### Для Dashboard Bot
Нужно реализовать функцию `get_user_token()` для получения токена пользователя:

```python
def get_user_token(self, user_id: str):
    # Здесь должна быть логика получения токена пользователя из базы данных
    # Например:
    # return database.get_user_token(user_id)
    pass
```

### Для Channel Bot
Нужно настроить админский токен для выдачи PRO-статуса:

```python
headers={"Authorization": "Bearer YOUR_ADMIN_TOKEN"}
```

## Шаг 6: Запуск ботов

### Dashboard Bot
```bash
python dashboard_bot.py
```

### Channel Bot
```bash
python channel_bot.py
```

## Шаг 7: Тестирование

### Тестирование дашборда
1. Откройте сайт HPI.EXPERT
2. Перейдите на страницу "Получить PRO-статус"
3. Выберите "Поделиться результатом"
4. Нажмите кнопку "Получить дашборд в Telegram"
5. В Telegram нажмите "Start"
6. Получите дашборд
7. Перешлите его в канал @hpi_expert_chat
8. Проверьте, что PRO-статус выдан

### Тестирование обратной связи
1. Напишите боту @myhpibot команду `/feedback`
2. Бот запросит текст обратной связи
3. Напишите ваш отзыв/предложение/сообщение об ошибке
4. Бот запросит фото/скриншот (или отправьте `/skip` для пропуска)
5. Отправьте фото или команду `/skip`
6. Проверьте, что сообщение и фото пришли в админский чат
7. **Проверьте, что пользователю выдан PRO-статус**

## Структура UTM-метки

UTM-метка имеет формат: `user_{user_id}_{timestamp}`

Пример: `user_1044_1734876543210`

## Логирование

Боты ведут логи в консоль. Для продакшена рекомендуется настроить файловое логирование:

```python
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
```

## Безопасность

1. Никогда не коммитьте токены в Git
2. Используйте переменные окружения для токенов
3. Ограничьте права ботов в канале
4. Регулярно обновляйте токены

## Мониторинг

Рекомендуется настроить мониторинг ботов:
- Проверка работоспособности
- Логирование ошибок
- Уведомления о сбоях
- Статистика использования 