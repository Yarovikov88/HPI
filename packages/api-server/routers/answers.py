import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
from typing import Any, Optional
from .. import models
from .. import database

router = APIRouter(tags=["answers"])

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnswerBody(BaseModel):
    questionId: str
    userId: int
    value: Any

@router.post("/answer")
def post_answer(answer_body: AnswerBody, db: Session = Depends(database.get_db)):
    logger.info(f"--> POST /answer: Received payload: {answer_body.model_dump_json()}")
    try:
        user = db.query(models.User).filter(models.User.user_id == answer_body.userId).first()
        if not user:
            logger.warning(f"User with id {answer_body.userId} not found.")
            raise HTTPException(status_code=404, detail=f"User with id {answer_body.userId} not found")

        question = db.query(models.Question).filter(models.Question.id == answer_body.questionId).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with id {answer_body.questionId} not found")

        today = date.today()
        
        # Ищем ответ за СЕГОДНЯ
        existing_answer = db.query(models.Answer).filter(
            models.Answer.user_id == answer_body.userId,
            models.Answer.question_id == answer_body.questionId,
            text("date(created_at) = :today") 
        ).params(today=today).first()

        if existing_answer:
            # Если нашли - обновляем
            logger.info(f"Updating existing answer for user {answer_body.userId} and question {answer_body.questionId} for today.")
            existing_answer.answer = answer_body.value
            existing_answer.created_at = datetime.now() # Обновляем таймстемп
        else:
            # Если не нашли - создаем новый
            logger.info(f"Creating new answer for user {answer_body.userId} and question {answer_body.questionId}.")
            db_answer = models.Answer(
                question_id=answer_body.questionId,
                user_id=answer_body.userId,
                sphere_id=question.sphere_id,
                answer=answer_body.value
                # created_at проставится автоматически благодаря server_default
            )
            db.add(db_answer)

        db.commit()
        
        logger.info(f"Successfully saved answer for user {answer_body.userId}")
        return {"status": "success", "message": "Ответ успешно сохранен."}
    except Exception as e:
        db.rollback()
        logger.error(f"!!! An unexpected error occurred in post_answer:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 