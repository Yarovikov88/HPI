from sqlalchemy import Column, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER
from .database import Base

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
    scores = Column(ARRAY(INTEGER), nullable=True)
    fields = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    sphere = relationship("Sphere", back_populates="questions", foreign_keys=[sphere_id]) 