from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db import SessionLocal
from app.models import Answer
from app.auth import get_current_user_id
from app.cache import cache_response, invalidate_cache_pattern, cache_dashboard_data, get_cached_dashboard_data
from typing import List, Optional, Dict, Tuple
from datetime import date as date_type
from collections import defaultdict
import re
import time

from app.hpi_core import HPICalculator, SPHERE_CONFIG, QUESTIONS_PER_SPHERE, calculate_sphere_score

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session


def _parse_question_index(question_id: Optional[str]) -> Optional[int]:
    if not question_id:
        return None
    # Извлекаем последнюю цифру из строки (поддержка форматов "4.1", "1", и т.п.)
    matches = re.findall(r"\d+", str(question_id))
    if not matches:
        return None
    try:
        return int(matches[-1])
    except ValueError:
        return None


def _build_answers_payload(answers: List[Answer]) -> Dict[str, List[int]]:
    """Преобразует список Answer в словарь {"1": [a1..a6], ...} строго по порядку вопросов 1..6.
    Если для сферы отсутствует хотя бы один ответ из 1..6, сфера не возвращается (будет заполнена 0 в калькуляторе).
    При дублях по (sphere, question_id) берём последний по id.
    """
    print(f"🔍 _build_answers_payload: получено {len(answers)} ответов")
    
    per_sphere: Dict[str, Dict[int, Tuple[int, int]]] = defaultdict(dict)  # sphere -> qidx -> (answer, id)
    for a in answers:
        if a.answer is None:
            continue
        sphere_key = str(a.sphere)
        qidx = _parse_question_index(a.question_id)
        if qidx is None:
            print(f"⚠️ Не удалось извлечь индекс вопроса из {a.question_id}")
            continue
        prev = per_sphere[sphere_key].get(qidx)
        if prev is None or (a.id is not None and a.id > prev[1]):
            per_sphere[sphere_key][qidx] = (a.answer, a.id or 0)
    
    print(f"📊 per_sphere: {dict(per_sphere)}")
    
    payload: Dict[str, List[int]] = {}
    for sphere in [s["number"] for s in SPHERE_CONFIG]:
        qmap = per_sphere.get(sphere, {})
        print(f"🔍 Сфера {sphere}: найдено {len(qmap)} ответов, требуется {QUESTIONS_PER_SPHERE}")
        if all(idx in qmap for idx in range(1, QUESTIONS_PER_SPHERE + 1)):
            ordered = [qmap[idx][0] for idx in range(1, QUESTIONS_PER_SPHERE + 1)]
            payload[sphere] = ordered
            print(f"✅ Сфера {sphere}: добавлена в payload с ответами {ordered}")
        else:
            missing = [idx for idx in range(1, QUESTIONS_PER_SPHERE + 1) if idx not in qmap]
            print(f"❌ Сфера {sphere}: отсутствуют ответы {missing}")
    
    print(f"📊 Итоговый payload: {payload}")
    return payload


def _compute_hpi_and_balance(answers: List[Answer]) -> Tuple[float, Dict[str, float]]:
    print(f"🔍 _compute_hpi_and_balance: получено {len(answers)} ответов")
    
    if not answers:
        print("⚠️ Нет ответов, возвращаем 0.0")
        # Полные нули, чтобы фронт понял, что данных нет
        return 0.0, {str(i): 0.0 for i in range(1, 9)}
    
    payload = _build_answers_payload(answers)
    print(f"📊 payload для калькулятора: {payload}")
    
    calculator = HPICalculator()
    hpi, sphere_scores = calculator.calculate_from_answers(payload)
    print(f"📊 Результат калькулятора: HPI={hpi}, sphere_scores={sphere_scores}")
    
    # Гарантируем наличие всех сфер в ответе
    for i in range(1, 9):
        key = str(i)
        if key not in sphere_scores:
            sphere_scores[key] = 0.0
    
    print(f"📊 Финальный результат: HPI={hpi}, sphere_scores={sphere_scores}")
    return hpi, sphere_scores


