#!/bin/bash

echo "🔧 Исправляем проблему с календарем API..."

# 1. Проверяем, что мы в правильной директории
if [ ! -f "src/services/api.ts" ]; then
    echo "❌ Ошибка: файл src/services/api.ts не найден!"
    echo "   Запустите скрипт из корневой директории проекта"
    exit 1
fi

# 2. Проверяем текущую функцию getCalendarStatus
echo "📋 Проверяем текущую функцию getCalendarStatus..."
if grep -q "getCalendarStatus.*month" src/services/api.ts; then
    echo "❌ Найдена старая версия с параметром 'month'"
    echo "   Нужно исправить на 'from' и 'to'"
else
    echo "✅ Функция уже исправлена"
fi

# 3. Показываем, как должна выглядеть функция
echo ""
echo "📝 Правильная функция должна выглядеть так:"
echo "   getCalendarStatus: async (from: string, to: string) => {"
echo "       const response = await axiosInstance.get('/calendar/status', { params: { from, to } });"
echo "   }"

# 4. Проверяем, есть ли проблемы
echo ""
echo "🔍 Проверяем наличие проблем..."
if grep -q "params.*month" src/services/api.ts; then
    echo "❌ Проблема найдена: параметр 'month' в API вызове"
    echo "   Нужно заменить на 'from' и 'to'"
else
    echo "✅ Проблем не найдено"
fi

echo ""
echo "🎯 Для исправления:"
echo "   1. Откройте src/services/api.ts"
echo "   2. Найдите функцию getCalendarStatus"
echo "   3. Замените параметр 'month' на 'from' и 'to'"
echo "   4. Обновите API вызов: params: { from, to }"
echo ""
echo "✅ Или используйте автоматический скрипт: ./fix-all.sh" 