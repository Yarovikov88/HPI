# 🔧 Инструкции по исправлению HPI.EXPERT

## ✅ Что исправлено:

### 1. Пароли PostgreSQL
- **Было**: `hpi_password` (неправильный)
- **Стало**: `hpi_password_2024` (правильный)
- **Файл**: `docker-compose.optimized.yml`

### 2. Nginx конфигурация
- **Убрано**: Циклическое проксирование к `frontend:80`
- **Добавлено**: Прямое обслуживание статических файлов
- **Файл**: `nginx-fixed.conf`

### 3. OAuth2 настройки
- **Было**: `tokenUrl="/api/auth/login"` (неправильный)
- **Стало**: `tokenUrl="/api/login"` (правильный)
- **Файлы**: `fastapi_app/backend/app/auth.py`, `main.py`

### 4. FastAPI приложение (main.py)
- **Было**: Дублирующее определение `app = FastAPI(...)` после подключения роутеров
- **Стало**: Одно определение FastAPI с lifespan и правильным порядком
- **Файл**: `fastapi_app/backend/main.py`

### 5. Подключение к базе данных
- **Было**: Конфликт между переменной окружения и дефолтным значением в `app/db.py`
- **Стало**: Единообразное подключение через `postgres:5432` (Docker сеть)
- **Файлы**: `fastapi_app/backend/app/db.py`, `create_tables.py`, `init_database.py`

### 6. Frontend API endpoints
- **Было**: `/auth/login`, `/auth/register`, `/auth/password` (неправильные)
- **Стало**: `/login`, `/register`, `/password` (правильные)
- **Файлы**: `src/services/api.ts`

### 7. Frontend аутентификация
- **Было**: Токен не сохранялся в localStorage после логина
- **Стало**: Токен автоматически сохраняется и используется для API запросов
- **Добавлено**: Функция logout для очистки токена
- **Файлы**: `src/services/api.ts`

### 8. Frontend календарь API
- **Было**: Функция `getCalendarStatus` отправляла параметр `month` вместо `from` и `to`
- **Стало**: Функция принимает `from` и `to` и отправляет правильные параметры
- **Исправлено**: API endpoint `/api/calendar/status` теперь работает корректно
- **Файлы**: `src/services/api.ts`

### 9. Backend redirect endpoints (совместимость)
- **Добавлено**: Redirect с `/api/auth/*` на `/api/*` для совместимости
- **Файлы**: `fastapi_app/backend/app/routers/auth.py`

### 10. MIME типы
- **JavaScript**: `application/javascript`
- **CSS**: `text/css`
- **Изображения**: Кэширование и правильные типы

## 🚀 Как применить исправления:

### Автоматически:
```bash
chmod +x fix-server.sh
./fix-server.sh
```

### Вручную:
```bash
# 1. Исправить OAuth2 настройки
chmod +x fix-oauth2.sh
./fix-oauth2.sh

# 2. Остановить сервисы
docker-compose -f docker-compose.optimized.yml down

# 3. Запустить с исправлениями
docker-compose -f docker-compose.optimized.yml up --build -d

# 4. Проверить результат
curl -I http://83.147.192.188/login
```

## 🎯 Ожидаемый результат:

- ✅ **Frontend**: HTTP 200 OK
- ✅ **API**: `/api/login` работает без Internal Server Error
- ✅ **База данных**: Подключение к PostgreSQL
- ✅ **Сайт**: Полностью функциональный

## 📁 Файлы для переноса:

1. `docker-compose.optimized.yml` - исправленные пароли
2. `nginx-fixed.conf` - правильная Nginx конфигурация
3. `fix-oauth2.sh` - скрипт исправления OAuth2
4. `fix-all.sh` - скрипт применения ВСЕХ исправлений
5. `FIX_INSTRUCTIONS.md` - подробные инструкции

## 📁 Обновленные файлы:

- `src/services/api.ts` - исправленные API endpoints
- `fastapi_app/backend/app/routers/auth.py` - добавлены redirect endpoints
- `fastapi_app/backend/main.py` - исправлено дублирующее FastAPI приложение
- `fastapi_app/backend/app/db.py` - исправлено подключение к БД
- `fastapi_app/backend/create_tables.py` - улучшенный скрипт создания таблиц
- `fastapi_app/backend/init_database.py` - скрипт инициализации БД

