from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext
from jose import jwt
from app.schemas.auth import UserCreate, UserLogin
from app.auth import get_current_user_id
from logging_config import logger
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_db():
    async with SessionLocal() as session:
        yield session

class PasswordChangeRequest(BaseModel):
    old_password: str | None = None
    new_password: str

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar():
        logger.warning(f"Registration failed: email already registered ({user.email})")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    # username = full_name, остальные поля игнорируем
    db_user = User(email=user.email, hashed_password=hashed_password, username=user.full_name, is_pro=True)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Генерируем токен для автоматического входа
    token = jwt.encode({"sub": str(db_user.id)}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"User registered: {user.email} (user_id={db_user.id})")
    
    return {
        "msg": "User registered successfully", 
        "user_id": db_user.id,
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        logger.warning(f"Login failed for {user.email}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = jwt.encode({"sub": str(db_user.id)}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"User login: {user.email} (user_id={db_user.id})")
    return {"access_token": token, "token_type": "bearer", "user_id": db_user.id}

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Если пароля ещё нет — устанавливаем первичный
    if not user.hashed_password:
        user.hashed_password = pwd_context.hash(data.new_password)
        await db.commit()
        logger.info(f"Initial password set for user_id={user_id}")
        return

    # Иначе требуется старый пароль
    if not data.old_password:
        raise HTTPException(status_code=400, detail="Old password required")

    if not pwd_context.verify(data.old_password, user.hashed_password):
        logger.warning(f"Password change failed (wrong old password) for user_id={user_id}")
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user.hashed_password = pwd_context.hash(data.new_password)
    await db.commit()
    logger.info(f"Password changed for user_id={user_id}")
    return

# Redirect endpoints для совместимости со старым frontend кодом
@router.post("/auth/login")
async def login_redirect(request: Request):
    """Redirect к правильному endpoint /login для совместимости"""
    return RedirectResponse(url="/api/login", status_code=307)

@router.post("/auth/register")
async def register_redirect(request: Request):
    """Redirect к правильному endpoint /register для совместимости"""
    return RedirectResponse(url="/api/register", status_code=307)

@router.put("/auth/password")
async def password_redirect(request: Request):
    """Redirect к правильному endpoint /password для совместимости"""
    return RedirectResponse(url="/api/password", status_code=307)

 