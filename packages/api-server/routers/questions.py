
import logging
from typing import List
from itertools import chain
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas
from .. import models
from .. import database

router = APIRouter(tags=["questions"])

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/api/v1/questions/", response_model=List[schemas.Question])
def get_questions(db: Session = Depends(database.get_db)):
    """
    Get all questions from the database.
    """
    basic_questions = db.query(models.Question).all()
    return basic_questions 