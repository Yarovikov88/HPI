
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas
from .. import models
from .. import database

router = APIRouter()

@router.get("/questions", response_model=list[schemas.Question])
def get_questions(db: Session = Depends(database.get_db)):
    """
    Получает список всех вопросов для диагностики.
    """
    questions = db.query(models.Question).all()
    return questions 