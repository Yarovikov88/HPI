"""
Глобальные константы и конфигурация проекта HPI.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Database ---
DATABASE_URL = "postgresql://hpi_user:hpi_password_2024@83.147.192.188:5433/hpi_db"

SPHERE_CONFIG = [
    {"number": "1", "name": "Отношения с любимыми", "emoji": "💖", "normalized": "relations_love"},
    {"number": "2", "name": "Отношения с родными", "emoji": "🏡", "normalized": "relations_family"},
    {"number": "3", "name": "Друзья", "emoji": "🤝", "normalized": "friends"},
    {"number": "4", "name": "Карьера", "emoji": "💼", "normalized": "career"},
    {"number": "5", "name": "Физическое здоровье", "emoji": "♂️", "normalized": "physical_health"},
    {"number": "6", "name": "Ментальное здоровье", "emoji": "🧠", "normalized": "mental_health"},
    {"number": "7", "name": "Хобби и увлечения", "emoji": "🎨", "normalized": "hobbies"},
    {"number": "8", "name": "Благосостояние", "emoji": "💰", "normalized": "wealth"}
] 