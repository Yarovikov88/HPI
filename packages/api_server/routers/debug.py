"""
API-роутер для отладочных и служебных операций.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect # ИМПОРТИРУЕМ inspect
from sqlalchemy import func
from datetime import date
import logging

from .. import database, models, schemas
from ..data_factory import seed_scenario

router = APIRouter(
    prefix="/debug",
    tags=["debug"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/debug/test")
def test_endpoint():
    return {"status": "ok"}

class ScenarioRequest(schemas.BaseModel):
    user_id: int
    scenario_name: str

@router.post("/debug/seed-scenario/",
             status_code=status.HTTP_201_CREATED)
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
            db.refresh(answer) # Принудительно загружаем все данные объекта
            db.expunge(answer) # Отвязываем объект от сессии
            mapper = inspect(answer.__class__)
            processed_answers.append({c.key: getattr(answer, c.key) for c in mapper.column_attrs})

        # Обрабатываем Pro-ответы
        processed_pro_answers = []
        for item in generated_data["pro_answers"]:
            db.refresh(item) # Принудительно загружаем все данные объекта
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

        db.commit() # ЯВНЫЙ COMMIT В КОНЦЕ
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}",
        )

@router.get("/debug/scenarios", response_model=list[str])
def get_available_scenarios():
    """
    Возвращает список ключей всех доступных сценариев.
    """
    # Предполагаем, что SCENARIOS определены где-то в `data_factory`
    # Чтобы избежать циклического импорта, можем сделать так:
    from packages.api_server.data_factory import SCENARIOS
    return list(SCENARIOS.keys()) 

@router.get("/debug/check-todays-answers/")
def check_todays_answers_endpoint(db: Session = Depends(database.get_db)):
    user_id_to_check = 179
    today = date.today()

    logger.info(f"--- [DEBUG] Проверка ответов для пользователя ID: {user_id_to_check} за {today} ---")

    basic_questions = db.query(models.Question).filter(models.Question.category == None).all()
    questions_by_sphere = {}
    for q in basic_questions:
        if q.sphere_id not in questions_by_sphere:
            questions_by_sphere[q.sphere_id] = []
        questions_by_sphere[q.sphere_id].append(q.id)
    
    todays_answers = db.query(models.Answer).filter(
        models.Answer.user_id == user_id_to_check,
        func.date(models.Answer.created_at) == today
    ).all()

    if not todays_answers:
        logger.info("!!! [DEBUG] В базе данных НЕТ ответов за сегодня для этого пользователя.")
        return {"message": "No answers for today."}

    logger.info(f"--- [DEBUG] Найдено всего ответов за сегодня: {len(todays_answers)} ---")

    answers_by_sphere = {}
    for answer in todays_answers:
        sphere_id_for_answer = None
        for sphere_id, question_ids in questions_by_sphere.items():
            if answer.question_id in question_ids:
                sphere_id_for_answer = sphere_id
                break
        
        if sphere_id_for_answer:
            if sphere_id_for_answer not in answers_by_sphere:
                answers_by_sphere[sphere_id_for_answer] = 0
            answers_by_sphere[sphere_id_for_answer] += 1

    all_spheres_complete = True
    result_details = {}
    for sphere_id, question_ids in questions_by_sphere.items():
        sphere_name = db.query(models.Sphere.name).filter(models.Sphere.id == sphere_id).scalar() or sphere_id
        count = answers_by_sphere.get(sphere_id, 0)
        expected_count = len(question_ids)
        is_complete = count == expected_count
        if not is_complete:
            all_spheres_complete = False
        
        detail = f"Найдено {count}/{expected_count} ответов."
        logger.info(f"--- [DEBUG] Сфера '{sphere_name}': {detail} ---")
        result_details[sphere_name] = detail

    final_message = "Все сферы в базе данных выглядят завершенными." if all_spheres_complete else "Не все сферы в базе данных завершены."
    logger.info(f"--- [DEBUG] {final_message} ---")
    
    return {
        "message": final_message,
        "details": result_details,
        "total_answers_today": len(todays_answers)
    } 