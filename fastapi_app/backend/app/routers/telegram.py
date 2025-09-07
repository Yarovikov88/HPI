from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import hashlib
import hmac
from dotenv import load_dotenv
from jose import jwt
from app.telegram_bot_multi.db_async import get_user_id_by_telegram_id, save_user
from logging_config import logger

# Загружаем переменные окружения из .env файла
load_dotenv()

router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SECRET_KEY = "your_secret_key"  # Тот же ключ, что и в auth.py
ALGORITHM = "HS256"
ALLOWED_FIELDS = {
    "id", "first_name", "last_name", "username", "photo_url", "auth_date"
}

def flatten_telegram_data(data):
    logger.info(f"FLATTEN: Исходные данные: {data}")
    # Если данные пришли с вложенным user, "расплющиваем" их
    if 'user' in data and isinstance(data['user'], dict):
        flat = {**data['user']}
        for k, v in data.items():
            if k not in ('user',):
                flat[k] = v
        logger.info(f"FLATTEN: Расплющенные данные: {flat}")
        return flat
    logger.info(f"FLATTEN: Данные уже плоские: {data}")
    return data

def check_telegram_auth(data):
    try:
        logger.info("=" * 50)
        logger.info("НАЧАЛО ПРОВЕРКИ TELEGRAM AUTH")
        logger.info("=" * 50)
        
        logger.info(f"Исходные данные: {data}")
        
        # Копируем данные
        auth_data = data.copy()
        
        # Проверяем наличие hash (как в официальной документации)
        hash_ = auth_data.pop('hash', None)
        logger.info(f"Hash: {hash_}")
        
        # РЕЖИМ ОТЛАДКИ: пропускаем проверку подписи
        DEBUG_MODE = True  # Установите False для включения проверки
        if DEBUG_MODE:
            logger.info("🔧 РЕЖИМ ОТЛАДКИ: пропускаем проверку подписи")
            return True
        
        if not hash_:
            logger.error("❌ Нет hash в данных")
            return False
        
        # Проверяем наличие обязательных полей
        required_fields = ['id', 'auth_date']
        missing_fields = [field for field in required_fields if field not in auth_data]
        if missing_fields:
            logger.error(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            return False
        
        logger.info("✅ Обязательные поля присутствуют")
        
        # ФИЛЬТРАЦИЯ: удаляем пустые значения и лишние поля
        original_data = auth_data.copy()
        auth_data = {}
        
        # Включаем только нужные поля и только если они не пустые
        allowed_fields = ['query_id', 'id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date']
        
        logger.info("🔍 Фильтрация полей:")
        for field in allowed_fields:
            if field in original_data:
                value = original_data[field]
                # Включаем все поля, даже пустые (как делает Telegram)
                if value is not None:
                    auth_data[field] = value
                    logger.info(f"  ✅ Включено: {field} = {value}")
                else:
                    logger.info(f"  ❌ Исключено (None): {field} = {value}")
            else:
                logger.info(f"  ⚠️  Отсутствует: {field}")
        
        logger.info(f"📋 Данные после фильтрации: {auth_data}")
        
        # Сортируем ключи по алфавиту (как требует Telegram)
        sorted_keys = sorted(auth_data.keys())
        logger.info(f"📝 Отсортированные ключи: {sorted_keys}")
        
        # Формируем строку для подписи
        data_check_string = '\n'.join([f"{k}={auth_data[k]}" for k in sorted_keys])
        logger.info("🔐 Строка для подписи:")
        logger.info("-" * 30)
        logger.info(data_check_string)
        logger.info("-" * 30)
        
        # Проверяем токен
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
            return False
        
        token_preview = TELEGRAM_BOT_TOKEN[:10] + "..." if len(TELEGRAM_BOT_TOKEN) > 10 else TELEGRAM_BOT_TOKEN
        logger.info(f"🤖 Токен бота: {token_preview}")
        
        # Вычисляем secret_key (как в официальной документации)
        secret_key = hmac.new('WebAppData'.encode(), TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        logger.info(f"🔑 Secret key (hex): {secret_key.hex()}")
        
        # Вычисляем HMAC
        hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        logger.info(f"🧮 Вычисленный hash: {hmac_hash}")
        
        # Сравниваем
        is_valid = hmac_hash == hash_
        logger.info(f"🔍 Сравнение хэшей:")
        logger.info(f"  Пришедший:  {hash_}")
        logger.info(f"  Вычисленный: {hmac_hash}")
        logger.info(f"  Совпадают:   {'✅ ДА' if is_valid else '❌ НЕТ'}")
        
        logger.info("=" * 50)
        logger.info(f"РЕЗУЛЬТАТ ПРОВЕРКИ: {'✅ УСПЕХ' if is_valid else '❌ ОШИБКА'}")
        logger.info("=" * 50)
        
        return is_valid
    except Exception as e:
        logger.error(f"AUTH CHECK: Ошибка в check_telegram_auth: {e}")
        logger.error(f"AUTH CHECK: Данные: {data}")
        return False

@router.post('/api/telegram_auth')
async def telegram_auth(request: Request):
    try:
        data = await request.json()
        logger.info(f"TELEGRAM AUTH: Получены данные: {data}")
        
        flat_data = flatten_telegram_data(data)
        logger.info(f"TELEGRAM AUTH: Плоские данные: {flat_data}")
        
        auth_result = check_telegram_auth(flat_data)
        logger.info(f"TELEGRAM AUTH: Результат проверки: {auth_result}")
        
        if auth_result:
            telegram_id = flat_data.get('id')
            username = flat_data.get('username')
            first_name = flat_data.get('first_name')
            logger.info(f"TELEGRAM AUTH: Данные пользователя - ID: {telegram_id}, username: {username}, first_name: {first_name}")
            
            # Не сохраняем last_name, чтобы оно всегда было NULL
            user_id = await get_user_id_by_telegram_id(telegram_id)
            logger.info(f"TELEGRAM AUTH: Найден существующий user_id: {user_id}")
            
            if not user_id:
                user_id = await save_user(telegram_id, username=username, first_name=first_name, last_name=None)
                logger.info(f"TELEGRAM AUTH: Создан новый пользователь с user_id: {user_id}")
            
            # Генерируем JWT токен
            token = jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"TELEGRAM AUTH: Сгенерирован JWT токен для user_id: {user_id}")
            
            response = {
                'status': 'ok', 
                'user_id': user_id, 
                'username': username,
                'access_token': token,
                'token_type': 'bearer'
            }
            logger.info(f"TELEGRAM AUTH: Успешный ответ с токеном: {response}")
            return JSONResponse(response)
        else:
            logger.error(f"TELEGRAM AUTH: Ошибка авторизации для данных: {flat_data}")
            return JSONResponse({'status': 'error', 'message': 'Invalid auth'}, status_code=403)
            
    except Exception as e:
        logger.error(f"TELEGRAM AUTH: Неожиданная ошибка: {e}")
        return JSONResponse({'status': 'error', 'message': 'Internal server error'}, status_code=500)

@router.get('/api/telegram_auth')
async def telegram_auth_get(request: Request):
    try:
        # Получаем query параметры
        params = dict(request.query_params)
        logger.info(f"TELEGRAM AUTH GET: Получены параметры: {params}")
        
        auth_result = check_telegram_auth(params)
        logger.info(f"TELEGRAM AUTH GET: Результат проверки: {auth_result}")
        
        if auth_result:
            telegram_id = params.get('id')
            username = params.get('username')
            first_name = params.get('first_name')
            logger.info(f"TELEGRAM AUTH GET: Данные пользователя - ID: {telegram_id}, username: {username}, first_name: {first_name}")
            
            # Не сохраняем last_name, чтобы оно всегда было NULL
            user_id = await get_user_id_by_telegram_id(telegram_id)
            logger.info(f"TELEGRAM AUTH GET: Найден существующий user_id: {user_id}")
            
            if not user_id:
                user_id = await save_user(telegram_id, username=username, first_name=first_name, last_name=None)
                logger.info(f"TELEGRAM AUTH GET: Создан новый пользователь с user_id: {user_id}")
            
            # Генерируем JWT токен
            token = jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)
            logger.info(f"TELEGRAM AUTH GET: Сгенерирован JWT токен для user_id: {user_id}")
            
            response = {
                'status': 'ok', 
                'user_id': user_id, 
                'username': username,
                'access_token': token,
                'token_type': 'bearer'
            }
            logger.info(f"TELEGRAM AUTH GET: Успешный ответ с токеном: {response}")
            return JSONResponse(response)
        else:
            logger.error(f"TELEGRAM AUTH GET: Ошибка авторизации для параметров: {params}")
            return JSONResponse({'status': 'error', 'message': 'Invalid auth'}, status_code=403)
            
    except Exception as e:
        logger.error(f"TELEGRAM AUTH GET: Неожиданная ошибка: {e}")
        return JSONResponse({'status': 'error', 'message': 'Internal server error'}, status_code=500) 