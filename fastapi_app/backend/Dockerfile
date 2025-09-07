FROM python:3.11-slim

# Устанавливаем curl для health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для логов и celery с максимальными правами
RUN mkdir -p /app/logs && chmod 777 /app/logs
RUN mkdir -p /app/celery && chmod 777 /app/celery

# Создаем пользователя
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя
USER appuser

EXPOSE 8000

# Запускаем напрямую через bash
CMD ["bash", "-c", "python create_tables.py && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"] 