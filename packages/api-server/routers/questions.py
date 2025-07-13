
from itertools import chain
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas
from .. import models
from .. import database

router = APIRouter()

@router.get("/questions")
def get_questions(db: Session = Depends(database.get_db)):
    """
    Получает список всех вопросов для диагностики.
    Включает в себя как базовые вопросы, так и шаблоны Pro-вопросов.
    """
    basic_questions = db.query(models.Question).all()
    
    # Запрашиваем ВСЕ записи из таблиц Pro-вопросов,
    # так как фронтенд ожидает уже готовый список
    problem_items = db.query(models.Problem).all()
    goal_items = db.query(models.Goal).all()
    blocker_items = db.query(models.Blocker).all()
    metric_items = db.query(models.Metric).all()
    achievement_items = db.query(models.Achievement).all()

    # Объединяем все в один список
    all_questions = list(chain(
        basic_questions,
        problem_items,
        goal_items,
        blocker_items,
        metric_items,
        achievement_items
    ))

    return all_questions 