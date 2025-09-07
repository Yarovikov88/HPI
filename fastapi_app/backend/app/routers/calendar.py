from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text as sa_text
from app.auth import get_current_user_id
from app.db import SessionLocal

router = APIRouter(prefix="/api", tags=["calendar"]) 

# Параметры подключения к БД (больше не используются, так как используем SQLAlchemy)
# DB_HOST = '83.147.192.188'
# DB_PORT = 5433
# DB_NAME = 'hpi_db'
# DB_USER = 'hpi_user'
# DB_PASSWORD = 'hpi_password_2024'

PRO_CATEGORIES = ["problems", "goals", "blockers", "metrics", "achievements"]


def daterange(start: datetime, end: datetime):
    cur = start
    while cur <= end:
        yield cur
    
        cur += timedelta(days=1)


@router.get("/calendar/status")
async def get_calendar_status(
    from_: str = Query(..., alias="from"),
    to_: str = Query(..., alias="to"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(lambda: SessionLocal()),
):
    try:
        date_from = datetime.strptime(from_, "%Y-%m-%d")
        date_to = datetime.strptime(to_, "%Y-%m-%d")
        if (date_to - date_from).days > 92:
            raise HTTPException(status_code=400, detail="Range too wide")

        # Упрощенная версия с асинхронным SQLAlchemy
        # total_basic_questions - из каноничной таблицы questions
        try:
            result = await db.execute(sa_text("SELECT COUNT(*) FROM questions WHERE type = 'basic'"))
            total_basic_row = result.fetchone()
            total_basic = int(total_basic_row[0]) if total_basic_row and total_basic_row[0] is not None else 0
        except Exception:
            total_basic = 0

        # total spheres per pro category (fallback 8)
        totals_by_cat: Dict[str, int] = {c: 8 for c in PRO_CATEGORIES}
        try:
            result = await db.execute(sa_text("""
                SELECT category, COUNT(DISTINCT sphere) AS total_spheres
                FROM pro_questions
                GROUP BY category
            """))
            for category, total_spheres in result.fetchall():
                totals_by_cat[str(category)] = int(total_spheres)
        except Exception:
            pass

        # BASIC: ответы по дням (date(created_at))
        result = await db.execute(sa_text("""
            SELECT date(created_at) AS day, COUNT(DISTINCT question_id) AS answered
            FROM answers
            WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
            GROUP BY day
        """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
        basic_map: Dict[str, int] = {str(row[0]): int(row[1]) for row in result.fetchall()}

        # PRO: упрощенный запрос для каждой категории
        pro_map: Dict[str, Dict[str, int]] = {c: {} for c in PRO_CATEGORIES}
        
        # Problems
        try:
            result = await db.execute(sa_text("""
                SELECT date(created_at) AS day, COUNT(DISTINCT sphere) AS filled
                FROM problems
                WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
                  AND text IS NOT NULL AND trim(text) <> ''
                GROUP BY day
            """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
            for row in result.fetchall():
                pro_map['problems'][str(row[0])] = int(row[1])
        except Exception:
            pass

        # Goals
        try:
            result = await db.execute(sa_text("""
                SELECT date(created_at) AS day, COUNT(DISTINCT sphere) AS filled
                FROM goals
                WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
                  AND text IS NOT NULL AND trim(text) <> ''
                GROUP BY day
            """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
            for row in result.fetchall():
                pro_map['goals'][str(row[0])] = int(row[1])
        except Exception:
            pass

        # Blockers
        try:
            result = await db.execute(sa_text("""
                SELECT date(created_at) AS day, COUNT(DISTINCT sphere) AS filled
                FROM blockers
                WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
                  AND text IS NOT NULL AND trim(text) <> ''
                GROUP BY day
            """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
            for row in result.fetchall():
                pro_map['blockers'][str(row[0])] = int(row[1])
        except Exception:
            pass

        # Metrics
        try:
            result = await db.execute(sa_text("""
                SELECT date(created_at) AS day, COUNT(DISTINCT sphere) AS filled
                FROM metrics
                WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
                  AND name IS NOT NULL AND trim(name) <> ''
                GROUP BY day
            """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
            for row in result.fetchall():
                pro_map['metrics'][str(row[0])] = int(row[1])
        except Exception:
            pass

        # Achievements
        try:
            result = await db.execute(sa_text("""
                SELECT date(created_at) AS day, COUNT(DISTINCT sphere) AS filled
                FROM achievements
                WHERE user_id = :user_id AND date(created_at) BETWEEN :date_from AND :date_to
                  AND description IS NOT NULL AND trim(description) <> ''
                GROUP BY day
            """), {"user_id": user_id, "date_from": date_from.date(), "date_to": date_to.date()})
            for row in result.fetchall():
                pro_map['achievements'][str(row[0])] = int(row[1])
        except Exception:
            pass

        # Преобразуем pro_map в формат pro_by_day для совместимости
        pro_by_day: Dict[str, Dict[str, int]] = {}
        for category in PRO_CATEGORIES:
            for day, filled in pro_map[category].items():
                if day not in pro_by_day:
                    pro_by_day[day] = {}
                pro_by_day[day][category] = filled

        # Формируем ответ по каждому дню диапазона
        result: List[Dict[str, Any]] = []
        for d in daterange(date_from, date_to):
            day = d.strftime("%Y-%m-%d")

            # basic
            answered_b = basic_map.get(day, 0)
            if answered_b == 0:
                basic_status = "none"
            elif total_basic > 0 and answered_b < total_basic:
                basic_status = "draft"
            else:
                basic_status = "complete" if (total_basic == 0 and answered_b > 0) or (total_basic > 0 and answered_b >= total_basic) else "draft"

            # pro
            filled_by_cat = pro_by_day.get(day, {})
            if not filled_by_cat:
                pro_status = "none"
                pro_answered = 0
            else:
                categories_complete = all(
                    int(filled_by_cat.get(cat, 0)) >= int(totals_by_cat.get(cat, 8))
                    for cat in PRO_CATEGORIES
                )
                pro_status = "complete" if categories_complete else "draft"
                pro_answered = sum(1 for cat in PRO_CATEGORIES if int(filled_by_cat.get(cat, 0)) > 0)

            result.append({
                "date": day,
                "basic": {"status": basic_status, "answered": int(answered_b), "total": int(total_basic)},
                "pro": {"status": pro_status, "answered": int(pro_answered), "total": len(PRO_CATEGORIES)},
            })

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"calendar/status error: {e}")
        raise HTTPException(status_code=500, detail="Internal error") 