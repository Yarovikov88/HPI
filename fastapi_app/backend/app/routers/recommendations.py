from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.db import SessionLocal
from app.models import AIRecommendation, User, Answer
from app.auth import get_current_user_id
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import re
from app.hpi_core import HPICalculator, SPHERE_CONFIG, QUESTIONS_PER_SPHERE
from app.services.ai import generate_ai_recommendations, SPHERE_TITLES_RU, SPHERE_TITLES_EN
from app.services.engine import collect_user_pro_data, generate_smart_recommendations
from datetime import datetime

router = APIRouter()

# Короткие (1–2 строки) базовые рекомендации по сферам (дефолт)
SHORT_BASIC_RU: Dict[str, str] = {
    "1": "Сделайте один тёплый контакт с партнёром (15–30 мин) на этой неделе.",
    "2": "Выделите 15–30 минут на разговор с родными: важное без спешки.",
    "3": "Назначьте короткую встречу или звонок с другом на этой неделе.",
    "4": "Выделите 30 минут на один шаг, который реально продвинет работу.",
    "5": "Добавьте сегодня 20–30 минут лёгкой активности (прогулка/растяжка).",
    "6": "Ежедневно 5 минут дыхания или заметок для разгрузки головы.",
    "7": "Запланируйте 30 минут любимого занятия: восстановите энергию.",
    "8": "Проверьте расходы: найдите одну простую оптимизацию на этой неделе.",
}

SHORT_BASIC_EN: Dict[str, str] = {
    "1": "Plan one warm check‑in with your partner (15–30 min).",
    "2": "Spend 15–30 minutes on a calm talk with family.",
    "3": "Schedule a short catch‑up with a friend this week.",
    "4": "Block 30 minutes for one task that truly moves work forward.",
    "5": "Add 20–30 minutes of light activity today (walk/stretch).",
    "6": "Do 5 minutes of breathing or notes daily to unload the mind.",
    "7": "Schedule 30 minutes for a hobby to recharge.",
    "8": "Review spending and make one simple optimization this week.",
}

# Шаблоны по 5 уровням (1 — очень низкий, 5 — высокий)
LEVEL_TEMPLATES_RU: Dict[int, str] = {
    1: "Критично низко: сделайте сегодня 1 простой шаг в «{title}» (15–30 мин).",
    2: "Ниже нормы: выберите микро‑шаг для «{title}» на этой неделе и запланируйте его.",
    3: "Средний уровень: укрепите «{title}» одним регулярным действием (2–3 раза/нед).",
    4: "Хорошо: закрепите работающий ритуал в «{title}» и проведите краткий обзор.",
    5: "Высоко: поддерживайте «{title}», делайте еженедельный 5‑мин. обзор прогресса.",
}

