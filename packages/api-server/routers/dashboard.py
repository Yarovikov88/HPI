from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
from datetime import datetime, date

from .. import database, models, schemas

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"]
)

# --- Константы и логика расчета (адаптировано из calculator.py) ---

FIBONACCI_SCORES = {1: 1.0, 2: 2.0, 3: 3.0, 4: 5.0}
QUESTIONS_PER_SPHERE = 6
MIN_POSSIBLE_SCORE = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[1]
MAX_POSSIBLE_SCORE = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[4]

def apply_fibonacci_score(answer: int, inverse: bool = False) -> float:
    """Применяет нелинейное преобразование Фибоначчи к ответу."""
    # TODO: Реализовать логику инверсии, если она потребуется
    return FIBONACCI_SCORES.get(answer, 0.0)

def normalize_sphere_score(raw_score: float) -> float:
    """Нормализация оценки сферы в шкалу 1-10."""
    if MAX_POSSIBLE_SCORE == MIN_POSSIBLE_SCORE:
        return 1.0
    normalized = ((raw_score - MIN_POSSIBLE_SCORE) / (MAX_POSSIBLE_SCORE - MIN_POSSIBLE_SCORE)) * 9 + 1
    return round(max(1.0, min(10.0, normalized)), 1)

def calculate_total_hpi(sphere_scores: Dict[str, float], sphere_weights: Dict[str, float]) -> float:
    """Расчет итогового HPI с учетом весов сфер."""
    total_weighted_score = 0
    total_weight = 0

    for sphere_id, score in sphere_scores.items():
        weight = sphere_weights.get(sphere_id)
        if weight is not None:
            total_weighted_score += score * weight
            total_weight += weight

    if total_weight == 0:
        return 20.0

    avg_score = total_weighted_score / total_weight
    hpi_score = ((avg_score - 1) * (80 / 9)) + 20
    return round(max(20.0, min(100.0, hpi_score)), 1)


