# FastAPI HPI Project

Проект FastAPI с системой регистрации и авторизации пользователей.

## Структура проекта

```
├── app/
│   ├── __init__.py
│   ├── db.py              # Подключение к базе данных
│   ├── models.py          # SQLAlchemy модели
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py        # Роуты авторизации
│   └── schemas/
│       ├── __init__.py
│       └── auth.py        # Pydantic схемы
├── main.py                # Точка входа FastAPI
├── requirements.txt       # Зависимости Python
├── Dockerfile            # Dockerfile для FastAPI
├── docker-compose.yml    # Docker Compose конфигурация
├── nginx.conf           # Конфигурация nginx
├── create_tables.py     # Скрипт создания таблиц
└── README.md            # Этот файл
```

## Запуск

1. **Соберите и запустите контейнеры:**
   ```bash
   docker compose up --build
   ```

2. **Создайте таблицы в базе данных (один раз):**
   ```bash
   docker exec -it fastapi_app python create_tables.py
   ```

3. **Откройте в браузере:**
   - API: http://localhost/
   - Документация: http://localhost/docs

## API Endpoints

- `POST /api/auth/register` - Регистрация пользователя
- `POST /api/auth/login` - Вход пользователя

## Технологии

- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Docker & Docker Compose
- Nginx
- JWT для авторизации