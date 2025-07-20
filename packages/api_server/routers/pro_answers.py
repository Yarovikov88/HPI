import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, time
from typing import Any, List

from .. import models, schemas, database

router = APIRouter(
    prefix="/pro-answers",
    tags=['pro-answers']
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Общая функция для UPSERT
def upsert_pro_answer(db: Session, model: Any, schema_create: Any, user_id: int):
    # Извлекаем sphere_id из схемы, а не принимаем как отдельный параметр
    sphere_id = schema_create.sphere_id

    existing_record = db.query(model).filter(
        model.user_id == user_id,
        model.sphere_id == sphere_id,
        func.DATE(model.created_at) == func.current_date()
    ).first()
    
    data_to_save = schema_create.model_dump()

    if existing_record:
        logger.info(f"Updating existing {model.__tablename__} for user {user_id}, sphere {sphere_id} for today.")
        for key, value in data_to_save.items():
            setattr(existing_record, key, value)
        existing_record.created_at = datetime.now()
        db.commit()
        db.refresh(existing_record)
        return existing_record
    else:
        logger.info(f"Creating new {model.__tablename__} for user {user_id}, sphere {sphere_id}.")
        # user_id передаем отдельно, а sphere_id уже есть в data_to_save
        new_record = model(**data_to_save, user_id=user_id)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

# НОВАЯ ОБЩАЯ ФУНКЦИЯ ДЛЯ UPSERT ЗА СУТКИ
def upsert_pro_answer_daily(db: Session, model: Any, schema_create: Any, user_id: int):
    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    
    sphere_id = schema_create.sphere_id

    existing_record = db.query(model).filter(
        model.user_id == user_id,
        model.sphere_id == sphere_id,
        model.created_at >= start_of_day,
        model.created_at <= end_of_day
    ).first()
    
    data_to_save = schema_create.model_dump()

    if existing_record:
        logger.info(f"Updating existing {model.__tablename__} for user {user_id}, sphere {sphere_id} for today.")
        for key, value in data_to_save.items():
            setattr(existing_record, key, value)
        existing_record.created_at = datetime.now() # Обновляем время
    else:
        logger.info(f"Creating new {model.__tablename__} for user {user_id}, sphere {sphere_id}.")
        existing_record = model(**data_to_save, user_id=user_id)
        db.add(existing_record)
    
    db.commit()
    db.refresh(existing_record)
    return existing_record

@router.post("/achievement/", response_model=schemas.ProAchievement, status_code=201)
def create_achievement(achievement: schemas.ProAchievementCreate, db: Session = Depends(database.get_db)):
    user_id = 179 # TODO: Get user_id from auth token
    return upsert_pro_answer_daily(db, models.Achievement, achievement, user_id)


@router.post("/problem/", response_model=schemas.ProProblem, status_code=201)
def create_problem(problem: schemas.ProProblemCreate, db: Session = Depends(database.get_db)):
    user_id = 179 # TODO: Get user_id from auth token
    return upsert_pro_answer_daily(db, models.Problem, problem, user_id)

@router.post("/goal/", response_model=schemas.ProGoal, status_code=201)
def create_goal(goal: schemas.ProGoalCreate, db: Session = Depends(database.get_db)):
    user_id = 179 # TODO: Get user_id from auth token
    return upsert_pro_answer_daily(db, models.Goal, goal, user_id)

@router.post("/blocker/", response_model=schemas.ProBlocker, status_code=201)
def create_blocker(blocker: schemas.ProBlockerCreate, db: Session = Depends(database.get_db)):
    user_id = 179 # TODO: Get user_id from auth token
    return upsert_pro_answer_daily(db, models.Blocker, blocker, user_id)

@router.post("/metric/", response_model=schemas.ProMetric, status_code=201)
def create_metric(metric: schemas.ProMetricCreate, db: Session = Depends(database.get_db)):
    """
    Создает или обновляет метрику для пользователя за ТЕКУЩИЕ СУТКИ.
    Ищет метрику по user_id, sphere_id и name за сегодняшний день.
    Если находит - обновляет. Если нет - создает новую.
    """
    user_id = 179 # TODO: Get user_id from auth token
    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    db_metric = db.query(models.Metric).filter(
        models.Metric.user_id == user_id,
        models.Metric.sphere_id == metric.sphere_id,
        models.Metric.name == metric.name,
        models.Metric.created_at >= start_of_day,
        models.Metric.created_at <= end_of_day
    ).first()

    if db_metric:
        # Обновляем существующую запись
        db_metric.current_value = metric.current_value
        if metric.target_value is not None:
            db_metric.target_value = metric.target_value
    else:
        # Создаем новую запись
        db_metric = models.Metric(**metric.model_dump(), user_id=user_id)
        db.add(db_metric)
    
    db.commit()
    db.refresh(db_metric)
    return db_metric

@router.get("/today", response_model=schemas.ProAnswersTodayResponse)
def get_todays_pro_answers(user_id: int = 179, db: Session = Depends(database.get_db)):
    """
    Возвращает сгруппированный список всех Pro-ответов (achievements, problems, goals, blockers, metrics)
    для указанного пользователя за сегодня.
    """
    response_data = {}
    
    # Получаем текущую дату с сервера БД для точного сравнения
    db_today = db.query(func.current_date()).scalar()
    logger.info(f"--- Начало запроса Pro-ответов для user_id={user_id} на дату в БД: {db_today} ---")

    # Функция-помощник для логирования
    def fetch_and_log(model, category_name):
        total_count = db.query(model).filter(model.user_id == user_id).count()
        today_records = db.query(model).filter(
            model.user_id == user_id, 
            func.DATE(model.created_at) == func.current_date()
        ).all()
        logger.info(f"  - Категория '{category_name}': Найдено {len(today_records)} за сегодня (всего записей: {total_count}).")
        return today_records

    # Извлекаем данные для каждой категории с логированием
    response_data["problems"] = fetch_and_log(models.Problem, "problems")
    response_data["goals"] = fetch_and_log(models.Goal, "goals")
    response_data["blockers"] = fetch_and_log(models.Blocker, "blockers")
    response_data["achievements"] = fetch_and_log(models.Achievement, "achievements")
    response_data["metrics"] = fetch_and_log(models.Metric, "metrics")
    
    logger.info(f"--- Запрос Pro-ответов для user_id={user_id} завершен ---")
    return schemas.ProAnswersTodayResponse(**response_data)


@router.get("/", response_model=List[schemas.AnyProAnswer])
def get_pro_answers(user_id: int = 179, db: Session = Depends(database.get_db)):
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