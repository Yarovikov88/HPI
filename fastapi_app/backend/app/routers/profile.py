from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.db import SessionLocal
from app.models import User
from app.auth import get_current_user_id

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

class ProfileResponse(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    full_name: str
    email: EmailStr | None
    phone: str | None
    telegram_id: int | None
    avatar_url: str | None
    has_password: bool
    is_pro: bool

    @classmethod
    def from_user(cls, user: User) -> "ProfileResponse":
        first = user.first_name or ""
        last = user.last_name or ""
        full = (first + " " + last).strip()
        return cls(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=full,
            email=user.email,
            phone=user.phone,
            telegram_id=user.telegram_id,
            avatar_url=user.avatar_url,
            has_password=bool(user.hashed_password or ""),
            is_pro=user.is_pro,
        )

class UserCheckResponse(BaseModel):
    exists: bool
    created_at: datetime | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    username: str | None = None
    avatar_url: str | None = None

    # Normalize blank strings to None for all optional string fields
    @field_validator("full_name", "first_name", "last_name", "email", "phone", "username", "avatar_url", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s != "" else None
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None):
        if v is None:
            return v
        # very permissive E.164 check: + and 8-15 digits
        import re
        if not re.fullmatch(r"\+[1-9]\d{7,14}", v):
            raise ValueError("phone must be in E.164 format, e.g. +79990000000")
        return v

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ProfileResponse.from_user(user)

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Split full_name if provided and explicit parts are missing
    if data.full_name and not (data.first_name or data.last_name):
        parts = data.full_name.strip().split()
        first = parts[0] if parts else None
        last = " ".join(parts[1:]) if len(parts) > 1 else None
        data.first_name = data.first_name or first
        data.last_name = data.last_name or last

    # Unique checks for email and username
    if data.email is not None and data.email != user.email:
        q = await db.execute(select(User).where(User.email == data.email))
        existing = q.scalar()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        user.email = data.email

    if data.username is not None and data.username != user.username:
        q = await db.execute(select(User).where(User.username == data.username))
        existing = q.scalar()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")
        user.username = data.username

    if data.first_name is not None:
        if len(data.first_name) > 255:
            raise HTTPException(status_code=422, detail="first_name too long")
        user.first_name = data.first_name

    if data.last_name is not None:
        if len(data.last_name) > 255:
            raise HTTPException(status_code=422, detail="last_name too long")
        user.last_name = data.last_name

    if data.avatar_url is not None:
        if len(data.avatar_url) > 4096:
            raise HTTPException(status_code=422, detail="avatar_url too long")
        user.avatar_url = data.avatar_url

    await db.commit()

    # Refresh user for updated response
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    return ProfileResponse.from_user(user)

@router.post("/profile/{user_id}/grant-pro", response_model=ProfileResponse)
async def grant_pro_status(
    user_id: int,
    # current_user_id: int = Depends(get_current_user_id), # Пока без защиты
    db: AsyncSession = Depends(get_db)
):
    """Выдать пользователю PRO статус."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_pro = True
    await db.commit()
    await db.refresh(user)

    return ProfileResponse.from_user(user)

@router.post("/profile/{user_id}/revoke-pro", response_model=ProfileResponse)
async def revoke_pro_status(
    user_id: int,
    # current_user_id: int = Depends(get_current_user_id), # Пока без защиты
    db: AsyncSession = Depends(get_db)
):
    """Отозвать у пользователя PRO статус."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_pro = False
    await db.commit()
    await db.refresh(user)

    return ProfileResponse.from_user(user)

@router.get("/profile/check", response_model=UserCheckResponse)
async def check_user(
    email: str | None = None,
    phone: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if not email and not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or phone must be provided",
        )

    user: User | None = None
    if email:
        q = select(User).where(User.email == email)
        result = await db.execute(q)
        user = result.scalar_one_or_none()

    if not user and phone:
        # Normalize phone number
        import re
        normalized_phone = re.sub(r'\D', '', phone)
        if len(normalized_phone) == 11 and (normalized_phone.startswith('7') or normalized_phone.startswith('8')):
            normalized_phone = '+7' + normalized_phone[1:]
        elif not normalized_phone.startswith('+'):
             normalized_phone = '+' + normalized_phone

        q = select(User).where(User.phone == normalized_phone)
        result = await db.execute(q)
        user = result.scalar_one_or_none()

    if user:
        return UserCheckResponse(exists=True, created_at=user.created_at)
    else:
        return UserCheckResponse(exists=False, created_at=None) 