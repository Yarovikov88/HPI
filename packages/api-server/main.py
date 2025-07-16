import logging
import uvicorn
import argparse

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, date

from . import models
from . import database
from .routers import questions, answers, dashboard, pro_answers, pro_dashboard, debug

# Строка для автоматического создания/проверки таблиц удалена
# в соответствии с требованием.
# Управление схемой БД должно производиться вручную.
# models.Base.metadata.create_all(bind=database.engine, checkfirst=True)

# --- Кастомный JSON-кодировщик для обработки datetime ---
def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

class CustomJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return super().render(content)

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# --- Инициализация FastAPI ---
app = FastAPI(
    title="HPI.EXPERT API",
    version="1.0.0",
    description="Центральный API для всех сервисов HPI.EXPERT",
    default_response_class=CustomJSONResponse,
)
app.json_serializer = json_serializer

# --- Настройка CORS ---
origins = [
    "http://localhost",
    "http://localhost:5173", # Адрес для Vite dev server
    "http://127.0.0.1:5173", # Адрес для Vite dev server (альтернативный)
    "http://localhost:5174", # Vite может занимать другие порты
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:8001", # Потенциальный адрес для деплоя
    "http://127.0.0.1:8000", # Разрешаем запросы с самого сервера
    "app-protocol://127.0.0.1:5173",
    "app-protocol://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Подключение роутеров ---
# Убираем все префиксы. Полные пути будут заданы в самих роутерах.
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(dashboard.router)
app.include_router(pro_answers.router)
app.include_router(pro_dashboard.router)
app.include_router(debug.router)

# --- Эндпоинты ---
@app.get("/")
def read_root():
    """Тестовый эндпоинт для проверки работы сервера."""
    logging.info("Root endpoint was called.")
    return {"message": "HPI.EXPERT API is running!"}

# --- Запуск сервера ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HPI.EXPERT API Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    logging.info(f"Starting uvicorn server on port {args.port}...")
    uvicorn.run("packages.api-server.main:app", host="0.0.0.0", port=args.port, reload=True) 