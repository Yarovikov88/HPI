from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import SessionLocal
from app.models import User
from jose import jwt, JWTError
from typing import Optional
import os

# Конфигурация
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")  # ← Исправлено!
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

async def get_db():
    async with SessionLocal() as session:
        yield session

class AuthManager:
    """Универсальный менеджер авторизации с поддержкой нескольких типов токенов"""
    
    @staticmethod
    async def get_current_user_id(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> int:
        """
        Универсальная функция авторизации, поддерживает:
        1. JWT токены (для обычной авторизации)
        2. Telegram ID (для Telegram авторизации)
        3. API ключи (для внешних сервисов)
        4. Сессии (для веб-интерфейса)
        """
        try:
            # 1. Пробуем как JWT токен
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id: str = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Invalid JWT token")
                return int(user_id)
            except JWTError:
                pass
            
            # 2. Пробуем как Telegram ID
            try:
                telegram_id = int(token)
                result = await db.execute(select(User).where(User.telegram_id == telegram_id))
                user = result.scalar()
                if user is None:
                    raise HTTPException(status_code=401, detail="Telegram user not found")
                return user.user_id
            except ValueError:
                pass
            
            # 3. Пробуем как API ключ
            api_key = os.getenv('API_KEY')
            if api_key and token == api_key:
                # Для API ключа возвращаем специальный user_id или используем дефолтного пользователя
                result = await db.execute(select(User).where(User.user_id == 1))  # Дефолтный пользователь
                user = result.scalar()
                if user:
                    return user.user_id
            
            # 4. Пробуем как сессию (можно добавить Redis для сессий)
            # session_user_id = await get_session_user_id(token)
            # if session_user_id:
            #     return session_user_id
            
            # Если ничего не подошло
            raise HTTPException(status_code=401, detail="Invalid token format")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        """Возвращает полный объект пользователя"""
        user_id = await AuthManager.get_current_user_id(token, db)
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    
    @staticmethod
    def create_jwt_token(user_id: int) -> str:
        """Создает JWT токен для пользователя"""
        return jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_api_key() -> str:
        """Создает API ключ (можно использовать UUID)"""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    async def validate_telegram_auth(telegram_id: int, db: AsyncSession) -> Optional[User]:
        """Проверяет Telegram авторизацию и возвращает пользователя"""
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar()

# Экспортируем основную функцию для использования в роутерах
get_current_user_id = AuthManager.get_current_user_id
get_current_user = AuthManager.get_current_user 