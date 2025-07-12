import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
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
    created_at: Optional[datetime] = None

@router.post("/answer")
def post_answer(answer_body: AnswerBody, db: Session = Depends(database.get_db)):
    logger.info(f"--> POST /answer: Received payload: {answer_body.model_dump_json()}")
    try:
        # Проверяем, существует ли такой пользователь
        logger.info(f"Checking for user_id: {answer_body.userId}")
        user = db.query(models.User).filter(models.User.user_id == answer_body.userId).first()
        if not user:
            logger.warning(f"User with id {answer_body.userId} not found.")
            raise HTTPException(status_code=404, detail=f"User with id {answer_body.userId} not found")
        logger.info(f"User found: {user.username}")

        # Получаем вопрос из БД, чтобы получить ID сферы
        question = db.query(models.Question).filter(models.Question.id == answer_body.questionId).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with id {answer_body.questionId} not found")
        
        logger.info(f"Question found, sphere_id is: {question.sphere_id}")

        db_answer = models.Answer(
            question_id=answer_body.questionId,
            user_id=answer_body.userId,
            sphere_id=question.sphere_id, # Используем правильное поле и значение
            answer=answer_body.value,
            created_at=answer_body.created_at or datetime.now()
        )
        logger.info("Adding answer to the session...")
        db.add(db_answer)
        logger.info("Committing transaction...")
        db.commit()
        db.refresh(db_answer)
        
        logger.info(f"Successfully saved answer for user {answer_body.userId}")
        return {"status": "success", "message": "Ответ успешно сохранен."}
    except Exception as e:
        db.rollback()
        logger.error(f"!!! An unexpected error occurred in post_answer. Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 