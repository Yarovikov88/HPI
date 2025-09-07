#!/bin/bash

echo "🔧 Исправляем OAuth2 настройки в backend..."

# 1. Находим файлы с OAuth2PasswordBearer
echo "�� Ищем файлы с OAuth2 настройками..."
find fastapi_app/backend -name "*.py" -exec grep -l "OAuth2PasswordBearer" {} \;

# 2. Исправляем tokenUrl
echo "📝 Исправляем tokenUrl..."
find fastapi_app/backend -name "*.py" -exec sed -i 's|tokenUrl="/api/auth/login"|tokenUrl="/api/login"|g' {} \;

# 3. Проверяем исправления
echo "✅ Проверяем исправления..."
find fastapi_app/backend -name "*.py" -exec grep -l "tokenUrl" {} \;

echo "🎉 OAuth2 настройки исправлены!"
echo "🔍 Теперь tokenUrl должен быть /api/login" 