def _select_year_month(all_answers: List[Answer], month: Optional[str], date: Optional[date_type]) -> Optional[Tuple[int, int]]:
    """Определяет целевой (год, месяц) по приоритету: month param -> date param -> последний доступный месяц."""
    if month:
        m = month.strip()
        match = re.fullmatch(r"(\d{4})-(\d{2})", m)
        if match:
            return int(match.group(1)), int(match.group(2))
        # если формат неверный, игнорируем и пойдём дальше
    if date is not None:
        return date.year, date.month
    dates = sorted({a.date for a in all_answers if a.date is not None})
    if not dates:
        return None
    latest = dates[-1]
    return latest.year, latest.month


@router.get("/dashboard")
@cache_response(ttl=300, key_prefix="dashboard")  # Кэш на 5 минут
async def get_dashboard(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    date: Optional[date_type] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
):
    """Получить основной дашборд пользователя"""
    try:
        stmt = select(Answer).where(Answer.user_id == user_id)
        result = await db.execute(stmt)
        all_answers = result.scalars().all()
        
        if date is not None:
            # Фильтрация по заданной дате
            answers = [a for a in all_answers if a.date == date]
            hpi, _ = _compute_hpi_and_balance(answers)
            return {"hpi": hpi, "date": date.isoformat()}
        
        # Если дата не указана — используем последнюю доступную дату из данных
        dates = sorted({a.date for a in all_answers if a.date is not None})
        if not dates:
            hpi, _ = _compute_hpi_and_balance([])
            return {"hpi": hpi, "date": None}
        
        latest_date = dates[-1]
        answers = [a for a in all_answers if a.date == latest_date]
        hpi, _ = _compute_hpi_and_balance(answers)
        return {"hpi": hpi, "date": latest_date.isoformat()}
        
    except Exception as e:
        # Возвращаем явные нули, а не заглушки
        return {"hpi": 0.0, "date": date.isoformat() if date else None}


@router.get("/dashboard/utm/{utm_param}")
async def get_dashboard_by_utm(
    utm_param: str,
    db: AsyncSession = Depends(get_db),
):
    """Получить дашборд пользователя по UTM-метке"""
    try:
        # Парсим UTM-метку: user_1044_1734876543210
        # Формат: user_{user_id}_{timestamp}
        if not utm_param.startswith('user_'):
            raise HTTPException(status_code=400, detail="Invalid UTM format")
        
        parts = utm_param.split('_')
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail="Invalid UTM format")
        
        try:
            user_id = int(parts[1])
            timestamp = int(parts[2])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UTM parameters")
        
        # Проверяем, что пользователь существует
        from app.models import User
        user_result = await db.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем ответы пользователя за последнюю дату
        from sqlalchemy import func
        
        # Находим последнюю дату с ответами
        latest_date_stmt = select(func.max(Answer.date)).where(Answer.user_id == user_id)
        latest_date_result = await db.execute(latest_date_stmt)
        latest_date = latest_date_result.scalar()
        
        if not latest_date:
            raise HTTPException(status_code=404, detail="No answers found for this user")
        
        # Получаем ответы только за последнюю дату
        stmt = select(Answer).where(
            Answer.user_id == user_id,
            Answer.date == latest_date
        )
        result = await db.execute(stmt)
        all_answers = result.scalars().all()
        
        if not all_answers:
            raise HTTPException(status_code=404, detail="No answers found for this user")
        
        # Вычисляем HPI и баланс
        hpi, sphere_scores = _compute_hpi_and_balance(all_answers)
        
        # Формируем данные ответов
        answers_data = []
        for answer in all_answers:
            answers_data.append({
                "id": answer.id,
                "sphere": answer.sphere,
                "question_id": answer.question_id,
                "answer": answer.answer,
                "date": answer.date.isoformat() if answer.date else None,
                "created_at": answer.created_at.isoformat() if answer.created_at else None
            })
        
        return {
            "user_id": user_id,
            "user_info": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "is_pro": user.is_pro
            },
            "hpi": hpi,
            "sphere_scores": sphere_scores,
            "answers": answers_data,
            "latest_date": latest_date.isoformat() if latest_date else None,
            "utm_param": utm_param
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/trend")
@cache_response(ttl=600, key_prefix="trend")  # Кэш на 10 минут
async def get_trend(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    month: Optional[str] = Query(None, description="Месяц в формате YYYY-MM"),
    date: Optional[date_type] = Query(None, description="Если указан, используется его месяц"),
):
    """Получить тренд HPI по месяцам"""
    stmt = select(Answer).where(Answer.user_id == user_id)
    result = await db.execute(stmt)
    all_answers = result.scalars().all()

    ym = _select_year_month(all_answers, month, date)
    if ym is None:
        return {"trend": [], "month": None}
    year, mon = ym

    # Фильтруем ответы выбранного месяца
    answers_in_month = [a for a in all_answers if a.date and a.date.year == year and a.date.month == mon]

    # Группируем по дням выбранного месяца
    by_date: Dict[str, List[Answer]] = defaultdict(list)
    for a in answers_in_month:
        by_date[a.date.isoformat()].append(a)

    points: List[Dict[str, object]] = []
    for d in sorted(by_date.keys()):
        day_answers = by_date[d]
        payload = _build_answers_payload(day_answers)
        # День считается только если базовая диагностика полная: 8 сфер x 6 ответов
        if all(str(i) in payload for i in range(1, 9)):
            calculator = HPICalculator()
            hpi, _ = calculator.calculate_from_answers(payload)
            points.append({"date": d, "hpi": hpi})

    return {"trend": points, "month": f"{year:04d}-{mon:02d}"}


