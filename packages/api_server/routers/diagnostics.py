 
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import database, models
from .dashboard import find_all_completed_dates # Используем новую функцию

router = APIRouter(
    prefix="/diagnostics",
    tags=['diagnostics']
)

USER_ID = 179 # TODO: в будущем получать из токена авторизации

@router.get("/dates", response_model=List[str])
def get_completed_diagnostic_dates(db: Session = Depends(database.get_db)):
    """
    Возвращает список всех дат (в формате YYYY-MM-DD), 
    за которые есть полностью завершенная базовая диагностика.
    """
    all_dates = find_all_completed_dates(USER_ID, db)
    return [d.isoformat() for d in all_dates] 