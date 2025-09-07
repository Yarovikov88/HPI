FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Делаем скрипт запуска исполняемым
RUN chmod +x start.sh

# Открываем порт
EXPOSE 8000

# Запускаем приложение с инициализацией БД
CMD ["./start.sh"] 