@router.get("/radar")
@cache_response(ttl=300, key_prefix="radar")  # Кэш на 5 минут
async def get_radar(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    date: Optional[date_type] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
):
    """Получить радарную диаграмму по сферам"""
    stmt = select(Answer).where(Answer.user_id == user_id)
    result = await db.execute(stmt)
    all_answers = result.scalars().all()

    if date is not None:
        answers = [a for a in all_answers if a.date == date]
        _, balance = _compute_hpi_and_balance(answers)
        return {"radar": balance, "date": date.isoformat()}

    # Если дата не указана — используем последнюю доступную дату
    dates = sorted({a.date for a in all_answers if a.date is not None})
    if not dates:
        return {"radar": {str(i): 0.0 for i in range(1, 9)}, "date": None}
    latest_date = dates[-1]
    answers = [a for a in all_answers if a.date == latest_date]
    _, balance = _compute_hpi_and_balance(answers)
    return {"radar": balance, "date": latest_date.isoformat()}


@router.get("/spheres/trend")
@cache_response(ttl=600, key_prefix="sphere_trend")  # Кэш на 10 минут
async def get_sphere_trend(
    sphere: str = Query(..., description="Номер сферы '1'..'8'"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    month: Optional[str] = Query(None, description="Месяц в формате YYYY-MM"),
    date: Optional[date_type] = Query(None, description="Если указан, используется его месяц"),
):
    """Получить тренд конкретной сферы"""
    # Валидируем сферу
    if sphere not in {s["number"] for s in SPHERE_CONFIG}:
        raise HTTPException(status_code=400, detail="Invalid sphere")

    stmt = select(Answer).where(Answer.user_id == user_id)
    result = await db.execute(stmt)
    all_answers = result.scalars().all()

    ym = _select_year_month(all_answers, month, date)
    if ym is None:
        return {"sphere": sphere, "trend": [], "month": None}
    year, mon = ym

    answers_in_month = [a for a in all_answers if a.date and a.date.year == year and a.date.month == mon]

    by_date: Dict[str, List[Answer]] = defaultdict(list)
    for a in answers_in_month:
        by_date[a.date.isoformat()].append(a)

    points: List[Dict[str, object]] = []
    for d in sorted(by_date.keys()):
        day_answers = [a for a in by_date[d] if str(a.sphere) == sphere]
        # Собираем ответы 1..6 по сфере
        per_q: Dict[int, int] = {}
        for a in day_answers:
            qidx = _parse_question_index(a.question_id)
            if qidx is None:
                continue
            per_q[qidx] = a.answer
        if all(idx in per_q for idx in range(1, QUESTIONS_PER_SPHERE + 1)):
            ordered = [per_q[idx] for idx in range(1, QUESTIONS_PER_SPHERE + 1)]
            inverse = [False] * QUESTIONS_PER_SPHERE
            if sphere in ["4", "6", "8"]:
                inverse[-1] = True
            try:
                _, normalized = calculate_sphere_score(ordered, inverse)
                points.append({"date": d, "score": normalized})
            except Exception:
                continue

    return {"sphere": sphere, "trend": points, "month": f"{year:04d}-{mon:02d}"}


@router.get("/dashboard/combined")
@cache_response(ttl=300, key_prefix="dashboard_combined")  # Кэш на 5 минут
async def get_combined_dashboard(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    date: Optional[date_type] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
):
    """Получить все данные дашборда в одном запросе для оптимизации"""
    try:
        start_time = time.time()
        print(f"🚀 get_combined_dashboard: user_id={user_id}, date={date}")
        
        # Получаем все ответы пользователя
        stmt = select(Answer).where(Answer.user_id == user_id)
        result = await db.execute(stmt)
        all_answers = result.scalars().all()
        print(f"📊 Получено {len(all_answers)} ответов для пользователя {user_id}")
        
        # Определяем целевую дату
        target_date = date
        if target_date is None:
            dates = sorted({a.date for a in all_answers if a.date is not None})
            if dates:
                target_date = dates[-1]
                print(f"📅 Автоматически выбрана дата: {target_date}")
            else:
                print("⚠️ Нет дат в ответах")
        else:
            print(f"📅 Используется указанная дата: {target_date}")
        
        # Фильтруем ответы по дате
        if target_date:
            answers = [a for a in all_answers if a.date == target_date]
            print(f"📊 Отфильтровано {len(answers)} ответов для даты {target_date}")
        else:
            answers = []
            print("⚠️ Нет ответов для выбранной даты")
        
        # Вычисляем HPI и баланс
        print(f"🔍 Вызываем _compute_hpi_and_balance с {len(answers)} ответами")
        hpi, sphere_scores = _compute_hpi_and_balance(answers)
        print(f"📊 Результат _compute_hpi_and_balance: HPI={hpi}, sphere_scores={sphere_scores}")
        
        # Вычисляем тренд за текущий месяц
        current_month = f"{target_date.year:04d}-{target_date.month:02d}" if target_date else None
        trend_data = []
        if current_month:
            year, month = target_date.year, target_date.month
            answers_in_month = [a for a in all_answers if a.date and a.date.year == year and a.date.month == month]
            print(f"📊 Для тренда найдено {len(answers_in_month)} ответов за месяц {current_month}")
            by_date = defaultdict(list)
            for a in answers_in_month:
                by_date[a.date.isoformat()].append(a)
            
            for d in sorted(by_date.keys()):
                day_answers = by_date[d]
                payload = _build_answers_payload(day_answers)
                if all(str(i) in payload for i in range(1, 9)):
                    calculator = HPICalculator()
                    day_hpi, _ = calculator.calculate_from_answers(payload)
                    trend_data.append({"date": d, "hpi": day_hpi})
        
        execution_time = time.time() - start_time
        
        result_data = {
            "hpi": hpi,
            "sphere_scores": sphere_scores,
            "trend": trend_data,
            "date": target_date.isoformat() if target_date else None,
            "month": current_month,
            "performance": {
                "execution_time_ms": round(execution_time * 1000, 2),
                "cached": False
            }
        }
        
        print(f"✅ Возвращаем результат: {result_data}")
        return result_data
        
    except Exception as e:
        print(f"❌ Ошибка в get_combined_dashboard: {e}")
        return {
            "hpi": 0.0,
            "sphere_scores": {str(i): 0.0 for i in range(1, 9)},
            "trend": [],
            "date": date.isoformat() if date else None,
            "month": None,
            "error": str(e)
        } 