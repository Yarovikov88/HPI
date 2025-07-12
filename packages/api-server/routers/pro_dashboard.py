import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from typing import List
from pydantic import BaseModel

from .. import database, models, schemas

logging.warning("--- LOADING PRO_DASHBOARD ROUTER ---")

router = APIRouter(
    prefix="/pro-dashboard",
    tags=["pro-dashboard"]
)

# TODO: Get user_id from auth token
USER_ID = 179

class ProDataResponse(BaseModel):
    achievements: List[schemas.ProSectionItem]
    problems: List[schemas.ProSectionItem]
    goals: List[schemas.ProSectionItem]
    blockers: List[schemas.ProSectionItem]
    metrics: List[schemas.ProMetricsItem]


@router.get("/data", response_model=ProDataResponse)
def get_pro_dashboard_data(db: Session = Depends(database.get_db)):
    # Helper to get sphere names
    all_db_spheres = db.query(models.Sphere).all()
    sphere_name_map = {s.id: s.name for s in all_db_spheres}

    def get_latest_for_each_sphere(model):
        """
        Для каждой сферы получает самую последнюю запись из указанной таблицы (модели).
        """
        # Создаем подзапрос для нахождения последней даты для каждой сферы
        latest_entry_subquery = db.query(
            model.sphere_id,
            func.max(model.created_at).label('max_created_at')
        ).filter(model.user_id == USER_ID).group_by(model.sphere_id).subquery()

        # Получаем полные записи, соответствующие самым последним датам
        latest_entries = db.query(model).join(
            latest_entry_subquery,
            (model.sphere_id == latest_entry_subquery.c.sphere_id) &
            (model.created_at == latest_entry_subquery.c.max_created_at)
        ).all()

        return latest_entries

    # Fetch data for the user using the helper
    achievements_db = get_latest_for_each_sphere(models.Achievement)
    problems_db = get_latest_for_each_sphere(models.Problem)
    goals_db = get_latest_for_each_sphere(models.Goal)
    blockers_db = get_latest_for_each_sphere(models.Blocker)
    
    # Для метрик логика может быть сложнее, если на одну сферу их может быть несколько.
    # Пока оставляем как есть, но если метрики тоже дублируются, нужно будет доработать.
    metrics_db = db.query(models.Metric).filter(models.Metric.user_id == USER_ID).order_by(models.Metric.created_at.desc()).all()
    
    # Transform data into response model
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