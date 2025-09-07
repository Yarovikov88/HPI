# src/telegram_bot_multi/db_async.py
# Асинхронный модуль работы с БД для мультиязычного Telegram-бота HPI

import os
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text as sa_text
from app.db import SessionLocal

async def get_user_id_by_telegram_id(telegram_id: int) -> int:
    """Получает ID пользователя по Telegram ID"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT user_id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        )
        row = result.fetchone()
        if row:
            return row[0]
        return None

async def save_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> int:
    """Сохраняет пользователя в БД"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("""
                INSERT INTO users (telegram_id, username, first_name, last_name, is_pro) 
                VALUES (:telegram_id, :username, :first_name, :last_name, TRUE) 
                ON CONFLICT (telegram_id) DO UPDATE SET 
                    username = EXCLUDED.username, 
                    first_name = EXCLUDED.first_name, 
                    last_name = EXCLUDED.last_name 
                RETURNING user_id
            """),
            {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        row = result.fetchone()
        await db.commit()
        if row:
            return row[0]
        return None

async def save_answer(user_id: int, sphere: int, question_id: int, answer: int) -> None:
    """Сохраняет ответ на базовый вопрос"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO answers (user_id, sphere, question_id, answer, created_at) 
                VALUES (:user_id, :sphere, :question_id, :answer, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "question_id": question_id,
                "answer": answer
            }
        )
        await db.commit()

async def get_user_answers(user_id: int) -> list:
    """Получает все ответы пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT sphere, question_id, answer FROM answers WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        return [{"sphere": row[0], "question_id": row[1], "answer": row[2]} for row in rows]

async def save_problem(user_id: int, sphere: int, description: str, status: str, severity: str, date_noticed: str) -> None:
    """Сохраняет проблему пользователя"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO problems (user_id, sphere, description, status, severity, date_noticed, created_at) 
                VALUES (:user_id, :sphere, :description, :status, :severity, :date_noticed, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "description": description,
                "status": status,
                "severity": severity,
                "date_noticed": date_noticed
            }
        )
        await db.commit()

async def save_goal(user_id: int, sphere: int, description: str, target_date: str, priority: str, status: str) -> None:
    """Сохраняет цель пользователя"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO goals (user_id, sphere, description, target_date, priority, status, created_at) 
                VALUES (:user_id, :sphere, :description, :target_date, :priority, :status, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "description": description,
                "target_date": target_date,
                "priority": priority,
                "status": status
            }
        )
        await db.commit()

async def save_blocker(user_id: int, sphere: int, description: str, impact_level: str, status: str, resolution_plan: str) -> None:
    """Сохраняет блокер пользователя"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO blockers (user_id, sphere, description, impact_level, status, resolution_plan, created_at) 
                VALUES (:user_id, :sphere, :description, :impact_level, :status, :resolution_plan, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "description": description,
                "impact_level": impact_level,
                "status": status,
                "resolution_plan": resolution_plan
            }
        )
        await db.commit()

async def save_metric(user_id: int, sphere: int, metric_name: str, current_value: float, target_value: float, metric_type: str) -> None:
    """Сохраняет метрику пользователя"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO metrics (user_id, sphere, metric_name, current_value, target_value, metric_type, created_at) 
                VALUES (:user_id, :sphere, :metric_name, :current_value, :target_value, :metric_type, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "metric_name": metric_name,
                "current_value": current_value,
                "target_value": target_value,
                "metric_type": metric_type
            }
        )
        await db.commit()

async def save_achievement(user_id: int, sphere: int, description: str, impact_areas: str, date_achieved: str) -> None:
    """Сохраняет достижение пользователя"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO achievements (user_id, sphere, description, impact_areas, date_achieved, created_at) 
                VALUES (:user_id, :sphere, :description, :impact_areas, :date_achieved, NOW())
            """),
            {
                "user_id": user_id,
                "sphere": sphere,
                "description": description,
                "impact_areas": impact_areas,
                "date_achieved": date_achieved
            }
        )
        await db.commit()

async def get_user_problems(user_id: int) -> list:
    """Получает проблемы пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT * FROM problems WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

async def get_user_goals(user_id: int) -> list:
    """Получает цели пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT * FROM goals WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

async def get_user_blockers(user_id: int) -> list:
    """Получает блокеры пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT * FROM blockers WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

async def get_user_metrics(user_id: int) -> list:
    """Получает метрики пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT * FROM metrics WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

async def get_user_achievements(user_id: int) -> list:
    """Получает достижения пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT * FROM achievements WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

async def get_hpi_history(user_id: int) -> list:
    """Получает историю HPI пользователя"""
    async with SessionLocal() as db:
        result = await db.execute(
            sa_text("SELECT hpi_value, created_at FROM hpi_history WHERE user_id = :user_id ORDER BY created_at"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        return [{"hpi_value": row[0], "created_at": row[1]} for row in rows]

async def save_hpi_history(user_id: int, hpi_value: float, scores: dict = None) -> None:
    """Сохраняет HPI в историю"""
    async with SessionLocal() as db:
        await db.execute(
            sa_text("""
                INSERT INTO hpi_history (user_id, hpi_value, scores, created_at) 
                VALUES (:user_id, :hpi_value, :scores, NOW())
            """),
            {
                "user_id": user_id,
                "hpi_value": hpi_value,
                "scores": json.dumps(scores) if scores else None
            }
        )
        await db.commit() 