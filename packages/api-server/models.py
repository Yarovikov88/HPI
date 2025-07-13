from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, DateTime, Integer, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER as PG_INTEGER
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    telegram_id = Column(BigInteger, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    answers = relationship("Answer", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    problems = relationship("Problem", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    blockers = relationship("Blocker", back_populates="user", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="user", cascade="all, delete-orphan")

class Sphere(Base):
    __tablename__ = 'spheres'
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    questions = relationship("Question", back_populates="sphere")

class Question(Base):
    __tablename__ = 'questions'

    id = Column(String, primary_key=True, index=True)
    sphere_id = Column("sphere", String, ForeignKey('spheres.id'))
    type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    text = Column(String)
    options = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    fields = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    sphere = relationship("Sphere", back_populates="questions", foreign_keys=[sphere_id])

class Answer(Base):
    __tablename__ = 'answers'

    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    sphere_id = Column("sphere", String, ForeignKey('spheres.id'), nullable=False)
    question_id = Column(String, ForeignKey('questions.id'), nullable=False)
    answer = Column(Integer, nullable=False) # Используем Integer для универсальности
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="answers")
    question = relationship("Question")

# --- Модели для Pro-ответов ---

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    sphere_id = Column("sphere", String, nullable=False, index=True)
    description = Column(String, nullable=False)
    date_achieved = Column(DateTime, nullable=True)
    impact_areas = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="achievements")

class Problem(Base):
    __tablename__ = 'problems'
    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    sphere_id = Column("sphere", String, nullable=False, index=True)
    text = Column(String, nullable=False)
    severity = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="problems")

class Goal(Base):
    __tablename__ = 'goals'
    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    sphere_id = Column("sphere", String, nullable=False, index=True)
    text = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="goals")

class Blocker(Base):
    __tablename__ = 'blockers'
    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    sphere_id = Column("sphere", String, nullable=False, index=True)
    text = Column(String, nullable=False)
    impact_level = Column(Integer, nullable=True)
    related_goals = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="blockers")

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    sphere_id = Column("sphere", String, nullable=False, index=True)
    name = Column(String, nullable=False)
    current_value = Column(Integer, nullable=False)
    target_value = Column(Integer, nullable=True)
    unit = Column(String, nullable=True)
    type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="metrics") 