import sys
import os
import logging
import uvicorn

# --- Явное добавление пути к 'src' ---
# Это делает импорты ниже более надежными, особенно при использовании --reload
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi import FastAPI

# --- Теперь используем абсолютные импорты ---
import models
from database import SessionLocal, engine
from routers import questions as questions_router 