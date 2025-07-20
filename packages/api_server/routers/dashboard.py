from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
from datetime import datetime, date

from .. import database, models, schemas

router = APIRouter(
    prefix="/dashboard",
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


def find_last_completed_date(user_id: int, db: Session) -> date | None:
    """
    Находит последнюю дату, когда пользователь полностью прошел базовую диагностику.
    Возвращает дату или None, если ни одной полной диагностики не найдено.
    """
    # Считаем количество уникальных вопросов в каждой сфере
    questions_per_sphere = db.query(
        models.Question.sphere_id,
        func.count(models.Question.id).label('question_count')
    ).filter(models.Question.category.is_(None)).group_by(models.Question.sphere_id).subquery()

    # Считаем количество ответов пользователя по датам и сферам
    answers_per_day_and_sphere = db.query(
        func.date(models.Answer.created_at).label('completion_date'),
        models.Answer.sphere_id,
        func.count(models.Answer.id).label('answer_count')
    ).filter(models.Answer.user_id == user_id).group_by(
        func.date(models.Answer.created_at),
        models.Answer.sphere_id
    ).subquery()

    # Соединяем ответы с количеством вопросов, чтобы найти "полные" сферы за день
    completed_spheres_per_day = db.query(
        answers_per_day_and_sphere.c.completion_date,
        func.count(answers_per_day_and_sphere.c.sphere_id).label('completed_spheres_count')
    ).join(
        questions_per_sphere,
        questions_per_sphere.c.sphere_id == answers_per_day_and_sphere.c.sphere_id
    ).filter(
        answers_per_day_and_sphere.c.answer_count == questions_per_sphere.c.question_count
    ).group_by(answers_per_day_and_sphere.c.completion_date).subquery()

    # Ищем день, когда количество завершенных сфер равно общему количеству сфер
    total_spheres_count = db.query(func.count(models.Sphere.id)).scalar()

    last_date = db.query(
        completed_spheres_per_day.c.completion_date
    ).filter(
        completed_spheres_per_day.c.completed_spheres_count == total_spheres_count
    ).order_by(completed_spheres_per_day.c.completion_date.desc()).first()

    return last_date[0] if last_date else None


def find_all_completed_dates(user_id: int, db: Session) -> List[date]:
    """
    Находит все даты, когда пользователь полностью прошел базовую диагностику.
    Возвращает список дат в порядке убывания (от новой к старой).
    """
    # Считаем количество уникальных вопросов в каждой сфере
    questions_per_sphere = db.query(
        models.Question.sphere_id,
        func.count(models.Question.id).label('question_count')
    ).filter(models.Question.category.is_(None)).group_by(models.Question.sphere_id).subquery()

    # Считаем количество ответов пользователя по датам и сферам
    answers_per_day_and_sphere = db.query(
        func.date(models.Answer.created_at).label('completion_date'),
        models.Answer.sphere_id,
        func.count(models.Answer.id).label('answer_count')
    ).filter(models.Answer.user_id == user_id).group_by(
        func.date(models.Answer.created_at),
        models.Answer.sphere_id
    ).subquery()

    # Соединяем ответы с количеством вопросов, чтобы найти "полные" сферы за день
    completed_spheres_per_day = db.query(
        answers_per_day_and_sphere.c.completion_date,
        func.count(answers_per_day_and_sphere.c.sphere_id).label('completed_spheres_count')
    ).join(
        questions_per_sphere,
        questions_per_sphere.c.sphere_id == answers_per_day_and_sphere.c.sphere_id
    ).filter(
        answers_per_day_and_sphere.c.answer_count == questions_per_sphere.c.question_count
    ).group_by(answers_per_day_and_sphere.c.completion_date).subquery()

    # Ищем день, когда количество завершенных сфер равно общему количеству сфер
    total_spheres_count = db.query(func.count(models.Sphere.id)).scalar()

    all_dates_result = db.query(
        completed_spheres_per_day.c.completion_date
    ).filter(
        completed_spheres_per_day.c.completed_spheres_count == total_spheres_count
    ).order_by(completed_spheres_per_day.c.completion_date.desc()).all()

    return [row[0] for row in all_dates_result]


@router.get("/", response_model=schemas.DashboardResponse)
async def get_dashboard_data(
    date_str: str | None = None, # Добавляем необязательный параметр даты
    user_id: int = 179,
    db: Session = Depends(database.get_db)
):
    # 1. Определяем, для какой даты строим дашборд
    target_date: date | None = None
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD.")
    else:
        # Если дата не передана, используем последнюю завершенную
        target_date = find_last_completed_date(user_id, db)

    # Если дату так и не удалось определить, возвращаем пустой дашборд
    if not target_date:
        return schemas.DashboardResponse(basic=None, pro=None)

    # 2. Получаем все справочные данные по сферам из БД
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

    # 3. Получаем все вопросы для БАЗОВОЙ диагностики
    all_questions = db.query(models.Question).filter(models.Question.category == None).all()
    questions_by_sphere: Dict[str, List[str]] = {}
    for q in all_questions:
        if q.sphere_id not in questions_by_sphere:
            questions_by_sphere[q.sphere_id] = []
        questions_by_sphere[q.sphere_id].append(q.id)

    # 4. Получаем ответы пользователя за целевую дату
    latest_answers = db.query(models.Answer).filter(
        models.Answer.user_id == user_id,
        func.date(models.Answer.created_at) == target_date
    ).all()

    # Если за эту дату почему-то нет ответов, возвращаем пустой дашборд
    if not latest_answers:
        return schemas.DashboardResponse(basic=None)

    # 5. Группируем ответы по ID вопроса для удобства
    answers_map = {a.question_id: a for a in latest_answers}
    
    # 6. Считаем HPI за последнюю дату
    sphere_scores = {}
    is_complete = True
    for sphere_id, question_ids in questions_by_sphere.items():
        sphere_answers_latest = [answers_map[qid] for qid in question_ids if qid in answers_map]
        
        # Эта проверка уже, по сути, не нужна, т.к. find_last_completed_date гарантирует полноту,
        # но оставим для надежности
        if len(sphere_answers_latest) == QUESTIONS_PER_SPHERE:
            raw_score = sum(apply_fibonacci_score(ans.answer) for ans in sphere_answers_latest)
            normalized_score = normalize_sphere_score(raw_score)
            sphere_scores[sphere_id] = normalized_score
        else:
            is_complete = False
            break 

    # Если опрос за эту дату не завершен (на всякий случай), то данных для дашборда нет
    if not is_complete:
        return schemas.DashboardResponse(basic=None)

    hpi_latest = calculate_total_hpi(sphere_scores, sphere_weights)
    last_updated_latest = datetime.combine(target_date, datetime.min.time())

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


    # --- Расчет изменения HPI ---
    hpi_change = None
    if len(trend_data) > 0:
        # Убедимся, что последняя точка в тренде - это не день дашборда
        last_trend_point = trend_data[-1]
        if last_trend_point.date.date() < target_date:
             hpi_change = hpi_latest - last_trend_point.hpi
        elif len(trend_data) > 1: # Если последняя точка - день дашборда, берем предпоследнюю
             previous_trend_point = trend_data[-2]
             hpi_change = hpi_latest - previous_trend_point.hpi
        
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
        hpi=hpi_latest,
        hpi_change=hpi_change,
        trend=trend_data,
        radar=radar_data,
        sphere_trends=sphere_trends_data,
        last_updated=last_updated_latest
    )

    return schemas.DashboardResponse(basic=basic_dashboard) 