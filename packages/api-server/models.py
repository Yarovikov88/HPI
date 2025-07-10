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
    answers = relationship("Answer", back_populates="user")

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
    options = Column(ARRAY(String), nullable=True)
    scores = Column(ARRAY(PG_INTEGER), nullable=True)
    fields = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    sphere = relationship("Sphere", back_populates="questions", foreign_keys=[sphere_id])

class Answer(Base):
    __tablename__ = 'answers'

    id = Column(PG_INTEGER, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    sphere = Column(Integer, nullable=False)
    question_id = Column(String, ForeignKey('questions.id'), nullable=False)
    answer = Column(Integer, nullable=False) # Используем Integer для универсальности
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="answers")
    question = relationship("Question") 