LEVEL_TEMPLATES_EN: Dict[int, str] = {
    1: "Critically low: do one simple step in {title} today (15–30 min).",
    2: "Below norm: pick a micro‑step for {title} this week and schedule it.",
    3: "Medium: reinforce {title} with one regular action (2–3x/week).",
    4: "Good: lock in a working ritual in {title} and do a brief review.",
    5: "High: maintain {title} with a weekly 5‑min review.",
}

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_user_language(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    return getattr(user, "language", "ru") if user else "ru"


def _parse_question_index(question_id: Optional[str]) -> Optional[int]:
    if not question_id:
        return None
    matches = re.findall(r"\d+", str(question_id))
    if not matches:
        return None
    try:
        return int(matches[-1])
    except ValueError:
        return None


def _build_answers_payload(answers: List[Answer]) -> Dict[str, List[int]]:
    per_sphere: Dict[str, Dict[int, Tuple[int, int]]] = defaultdict(dict)
    for a in answers:
        if a.answer is None:
            continue
        sphere_key = str(a.sphere)
        qidx = _parse_question_index(a.question_id)
        if qidx is None:
            continue
        prev = per_sphere[sphere_key].get(qidx)
        if prev is None or (a.id is not None and a.id > prev[1]):
            per_sphere[sphere_key][qidx] = (a.answer, a.id or 0)
    payload: Dict[str, List[int]] = {}
    for sphere in [s["number"] for s in SPHERE_CONFIG]:
        qmap = per_sphere.get(sphere, {})
        if all(idx in qmap for idx in range(1, QUESTIONS_PER_SPHERE + 1)):
            ordered = [qmap[idx][0] for idx in range(1, QUESTIONS_PER_SPHERE + 1)]
            payload[sphere] = ordered
    return payload


def _score_to_level(score: float) -> int:
    # 1: ≤4.0, 2: 4.1–5.9, 3: 6.0–6.9, 4: 7.0–8.4, 5: ≥8.5
    if score <= 4.0:
        return 1
    if score < 6.0:
        return 2
    if score < 7.0:
        return 3
    if score < 8.5:
        return 4
    return 5


def _basic_structured(lang: str, sphere_scores: Optional[Dict[str, float]] = None) -> List[Dict]:
    now = datetime.utcnow()
    ts = now.isoformat()
    titles = SPHERE_TITLES_EN if lang == "en" else SPHERE_TITLES_RU
    default_texts = SHORT_BASIC_EN if lang == "en" else SHORT_BASIC_RU
    level_templates = LEVEL_TEMPLATES_EN if lang == "en" else LEVEL_TEMPLATES_RU
    structured: List[Dict] = []
    for i in range(1, 9):
        s = str(i)
        sphere_title = titles.get(s, s)
        if sphere_scores and s in sphere_scores:
            level = _score_to_level(float(sphere_scores.get(s, 0.0)))
            desc = level_templates.get(level, default_texts.get(s))
            desc = desc.format(title=sphere_title)
        else:
            desc = default_texts.get(s, ("One small weekly step (15–30 min)." if lang == "en" else "Один маленький шаг на неделе (15–30 мин)."))
        structured.append({
            "recommendation_id": f"basic_{s}_{int(now.timestamp())}",
            "timestamp": ts,
            "sphere": s,
            "type": "short_term",
            "priority": 0.2,
            "data": {
                # Один короткий текст: переносим в title
                "title": desc,
                "description": "",
                "action_steps": [],
                "metrics": {
                    "target_improvement": 0.3,
                    "timeframe": "2 weeks" if lang == "en" else "2 недели",
                    "success_criteria": []
                },
                "related_spheres": [],
                "evidence": {
                    "data_points": [],
                    "correlations": [],
                    "historical_success": 0.0
                }
            }
        })
    return structured


@router.get("/recommendations")
async def get_recommendations(
    date: Optional[str] = Query(None, description="Дата YYYY-MM-DD. Без даты используется последняя доступная."),
    lang: Optional[str] = Query(None, description="Язык 'ru'/'en'"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Основной эндпоинт для получения рекомендаций"""
    if not lang:
        lang = await get_user_language(user_id, db)

    # Пытаемся подстроить под пользователя по последней дате ответов
    try:
        stmt = select(Answer).where(Answer.user_id == user_id)
        result = await db.execute(stmt)
        all_answers: List[Answer] = result.scalars().all()
        dates = sorted({a.date.isoformat() for a in all_answers if a.date is not None})
        if dates:
            target_date = date if date else dates[-1]
            day_answers = [a for a in all_answers if a.date and a.date.isoformat() == target_date]
            payload = _build_answers_payload(day_answers)
            if payload:
                calculator = HPICalculator()
                _, sphere_scores = calculator.calculate_from_answers(payload)
                return {"recommendations": _basic_structured(lang, sphere_scores)}
    except Exception:
        pass

    # Если данных нет — отдаём дефолтные короткие
    return {"recommendations": _basic_structured(lang)}


@router.get("/recommendations/basic")
async def get_basic_recommendations(
    lang: str = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not lang:
        lang = await get_user_language(user_id, db)

    # Пытаемся подстроить под пользователя по последней дате ответов
    try:
        stmt = select(Answer).where(Answer.user_id == user_id)
        result = await db.execute(stmt)
        all_answers: List[Answer] = result.scalars().all()
        dates = sorted({a.date.isoformat() for a in all_answers if a.date is not None})
        if dates:
            target_date = dates[-1]
            day_answers = [a for a in all_answers if a.date and a.date.isoformat() == target_date]
            payload = _build_answers_payload(day_answers)
            if payload:
                calculator = HPICalculator()
                _, sphere_scores = calculator.calculate_from_answers(payload)
                return {"recommendations": _basic_structured(lang, sphere_scores)}
    except Exception:
        pass

    # Если данных нет — отдаём дефолтные короткие
    return {"recommendations": _basic_structured(lang)}


@router.get("/recommendations/ai")
async def get_ai_recommendations(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AIRecommendation).where(AIRecommendation.user_id == user_id))
        items = result.scalars().all()
        # Возвращаем полную структуру, если есть
        out = []
        for item in items:
            if item.data:
                obj = item.data
                obj.setdefault("sphere", str(item.sphere) if item.sphere is not None else None)
                out.append(obj)
            else:
                out.append({"sphere": str(item.sphere), "text": item.text})
        return {"ai_recommendations": out}
    except Exception:
        return {"ai_recommendations": []}


@router.post("/recommendations/ai/generate")
async def generate_ai_recs(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    date: Optional[str] = Query(None, description="Дата YYYY-MM-DD. Без даты используется последняя доступная."),
    lang: Optional[str] = Query(None, description="Язык 'ru'/'en'; без параметра берётся язык пользователя"),
    refresh: bool = Query(True, description="Если true — перезаписать старые AI рекомендации пользователя"),
    save: bool = Query(False, description="Если true — сохранять рекомендации в БД; по умолчанию не сохраняем"),
):
    if not lang:
        lang = await get_user_language(user_id, db)

    stmt = select(Answer).where(Answer.user_id == user_id)
    result = await db.execute(stmt)
    all_answers: List[Answer] = result.scalars().all()

    target_date: Optional[str] = date
    if not target_date:
        dates = sorted({a.date.isoformat() for a in all_answers if a.date is not None})
        target_date = dates[-1] if dates else None
    if not target_date:
        return {"ai_recommendations": [], "date": None}

    day_answers = [a for a in all_answers if a.date and a.date.isoformat() == target_date]
    payload = _build_answers_payload(day_answers)
    if not payload:
        # нет данных — ничего не генерируем
        return {"ai_recommendations": [], "date": target_date}

    calculator = HPICalculator()
    hpi, sphere_scores = calculator.calculate_from_answers(payload)

    # 1) получаем короткие тексты (LLM/фоллбек)
    simple_recs = generate_ai_recommendations(user_id=user_id, lang=lang, hpi=hpi, sphere_scores=sphere_scores)
    seed_texts = {str(r.get("sphere")): r.get("text", "") for r in simple_recs}

    # 2) подтягиваем PRO-данные для признаков
    pro_data = await collect_user_pro_data(db, user_id, target_date)

    # 3) формируем умные рекомендации с приоритизацией/типами/шагами/метриками/доказательствами
    structured = generate_smart_recommendations(
        user_id=user_id,
        lang=lang,
        hpi=hpi,
        sphere_scores=sphere_scores,
        pro=pro_data,
        seed_texts=seed_texts,
    )

    # Сохраняем при необходимости
    if save:
        if refresh:
            await db.execute(delete(AIRecommendation).where(AIRecommendation.user_id == user_id))
        for obj in structured:
            sphere_num = int(obj.get("sphere", "0") or 0)
            db.add(AIRecommendation(
                user_id=user_id,
                sphere=sphere_num,
                text=obj["data"]["description"],
                recommendation_id=obj["recommendation_id"],
                type=obj["type"],
                priority=obj.get("priority"),
                data=obj,
            ))
        await db.commit()

    return {"ai_recommendations": structured, "date": target_date, "hpi": hpi, "scores": sphere_scores} 