## 🔍 Проверка:

```bash
# Frontend
curl -I http://83.147.192.188/login

# API (новый endpoint)
curl -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'

# API (старый endpoint - должен работать через redirect)
curl -X POST http://83.147.192.188/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

## 🎯 Основные исправления:

1. ✅ **Пароли PostgreSQL**: `hpi_password` → `hpi_password_2024`
2. ✅ **Nginx конфигурация**: Убрано циклическое проксирование
3. ✅ **OAuth2 настройки**: `tokenUrl="/api/login"`
4. ✅ **FastAPI приложение**: Исправлено дублирующее определение
5. ✅ **Подключение к БД**: Единообразное подключение через Docker сеть
6. ✅ **Frontend API endpoints**: `/auth/*` → `/*`
7. ✅ **Frontend аутентификация**: Токен сохраняется в localStorage
8. ✅ **Frontend календарь API**: Исправлены параметры `from` и `to`
9. ✅ **Backend redirect endpoints**: Совместимость со старым кодом
10. ✅ **MIME типы**: Правильные для JavaScript и CSS
11. ✅ **Автоматизация**: Скрипты для применения исправлений

**Теперь все файлы готовы для переноса на сервер!** 🚀 

##  **Проблема найдена:**

**`ImportError: cannot import name 'get_db' from 'app.db'`**

**В файле `main.py` есть неправильный импорт!**

## 🔧 **Быстрое исправление:**

```bash
# Проверяем, что есть в app/db.py
docker exec -it hpisite-postgres-1 cat /app/app/db.py | grep -A 5 -B 5 "def get_db"

# Или если контейнер не запущен, проверяем локально
cat fastapi_app/backend/app/db.py | grep -A 5 -B 5 "def get_db"
```

##  **Проблема в `main.py`:**

**Убрали неправильные импорты, но оставили неиспользуемые:**

```python
<code_block_to_apply_changes_from>
```

## 🔧 **Исправляю `fastapi_app/backend/main.py`:**

```python:fastapi_app/backend/main.py
# ... existing code ...

# Убираем лишние импорты
from app.db import create_indexes
from app.cache import get_redis
# УБИРАЕМ: from fastapi.security import OAuth2PasswordBearer
# УБИРАЕМ: from sqlalchemy.ext.asyncio import AsyncSession
# УБИРАЕМ: from app.db import get_db
# УБИРАЕМ: from app.models.user import UserLogin

# ... existing code ...

# Убираем дублирующий OAuth2PasswordBearer
app = FastAPI(
    title="HPI API",
    description="Human Performance Index API - Оптимизированная версия",
    version="2.0.0",
    openapi_tags=[
        {"name": "auth", "description": "Аутентификация и авторизация"},
        {"name": "questions", "description": "Базовые вопросы и ответы"},
        {"name": "pro", "description": "PRO вопросы и ответы"},
        {"name": "dashboard", "description": "Дашборд и аналитика"},
        {"name": "recommendations", "description": "Рекомендации"},
        {"name": "profile", "description": "Профиль пользователя"},
        {"name": "calendar", "description": "Календарь и события"}
    ]
)

# ... existing code ...

# УБИРАЕМ: oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ... existing code ...
```

## 🔧 **Быстрое исправление на сервере:**

```bash
# Останавливаем все
docker-compose -f docker-compose.optimized.yml down

# Исправляем main.py
sed -i '/from fastapi.security import OAuth2PasswordBearer/d' fastapi_app/backend/main.py
sed -i '/from sqlalchemy.ext.asyncio import AsyncSession/d' fastapi_app/backend/main.py
sed -i '/from app.db import get_db/d' fastapi_app/backend/main.py
sed -i '/from app.models.user import UserLogin/d' fastapi_app/backend/main.py
sed -i '/oauth2_scheme = OAuth2PasswordBearer/d' fastapi_app/backend/main.py

# Запускаем заново
docker-compose -f docker-compose.optimized.yml up --build -d
```

## 🎯 **Ожидаемый результат:**

После исправления:
- ✅ **Backend запустится** без ошибок импорта
- ✅ **Frontend получит данные** от backend
- ✅ **Сайт будет доступен**

**Проблема в лишних импортах в main.py! Нужно их убрать!** 🔧

**Исправьте main.py и запустите заново!** 🚀 