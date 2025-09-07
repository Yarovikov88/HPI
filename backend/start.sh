#!/bin/bash

echo "🚀 Запуск HPI Backend..."

# Инициализируем базу данных
echo "📊 Инициализация базы данных..."
python3 init_db.py

if [ $? -eq 0 ]; then
    echo "✅ База данных инициализирована успешно!"
else
    echo "❌ Ошибка инициализации базы данных!"
    exit 1
fi

# Запускаем приложение
echo "🌐 Запуск FastAPI приложения..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 