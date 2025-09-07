#!/bin/bash

echo "🚀 Запуск HPI Backend..."

# Создаем базу данных и таблицы
echo "📊 Инициализация базы данных..."
python create_tables.py

# Запускаем приложение
echo "🌐 Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 