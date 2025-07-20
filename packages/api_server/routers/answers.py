import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, date
from typing import Any, Optional, List, Dict

from .. import database, models, schemas

router = APIRouter(
    prefix="/answers",
    tags=['answers']
)

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnswerBody(BaseModel):
    question_id: str
    answer: Any
    # userId убрали, будем хардкодить
    # value переименовали в answer

@router.post("/", response_model=schemas.AnswerSchema, status_code=status.HTTP_200_OK)
def create_or_update_answer(answer: schemas.AnswerCreate, response: Response, db: Session = Depends(database.get_db), user_id: int = 179):
    today = date.today()
    
    existing_answer = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        models.Answer.question_id == answer.question_id,
        func.date(models.Answer.created_at) == today
    ).first()

    question_sphere = db.query(models.Question.sphere_id).filter(models.Question.id == answer.question_id).scalar()
    if not question_sphere:
        raise HTTPException(status_code=404, detail="Question not found to determine sphere.")

    if existing_answer:
        existing_answer.answer = answer.answer
        db.commit()
        db.refresh(existing_answer)
        return existing_answer
    else:
        db_answer = models.Answer(
            user_id=user_id,
            question_id=answer.question_id,
            sphere_id=question_sphere,
            answer=answer.answer
        )
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)
        response.status_code = status.HTTP_201_CREATED
        return db_answer

@router.delete("/{question_id}", status_code=204)
def delete_answer(question_id: str, db: Session = Depends(database.get_db), user_id: int = 179):
    today = date.today()
    
    answer_to_delete = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        models.Answer.question_id == question_id,
        func.date(models.Answer.created_at) == today
    ).first()

    if answer_to_delete:
        db.delete(answer_to_delete)
        db.commit()
    
    return


@router.get("/today", response_model=List[schemas.AnswerSchema])
def get_todays_answers(db: Session = Depends(database.get_db), user_id: int = 179):
    today = date.today()
    todays_answers = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        func.date(models.Answer.created_at) == today
    ).all()
    return todays_answers


@router.get("/history", response_model=Dict[str, List[schemas.AnswerSchema]])
def get_answers_history(user_id: int = 179, db: Session = Depends(database.get_db)):
    """
    Get all answers for a user, grouped by date.
    """
    answers = (
        db.query(models.Answer)
        .filter(models.Answer.user_id == user_id)
        .order_by(models.Answer.created_at.desc())
        .all()
    )

    grouped_answers: Dict[str, List[models.Answer]] = {}
    for answer in answers:
        answer_date_str = answer.created_at.date().isoformat()
        if answer_date_str not in grouped_answers:
            grouped_answers[answer_date_str] = []
        grouped_answers[answer_date_str].append(answer)

    return grouped_answers 