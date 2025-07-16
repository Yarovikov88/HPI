import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, date
from typing import Any, Optional, List, Dict
from .. import models
from .. import database
from .. import schemas

router = APIRouter(tags=["answers"])

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnswerBody(BaseModel):
    question_id: str
    answer: Any
    # userId убрали, будем хардкодить
    # value переименовали в answer

@router.post("/api/v1/answers/")
def post_answer(answer_body: AnswerBody, db: Session = Depends(database.get_db)):
    # Пока что хардкодим user_id, как договаривались
    user_id = 1 
    logger.info(f"--> POST /api/v1/answers/: Received payload: {answer_body.model_dump_json()} for user_id={user_id}")
    
    try:
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            logger.warning(f"User with id {user_id} not found.")
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

        question = db.query(models.Question).filter(models.Question.id == answer_body.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with id {answer_body.question_id} not found")

        today = date.today()
        
        # Ищем ответ за СЕГОДНЯ
        existing_answer = db.query(models.Answer).filter(
            models.Answer.user_id == user_id,
            models.Answer.question_id == answer_body.question_id,
            func.date(models.Answer.created_at) == today
        ).first()

        if existing_answer:
            # Если нашли - обновляем
            logger.info(f"Updating existing answer for user {user_id} and question {answer_body.question_id} for today.")
            existing_answer.answer = answer_body.answer
            existing_answer.created_at = datetime.now() # Обновляем таймстемп
            db.commit()
            db.refresh(existing_answer)
            return {"status": "success", "message": "Ответ успешно обновлен.", "answer_id": existing_answer.id}
        else:
            # Если не нашли - создаем новый
            logger.info(f"Creating new answer for user {user_id} and question {answer_body.question_id}.")
            db_answer = models.Answer(
                question_id=answer_body.question_id,
                user_id=user_id,
                sphere_id=question.sphere_id,
                answer=answer_body.answer
                # created_at проставится автоматически благодаря server_default
            )
            db.add(db_answer)
            db.commit()
            db.refresh(db_answer)
            logger.info(f"Successfully saved answer for user {user_id}")
            return {"status": "success", "message": "Ответ успешно сохранен.", "answer_id": db_answer.id}
    except Exception as e:
        db.rollback()
        logger.error(f"!!! An unexpected error occurred in post_answer:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 


@router.delete("/api/v1/answers/{question_id}", status_code=204)
def delete_answer(question_id: str, db: Session = Depends(database.get_db)):
    # Пока что хардкодим user_id
    user_id = 1
    today = date.today()

    answer_to_delete = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        models.Answer.question_id == question_id,
        func.date(models.Answer.created_at) == today
    ).first()

    if answer_to_delete:
        db.delete(answer_to_delete)
        db.commit()
    
    # Мы не возвращаем ошибку, если ответа нет, так как
    # с точки зрения клиента, результат (отсутствие ответа) тот же.
    return


@router.get("/api/v1/answers/today", response_model=List[schemas.AnswerSchema])
def get_todays_answers(user_id: int = 1, db: Session = Depends(database.get_db)):
    """
    Get all answers for a user for the current date.
    """
    today = date.today()
    answers = (
        db.query(models.Answer)
        .filter(
            models.Answer.user_id == user_id,
            func.date(models.Answer.created_at) == today
        )
        .all()
    )
    return answers


@router.get("/api/v1/answers/history", response_model=Dict[str, List[schemas.AnswerSchema]])
def get_answers_history(user_id: int = 1, db: Session = Depends(database.get_db)):
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