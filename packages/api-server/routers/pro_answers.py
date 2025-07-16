import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date, datetime
from typing import Any, List

from .. import models, schemas, database

router = APIRouter(
    tags=["pro-answers"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Общая функция для UPSERT
def upsert_pro_answer(db: Session, model: Any, data: dict, user_id: int, sphere_id: str):
    today = date.today()
    
    existing_record = db.query(model).filter(
        model.user_id == user_id,
        model.sphere_id == sphere_id,
        func.date(model.created_at) == today
    ).first()

    if existing_record:
        logger.info(f"Updating existing {model.__tablename__} for user {user_id}, sphere {sphere_id} for today.")
        for key, value in data.items():
            setattr(existing_record, key, value)
        existing_record.created_at = datetime.now()
        db.commit()
        db.refresh(existing_record)
        return existing_record
    else:
        logger.info(f"Creating new {model.__tablename__} for user {user_id}, sphere {sphere_id}.")
        new_record = model(**data, user_id=user_id, sphere_id=sphere_id)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

@router.post("/api/v1/pro-answers/achievement/", response_model=schemas.ProAchievement, status_code=201)
def create_achievement(achievement: schemas.ProAchievementCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    return upsert_pro_answer(db, models.Achievement, achievement.model_dump(), user_id, achievement.sphere_id)

@router.post("/api/v1/pro-answers/problem/", response_model=schemas.ProProblem, status_code=201)
def create_problem(problem: schemas.ProProblemCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    return upsert_pro_answer(db, models.Problem, problem.model_dump(), user_id, problem.sphere_id)

@router.post("/api/v1/pro-answers/goal/", response_model=schemas.ProGoal, status_code=201)
def create_goal(goal: schemas.ProGoalCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    return upsert_pro_answer(db, models.Goal, goal.model_dump(), user_id, goal.sphere_id)

@router.post("/api/v1/pro-answers/blocker/", response_model=schemas.ProBlocker, status_code=201)
def create_blocker(blocker: schemas.ProBlockerCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    return upsert_pro_answer(db, models.Blocker, blocker.model_dump(), user_id, blocker.sphere_id)

@router.post("/api/v1/pro-answers/metric/", response_model=schemas.ProMetric, status_code=201)
def create_metric(metric: schemas.ProMetricCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    return upsert_pro_answer(db, models.Metric, metric.model_dump(), user_id, metric.sphere_id) 

@router.get("/api/v1/pro-answers/", response_model=List[schemas.AnyProAnswer])
def get_pro_answers(user_id: int = 1, db: Session = Depends(database.get_db)):
    """
    Возвращает список всех Pro-ответов (achievements, problems, goals, blockers, metrics)
    для указанного пользователя.
    """
    all_pro_answers = []

    # Собираем данные из всех таблиц
    achievements = db.query(models.Achievement).filter(models.Achievement.user_id == user_id).all()
    problems = db.query(models.Problem).filter(models.Problem.user_id == user_id).all()
    goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()
    blockers = db.query(models.Blocker).filter(models.Blocker.user_id == user_id).all()
    metrics = db.query(models.Metric).filter(models.Metric.user_id == user_id).all()

    all_pro_answers.extend(achievements)
    all_pro_answers.extend(problems)
    all_pro_answers.extend(goals)
    all_pro_answers.extend(blockers)
    all_pro_answers.extend(metrics)
    
    # Сортируем все по дате создания для консистентности
    all_pro_answers.sort(key=lambda x: x.created_at, reverse=True)

    return all_pro_answers 