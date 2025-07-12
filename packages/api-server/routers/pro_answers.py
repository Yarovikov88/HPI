import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, database

router = APIRouter(
    prefix="/pro-answers",
    tags=["pro-answers"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/achievement/", response_model=schemas.ProAchievement, status_code=201)
def create_achievement(achievement: schemas.ProAchievementCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    db_achievement = models.Achievement(**achievement.model_dump(), user_id=user_id)
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

@router.post("/problem/", response_model=schemas.ProProblem, status_code=201)
def create_problem(problem: schemas.ProProblemCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    db_problem = models.Problem(**problem.model_dump(), user_id=user_id)
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

@router.post("/goal/", response_model=schemas.ProGoal, status_code=201)
def create_goal(goal: schemas.ProGoalCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    db_goal = models.Goal(**goal.model_dump(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.post("/blocker/", response_model=schemas.ProBlocker, status_code=201)
def create_blocker(blocker: schemas.ProBlockerCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    db_blocker = models.Blocker(**blocker.model_dump(), user_id=user_id)
    db.add(db_blocker)
    db.commit()
    db.refresh(db_blocker)
    return db_blocker

@router.post("/metric/", response_model=schemas.ProMetric, status_code=201)
def create_metric(metric: schemas.ProMetricCreate, db: Session = Depends(database.get_db)):
    # TODO: Get user_id from auth token
    user_id = 179
    db_metric = models.Metric(**metric.model_dump(), user_id=user_id)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric 