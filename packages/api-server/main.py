import logging
import uvicorn
import argparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from . import database
from .routers import questions, answers, dashboard, pro_answers, pro_dashboard

# Строка для автоматического создания/проверки таблиц удалена
# в соответствии с требованием.
# Управление схемой БД должно производиться вручную.
# models.Base.metadata.create_all(bind=database.engine, checkfirst=True)

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# --- Инициализация FastAPI ---
app = FastAPI(
    title="HPI.EXPERT API",
    version="1.0.0",
    description="Центральный API для всех сервисов HPI.EXPERT"
)

# --- Настройка CORS ---
origins = [
    "http://localhost",
    "http://localhost:5173", # Адрес для Vite dev server
    "http://localhost:8001", # Потенциальный адрес для деплоя
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Подключение роутеров ---
app.include_router(questions.router, prefix="/api/v1")
app.include_router(answers.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(pro_answers.router, prefix="/api/v1")
app.include_router(pro_dashboard.router, prefix="/api/v1")

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