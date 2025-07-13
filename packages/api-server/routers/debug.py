"""
API-роутер для отладочных и служебных операций.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect # ИМПОРТИРУЕМ inspect
from .. import database, schemas, models
from ..data_factory import seed_scenario

router = APIRouter(
    prefix="/debug",  # ИСПРАВЛЕНО: Убран дублирующийся префикс /api/v1
    tags=["Debug"],
)

class ScenarioRequest(schemas.BaseModel):
    user_id: int
    scenario_name: str

@router.post("/seed-scenario",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.GeneratedData)
def create_scenario_data(
    request: ScenarioRequest, 
    db: Session = Depends(database.get_db)
):
    """
    Эндпоинт для полной очистки данных пользователя и генерации нового
    набора данных по указанному сценарию.
    
    Возвращает сгенерированные данные для немедленного обновления фронтенда.
    """
    try:
        generated_data = seed_scenario(
            db=db, 
            user_id=request.user_id, 
            scenario_name=request.scenario_name
        )

        # Обрабатываем базовые ответы
        processed_answers = []
        for answer in generated_data["answers"]:
            db.expunge(answer) # Отвязываем объект от сессии
            mapper = inspect(answer.__class__)
            processed_answers.append({c.key: getattr(answer, c.key) for c in mapper.column_attrs})

        # Обрабатываем Pro-ответы
        processed_pro_answers = []
        for item in generated_data["pro_answers"]:
            db.expunge(item) # Отвязываем объект от сессии
            mapper = inspect(item.__class__)
            item_dict = {c.key: getattr(item, c.key) for c in mapper.column_attrs}
            
            class_name = item.__class__.__name__
            category = ""

            if class_name == "Problem":
                category = "problems"
                if 'text' in item_dict: item_dict['description'] = item_dict.pop('text')
            elif class_name == "Goal":
                category = "goals"
                if 'text' in item_dict: item_dict['description'] = item_dict.pop('text')
            elif class_name == "Blocker":
                category = "blockers"
                if 'text' in item_dict: item_dict['description'] = item_dict.pop('text')
            elif class_name == "Metric":
                category = "metrics"
            elif class_name == "Achievement":
                category = "achievements"
            
            if category:
                item_dict["category"] = category
                processed_pro_answers.append(item_dict)

        return {
            "answers": processed_answers,
            "pro_answers": processed_pro_answers
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}",
        )

@router.get("/scenarios", response_model=list[str])
def get_available_scenarios():
    """
    Возвращает список ключей всех доступных сценариев.
    """
    # Предполагаем, что SCENARIOS определены где-то в `data_factory`
    # Чтобы избежать циклического импорта, можем сделать так:
    from ..data_factory import SCENARIOS
    return list(SCENARIOS.keys()) 