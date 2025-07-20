
import logging
from typing import List
from itertools import chain
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from .. import models
from .. import database

router = APIRouter(
    prefix="/questions",
    tags=["questions"]
)

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[schemas.Question])
def read_questions(db: Session = Depends(database.get_db)):
    questions = db.query(models.Question).all()
    return questions 