@router.get("/", response_model=schemas.DashboardResponse)
async def get_dashboard_data(
    user_id: int = 179, # ВРЕМЕННО, пока нет реальной аутентификации
    db: Session = Depends(database.get_db)
):
    # 1. Получаем все справочные данные по сферам из БД
    all_db_spheres = db.query(models.Sphere).all()
    if not all_db_spheres:
        raise HTTPException(status_code=404, detail="В базе данных не найдены сферы для расчета.")

    sphere_name_map = {s.id: s.name for s in all_db_spheres}
    
    # Динамически создаем веса для сфер (пока все равны)
    num_spheres = len(all_db_spheres)
    if num_spheres == 0:
        raise HTTPException(status_code=500, detail="Количество сфер не может быть равно нулю.")
    equal_weight = 1 / num_spheres
    sphere_weights = {s.id: equal_weight for s in all_db_spheres}

    # 2. Получаем все вопросы для БАЗОВОЙ диагностики
    all_questions = db.query(models.Question).filter(models.Question.category == None).all()
    questions_by_sphere: Dict[str, List[str]] = {}
    for q in all_questions:
        if q.sphere_id not in questions_by_sphere:
            questions_by_sphere[q.sphere_id] = []
        questions_by_sphere[q.sphere_id].append(q.id)

    # 3. Получаем ответы пользователя ТОЛЬКО за СЕГОДНЯ
    today = date.today()
    todays_answers = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        func.date(models.Answer.created_at) == today
    ).all()

    # Если сегодня ответов нет, возвращаем пустой дашборд
    if not todays_answers:
        return schemas.DashboardResponse(basic=None)

    # 4. Группируем сегодняшние ответы по ID вопроса для удобства
    answers_map = {a.question_id: a for a in todays_answers}
    
    # 5. Проверяем, завершен ли опрос СЕГОДНЯ, и считаем HPI
    sphere_scores = {}
    is_complete_today = True
    for sphere_id, question_ids in questions_by_sphere.items():
        sphere_answers_today = [answers_map[qid] for qid in question_ids if qid in answers_map]
        
        if len(sphere_answers_today) == QUESTIONS_PER_SPHERE:
            raw_score = sum(apply_fibonacci_score(ans.answer) for ans in sphere_answers_today)
            normalized_score = normalize_sphere_score(raw_score)
            sphere_scores[sphere_id] = normalized_score
        else:
            # Если хоть одна сфера не заполнена, опрос за сегодня не завершен
            is_complete_today = False
            break # Выходим из цикла, т.к. считать HPI нет смысла

    # Если опрос за сегодня не завершен, то данных для дашборда нет
    if not is_complete_today:
        return schemas.DashboardResponse(basic=None)

    hpi_today = calculate_total_hpi(sphere_scores, sphere_weights)
    last_updated_today = datetime.combine(today, datetime.min.time())

    # --- Расчет ИСТОРИЧЕСКИХ данных для ТРЕНДА ---
    # Получаем ВСЕ ответы пользователя за все время
    all_historical_answers = db.query(models.Answer).filter(models.Answer.user_id == user_id).order_by(models.Answer.created_at).all()

    # Группируем ВСЕ ответы по датам
    answers_by_date: Dict[datetime.date, List[models.Answer]] = {}
    for answer in all_historical_answers:
        completion_date = answer.created_at.date()
        if completion_date not in answers_by_date:
            answers_by_date[completion_date] = []
        answers_by_date[completion_date].append(answer)

    # Считаем HPI для каждой завершенной даты в прошлом
    trend_data = []
    sphere_trends_accumulator: Dict[str, List[schemas.TrendDataPoint]] = {s.id: [] for s in all_db_spheres}
    sorted_dates = sorted(answers_by_date.keys())

    for d in sorted_dates:
        daily_answers_map = {a.question_id: a for a in answers_by_date[d]}
        daily_sphere_scores = {}
        is_complete_for_day = True

        for sphere_id, question_ids in questions_by_sphere.items():
            sphere_answers_for_day = [daily_answers_map[qid] for qid in question_ids if qid in daily_answers_map]
            
            if len(sphere_answers_for_day) == QUESTIONS_PER_SPHERE:
                raw_score = sum(apply_fibonacci_score(ans.answer) for ans in sphere_answers_for_day)
                normalized_score = normalize_sphere_score(raw_score)
                daily_sphere_scores[sphere_id] = normalized_score
                sphere_trends_accumulator[sphere_id].append(
                    schemas.TrendDataPoint(date=datetime.combine(d, datetime.min.time()), hpi=normalized_score)
                )
            else:
                is_complete_for_day = False
                break
        
        if is_complete_for_day:
            hpi = calculate_total_hpi(daily_sphere_scores, sphere_weights)
            trend_data.append(schemas.TrendDataPoint(date=datetime.combine(d, datetime.min.time()), hpi=hpi))


    # --- Расчет изменения HPI (сегодня по сравнению с последним трендом) ---
    hpi_change = None
    if len(trend_data) > 0:
        # Убедимся, что последняя точка в тренде - это не сегодня
        last_trend_date = trend_data[-1].date.date()
        if last_trend_date < today:
             hpi_change = hpi_today - trend_data[-1].hpi
        elif len(trend_data) > 1: # Если последняя точка - сегодня, берем предпоследнюю
             hpi_change = hpi_today - trend_data[-2].hpi
        
        if hpi_change is not None:
            hpi_change = round(hpi_change, 1)


    radar_data = []
    for sphere_id, score in sphere_scores.items():
        radar_data.append(schemas.SphereScore(
            sphere_id=sphere_id,
            sphere_name=sphere_name_map.get(sphere_id, sphere_id),
            score=score
        ))

    # --- Формирование финальной структуры ---
    sphere_trends_data = []
    for sphere_id, trend_points in sphere_trends_accumulator.items():
        if trend_points:
            sphere_trends_data.append(schemas.SphereTrendData(
                sphere_id=sphere_id,
                sphere_name=sphere_name_map.get(sphere_id, "Unknown Sphere"),
                trend=trend_points
            ))

    basic_dashboard = schemas.BasicDashboardData(
        hpi=hpi_today,
        hpi_change=hpi_change,
        trend=trend_data,
        radar=radar_data,
        sphere_trends=sphere_trends_data,
        last_updated=datetime.combine(today, datetime.min.time())
    )

    return schemas.DashboardResponse(basic=basic_dashboard) 