import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from datetime import date
from typing import List, Dict
from pydantic import BaseModel

from .. import database, models, schemas
from .dashboard import find_last_completed_date # Импортируем нашу новую функцию

logging.warning("--- LOADING PRO_DASHBOARD ROUTER ---")

router = APIRouter(
    prefix="/pro-dashboard",
    tags=['pro-dashboard']
)

USER_ID = 179 # TODO: в будущем получать из токена авторизации

class ProDataResponse(BaseModel):
    achievements: List[schemas.ProSectionItem]
    problems: List[schemas.ProSectionItem]
    goals: List[schemas.ProSectionItem]
    blockers: List[schemas.ProSectionItem]
    metrics: List[schemas.ProMetricsItem]


@router.get("/data", response_model=ProDataResponse)
def get_pro_dashboard_data(
    date_str: str | None = None,
    db: Session = Depends(database.get_db)
):
    # 1. Определяем, для какой даты строим дашборд
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD.")
    else:
        # Если дата не передана, используем последнюю завершенную
        target_date = find_last_completed_date(USER_ID, db)

    # Если даты нет, возвращаем пустой ответ
    if not target_date:
        return ProDataResponse(achievements=[], problems=[], goals=[], blockers=[], metrics=[])
        
    # 2. Получаем все справочные данные по сферам
    all_db_spheres = db.query(models.Sphere).all()
    sphere_name_map = {s.id: s.name for s in all_db_spheres}

    # 3. Получаем ВСЕ pro-ответы за найденную дату
    achievements_db = db.query(models.Achievement).filter(
        models.Achievement.user_id == USER_ID,
        func.DATE(models.Achievement.created_at) == target_date
    ).all()
    
    problems_db = db.query(models.Problem).filter(
        models.Problem.user_id == USER_ID,
        func.DATE(models.Problem.created_at) == target_date
    ).all()
    
    goals_db = db.query(models.Goal).filter(
        models.Goal.user_id == USER_ID,
        func.DATE(models.Goal.created_at) == target_date
    ).all()

    blockers_db = db.query(models.Blocker).filter(
        models.Blocker.user_id == USER_ID,
        func.DATE(models.Blocker.created_at) == target_date
    ).all()

    metrics_db = db.query(models.Metric).filter(
        models.Metric.user_id == USER_ID,
        func.DATE(models.Metric.created_at) == target_date
    ).all()
    
    # 4. Трансформируем данные в модель ответа
    achievements = [schemas.ProSectionItem(sphere=sphere_name_map.get(a.sphere_id, 'N/A'), value=a.description) for a in achievements_db]
    problems = [schemas.ProSectionItem(sphere=sphere_name_map.get(p.sphere_id, 'N/A'), value=p.text) for p in problems_db]
    goals = [schemas.ProSectionItem(sphere=sphere_name_map.get(g.sphere_id, 'N/A'), value=g.text) for g in goals_db]
    blockers = [schemas.ProSectionItem(sphere=sphere_name_map.get(b.sphere_id, 'N/A'), value=b.text) for b in blockers_db]
    metrics = [
        schemas.ProMetricsItem(
            sphere=sphere_name_map.get(m.sphere_id, 'N/A'),
            metric=m.name,
            value=m.current_value,
            target=m.target_value if m.target_value is not None else 0
        ) for m in metrics_db
    ]

    return ProDataResponse(
        achievements=achievements,
        problems=problems,
        goals=goals,
        blockers=blockers,
        metrics=metrics
    )

@router.get("/basic-recommendations", response_model=List[schemas.RecommendationItem])
def get_basic_recommendations(db: Session = Depends(database.get_db)):
    # Mock data for now
    return [
        schemas.RecommendationItem(sphere="Карьера", recommendation="Начните отслеживать свои ежедневные достижения."),
        schemas.RecommendationItem(sphere="Здоровье", recommendation="Попробуйте добавить 15-минутную прогулку в свой распорядок дня.")
    ]

@router.get("/ai-recommendations", response_model=List[schemas.AiRecommendationItem])
def get_ai_recommendations(db: Session = Depends(database.get_db)):
    # Mock data for now
    return [
        schemas.AiRecommendationItem(
            sphere="Финансы",
            ai_recommendation="Создать и придерживаться бюджета",
            description="Анализ ваших проблем и целей показывает, что основной точкой роста является управление личными финансами.",
            steps="1. Проанализируйте доходы и расходы за последние 3 месяца.<br/>2. Создайте бюджет в приложении или таблице.<br/>3. Установите лимиты на необязательные траты.",
            justification="Это создаст прочную финансовую основу и позволит быстрее достигать долгосрочных целей, таких как 'создание финансовой подушки'."
        )
    ] 