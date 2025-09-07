#!/bin/bash

echo "🔍 Проверяем все исправления HPI.EXPERT..."

# 1. Проверяем frontend
echo "🌐 Проверяем frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://83.147.192.188/login)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: HTTP $FRONTEND_STATUS OK"
else
    echo "❌ Frontend: HTTP $FRONTEND_STATUS"
fi

# 2. Проверяем backend health
echo "🔌 Проверяем backend health..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$BACKEND_HEALTH" = "ok" ]; then
    echo "✅ Backend health: $BACKEND_HEALTH"
else
    echo "❌ Backend health: $BACKEND_HEALTH"
fi

# 3. Проверяем API endpoints
echo "🔌 Проверяем API endpoints..."

# Новый endpoint
echo "   📍 /api/login:"
LOGIN_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://83.147.192.188/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555"}' \
  -o /tmp/login_response)
LOGIN_STATUS=$(tail -c 3 /tmp/login_response)
if [ "$LOGIN_STATUS" = "200" ]; then
    echo "     ✅ HTTP 200 OK"
else
    echo "     ❌ HTTP $LOGIN_STATUS"
    echo "     📄 Ответ: $(cat /tmp/login_response | head -c 200)"
fi

# Старый endpoint (через redirect)
echo "   📍 /api/auth/login:"
AUTH_LOGIN_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://83.147.192.188/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yx@gmail.com","password":"555"}' \
  -o /tmp/auth_login_response)
AUTH_LOGIN_STATUS=$(tail -c 3 /tmp/auth_login_response)
if [ "$AUTH_LOGIN_STATUS" = "200" ]; then
    echo "     ✅ HTTP 200 OK (через redirect)"
else
    echo "     ❌ HTTP $AUTH_LOGIN_STATUS"
    echo "     📄 Ответ: $(cat /tmp/auth_login_response | head -c 200)"
fi

# 4. Проверяем базу данных
echo "🗄️ Проверяем базу данных..."
if docker exec hpisite-backend-1 python /app/create_tables.py > /dev/null 2>&1; then
    echo "✅ База данных: Таблицы доступны"
else
    echo "❌ База данных: Проблема с таблицами"
fi

# 5. Проверяем OpenAPI
echo "📚 Проверяем OpenAPI документацию..."
OPENAPI_SIZE=$(curl -s http://localhost:8000/openapi.json | wc -c)
if [ "$OPENAPI_SIZE" -gt 10000 ]; then
    echo "✅ OpenAPI: $OPENAPI_SIZE байт (полная документация)"
else
    echo "❌ OpenAPI: $OPENAPI_SIZE байт (неполная документация)"
fi

# 6. Проверяем календарь API
echo "📅 Проверяем календарь API..."
CALENDAR_RESPONSE=$(curl -s -w "%{http_code}" -X GET "http://83.147.192.188/api/calendar/status?from=2025-08-01&to=2025-08-31" \
  -H "Authorization: Bearer $(curl -s -X POST http://83.147.192.188/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"yx@gmail.com","password":"555"}' \
    -o /tmp/calendar_login_response | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)" \
  -o /tmp/calendar_response)
CALENDAR_STATUS=$(tail -c 3 /tmp/calendar_response)
if [ "$CALENDAR_STATUS" = "200" ]; then
    echo "✅ Календарь API: HTTP 200 OK"
else
    echo "❌ Календарь API: HTTP $CALENDAR_STATUS"
    echo "   📄 Ответ: $(cat /tmp/calendar_response | head -c 200)"
fi

# 6. Итоговая сводка
echo ""
echo "🎯 ИТОГОВАЯ СВОДКА:"
echo "=================="

if [ "$FRONTEND_STATUS" = "200" ] && [ "$BACKEND_HEALTH" = "ok" ] && [ "$LOGIN_STATUS" = "200" ] && [ "$AUTH_LOGIN_STATUS" = "200" ] && [ "$OPENAPI_SIZE" -gt 10000 ] && [ "$CALENDAR_STATUS" = "200" ]; then
    echo "🎉 ВСЕ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ УСПЕШНО!"
    echo "✅ Frontend работает"
    echo "✅ Backend работает"
    echo "✅ API endpoints работают"
    echo "✅ База данных доступна"
    echo "✅ OpenAPI документация полная"
    echo "✅ Календарь API работает"
    echo ""
    echo "🌐 Сайт доступен: http://83.147.192.188"
    echo "🔌 API работает: http://83.147.192.188/api/*"
    echo "📚 Документация: http://localhost:8000/docs"
else
    echo "⚠️ ЕСТЬ ПРОБЛЕМЫ:"
    [ "$FRONTEND_STATUS" != "200" ] && echo "❌ Frontend не работает"
    [ "$BACKEND_HEALTH" != "ok" ] && echo "❌ Backend не работает"
    [ "$LOGIN_STATUS" != "200" ] && echo "❌ API login не работает"
    [ "$AUTH_LOGIN_STATUS" != "200" ] && echo "❌ API auth/login не работает"
    [ "$OPENAPI_SIZE" -le 10000 ] && echo "❌ OpenAPI документация неполная"
    [ "$CALENDAR_STATUS" != "200" ] && echo "❌ Календарь API не работает"
    echo ""
    echo "🔧 Запустите: ./fix-all.sh"
fi

# Очистка временных файлов
rm -f /tmp/login_response /tmp/auth_login_response /tmp/calendar_response /tmp/calendar_login_response 