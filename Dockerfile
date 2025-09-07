FROM node:18-alpine

WORKDIR /app

# Копирование package файлов
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Установка serve для раздачи статических файлов
RUN npm install -g serve

# Открытие порта
EXPOSE 3000

# Команда запуска
CMD ["serve", "-s", "dist", "-l", "3000"] 