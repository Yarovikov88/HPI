from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from dotenv import load_dotenv
try:
    from logging_config import logger
except ImportError:
    from logging_config_simple import logger
from app.routers import auth, pro, questions, dashboard, recommendations, calendar, profile
# from app.routers import telegram  # Временно отключено
from sqlalchemy.exc import IntegrityError
import time
import os
from contextlib import asynccontextmanager
from app.db import create_indexes
from app.cache import get_redis

# Загружаем переменные окружения
load_dotenv()

# Глобальные переменные для метрик
request_count = 0
request_duration_sum = 0.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск
    logger.info("🚀 Запуск HPI API...")
    
    # Создаем индексы в БД
    try:
        await create_indexes()
        logger.info("✅ Индексы БД созданы/проверены")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка создания индексов: {e}")
    
    # Проверяем подключение к Redis
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        logger.info("✅ Redis подключен")
    except Exception as e:
        logger.warning(f"⚠️ Redis недоступен: {e}")
    
    yield
    
    # Завершение
    logger.info("🛑 Остановка HPI API...")

# Создаем FastAPI приложение с lifespan
app = FastAPI(
    title="HPI API",
    description="Human Performance Index API - Оптимизированная версия",
    version="2.0.0",
    lifespan=lifespan,
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

# Middleware для сжатия
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware для доверенных хостов
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # В продакшене ограничить конкретными доменами
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hpi.expert:8443",
        "https://www.hpi.expert:8443",
        "https://hpi.expert:2222",
        "https://www.hpi.expert:2222",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://83.147.192.188:5173",
        "http://83.147.192.188:3000",
        "http://172.18.0.1:5173",
        "http://172.18.0.1:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware для отслеживания производительности"""
    global request_count, request_duration_sum
    
    start_time = time.time()
    request_count += 1
    
    # Логируем запрос
    logger.info(f"📥 REQUEST: {request.method} {request.url} from {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Вычисляем время выполнения
        duration = time.time() - start_time
        request_duration_sum += duration
        
        # Логируем ответ с временем выполнения
        logger.info(f"📤 RESPONSE: {request.method} {request.url} status {response.status_code} in {duration:.3f}s")
        
        # Добавляем заголовки производительности
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-Count"] = str(request_count)
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ ERROR: {request.method} {request.url} failed in {duration:.3f}s: {str(e)}")
        raise

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений с детальным логированием"""
    logger.error(f"HTTPException: {exc.detail} (status={exc.status_code}) path={request.url}")
    return JSONResponse(
        status_code=exc.status_code, 
        content={
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации с детальным логированием"""
    logger.error(f"ValidationError: {exc.errors()} path={request.url}")
    return JSONResponse(
        status_code=422, 
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": str(request.url)
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Обработчик ошибок целостности БД"""
    msg = str(getattr(exc, "orig", exc)).lower()
    logger.error(f"IntegrityError: {msg} path={request.url}")
    
    # Определяем тип ошибки
    detail = "Unique constraint violated"
    if "email" in msg:
        detail = "Email already in use"
    elif "username" in msg:
        detail = "Username already in use"
    elif "telegram" in msg or "telegram_id" in msg:
        detail = "Telegram already in use"
    
    return JSONResponse(
        status_code=409, 
        content={
            "detail": detail,
            "path": str(request.url)
        }
    )

# Подключаем роутеры
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(pro.router, prefix="/api/pro", tags=["pro"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
# app.include_router(telegram.router)  # Временно отключено
app.include_router(calendar.router)
app.include_router(profile.router, prefix="/api", tags=["profile"])

@app.get("/")
async def read_root():
    """Корневой эндпоинт с информацией о системе"""
    return {
        "message": "HPI API v2.0 - Оптимизированная версия",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Redis кэширование",
            "Оптимизированная БД",
            "Метрики производительности",
            "Асинхронная обработка"
        ]
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        # Проверяем подключение к Redis
        redis_client = await get_redis()
        await redis_client.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"
    
    return {
        "status": "ok",
        "timestamp": time.time(),
        "redis": redis_status,
        "metrics": {
            "total_requests": request_count,
            "avg_response_time": request_duration_sum / max(request_count, 1)
        }
    }

@app.get("/metrics")
async def get_metrics():
    """Метрики производительности системы"""
    return {
        "requests": {
            "total": request_count,
            "avg_response_time": request_duration_sum / max(request_count, 1),
            "total_duration": request_duration_sum
        },
        "system": {
            "redis_connected": True,  # Упрощенно
            "database_connected": True
        }
    } 