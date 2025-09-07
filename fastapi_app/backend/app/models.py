from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, BigInteger, Date, Float, Boolean
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    avatar_url = Column(Text, nullable=True)
    hashed_password = Column(String, nullable=True)  # Хешированный пароль
    has_password = Column(Boolean, default=False, nullable=False)
    is_pro = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, index=True)  # ID вопроса (например, "1.1", "1.2")
    sphere = Column(String)  # Сфера (love, family, friends, etc.)
    type = Column(String)  # basic или pro
    text = Column(Text)  # Текст вопроса
    options = Column(JSON, nullable=True)  # Варианты ответов
    scores = Column(JSON, nullable=True)  # Баллы за ответы
    inverse = Column(Boolean, default=False)  # Инвертированные баллы
    category = Column(String, nullable=True)  # Для pro вопросов
    description = Column(Text, nullable=True)  # Описание для pro вопросов
    fields = Column(JSON, nullable=True)  # Поля для pro вопросов
    language = Column(String, default='ru')  # Язык вопроса

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    question_id = Column(String)  # ID вопроса
    answer = Column(String)  # Ответ пользователя
    date = Column(Date)  # Явная дата ответа
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    text = Column(Text)
    date = Column(Date)  # Явная дата записи
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    text = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Blocker(Base):
    __tablename__ = "blockers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    text = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    name = Column(Text)  # Название метрики
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sphere = Column(Integer)  # 1-8 сферы жизни
    description = Column(Text)  # Описание достижения
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    # Базовая совместимость
    sphere = Column(Integer)  # 1..8
    text = Column(Text)  # краткий текст рекомендации
    # Расширенная структура по гайду
    recommendation_id = Column(String, nullable=True)
    type = Column(String, nullable=True)  # immediate | short_term | long_term
    priority = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)  # JSON с title, description, action_steps, metrics, related_spheres, evidence
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 