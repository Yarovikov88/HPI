from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.models import Problem, Goal, Blocker, Achievement

SphereId = str

async def collect_user_pro_data(db, user_id: int, date_iso: Optional[str]) -> Dict[SphereId, Dict[str, List[str]]]:
    from sqlalchemy.future import select
    pro: Dict[SphereId, Dict[str, List[str]]] = {str(i): {"problems": [], "goals": [], "blockers": [], "achievements": []} for i in range(1, 9)}
    if not date_iso:
        return pro
    # Parse YYYY-MM-DD to date for equality filter
    from sqlalchemy import func
    try:
        # Problems
        result = await db.execute(select(Problem).where(Problem.user_id == user_id, Problem.date == func.to_date(date_iso, 'YYYY-MM-DD')))
        for row in result.scalars().all():
            pro.setdefault(str(row.sphere), {"problems": [], "goals": [], "blockers": [], "achievements": []})["problems"].append(row.text)
        # Goals
        result = await db.execute(select(Goal).where(Goal.user_id == user_id, Goal.date == func.to_date(date_iso, 'YYYY-MM-DD')))
        for row in result.scalars().all():
            pro.setdefault(str(row.sphere), {"problems": [], "goals": [], "blockers": [], "achievements": []})["goals"].append(row.text)
        # Blockers
        result = await db.execute(select(Blocker).where(Blocker.user_id == user_id, Blocker.date == func.to_date(date_iso, 'YYYY-MM-DD')))
        for row in result.scalars().all():
            pro.setdefault(str(row.sphere), {"problems": [], "goals": [], "blockers": [], "achievements": []})["blockers"].append(row.text)
        # Achievements
        result = await db.execute(select(Achievement).where(Achievement.user_id == user_id, Achievement.date == func.to_date(date_iso, 'YYYY-MM-DD')))
        for row in result.scalars().all():
            pro.setdefault(str(row.sphere), {"problems": [], "goals": [], "blockers": [], "achievements": []})["achievements"].append(row.description)
    except Exception:
        # If tables missing — return what we have
        pass
    return pro


def _detect_hyperfocus(sphere_scores: Dict[SphereId, float]) -> bool:
    highs = [s for s in sphere_scores.values() if s >= 9.0]
    lows = [s for s in sphere_scores.values() if s <= 6.0]
    return len(highs) >= 1 and len(lows) >= 3


def _priority_for_score(score: float) -> float:
    if score <= 4.0:
        return 0.9
    if score < 6.0:
        return 0.75
    if score < 8.0:
        return 0.5
    return 0.2


def _type_for_score(score: float) -> str:
    if score < 6.0:
        return "immediate"
    if score < 8.0:
        return "short_term"
    return "long_term"


def _default_step(lang: str, sphere_title: str) -> Dict:
    if lang == 'en':
        return {"step": 1, "description": f"Choose one small weekly habit for {sphere_title} (15–30 min, 3x/week).", "expected_impact": 0.3, "estimated_time": "2 weeks", "dependencies": []}
    return {"step": 1, "description": f"Выбери одну маленькую недельную привычку для сферы «{sphere_title}» (15–30 мин, 3 раза/нед).", "expected_impact": 0.3, "estimated_time": "2 недели", "dependencies": []}


SPHERE_TITLES_RU = {
    "1": "Отношения с любимыми",
    "2": "Отношения с родными",
    "3": "Друзья",
    "4": "Карьера",
    "5": "Физическое здоровье",
    "6": "Ментальное здоровье",
    "7": "Хобби и увлечения",
    "8": "Благосостояние",
}

SPHERE_TITLES_EN = {
    "1": "Romantic relationships",
    "2": "Family relationships",
    "3": "Friends",
    "4": "Career",
    "5": "Physical health",
    "6": "Mental health",
    "7": "Hobbies and interests",
    "8": "Wealth",
}


def _title(lang: str, sphere: SphereId) -> str:
    return (SPHERE_TITLES_EN if lang == 'en' else SPHERE_TITLES_RU).get(sphere, sphere)


def generate_smart_recommendations(
    user_id: int,
    lang: str,
    hpi: float,
    sphere_scores: Dict[SphereId, float],
    pro: Dict[SphereId, Dict[str, List[str]]],
    seed_texts: Optional[Dict[SphereId, str]] = None,
) -> List[Dict]:
    now = datetime.utcnow()
    ts = now.isoformat()
    hyper = _detect_hyperfocus(sphere_scores)
    recs: List[Dict] = []
    for i in range(1, 9):
        s = str(i)
        score = float(sphere_scores.get(s, 0.0))
        base_prio = _priority_for_score(score)
        rtype = _type_for_score(score)
        sphere_title = _title(lang, s)
        p = pro.get(s, {"problems": [], "goals": [], "blockers": [], "achievements": []})
        # Adjust priority by blockers/problems
        if p.get("blockers"):
            base_prio = min(1.0, base_prio + 0.1)
        if p.get("problems"):
            base_prio = min(1.0, base_prio + 0.05)
        if hyper and score <= 6.0:
            base_prio = min(1.0, base_prio + 0.05)
        # Description (seed from LLM if any)
        desc = (seed_texts or {}).get(s)
        if not desc:
            if lang == 'en':
                desc = f"{sphere_title}: focus on 1 small, consistent improvement this week."
            else:
                desc = f"{sphere_title}: сфокусируйся на 1 маленьком стабильном улучшении на этой неделе."
        # Steps
        steps: List[Dict] = []
        if p.get("problems"):
            problem = p["problems"][0]
            if lang == 'en':
                steps.append({"step": 1, "description": f"Define one concrete action targeting: {problem}", "expected_impact": 0.4, "estimated_time": "1-2 weeks", "dependencies": []})
            else:
                steps.append({"step": 1, "description": f"Определи одно конкретное действие под проблему: {problem}", "expected_impact": 0.4, "estimated_time": "1-2 недели", "dependencies": []})
        steps.append(_default_step(lang, sphere_title))
        # Metrics
        metrics = {
            "target_improvement": 0.5 if score < 6.0 else 0.3,
            "timeframe": "2 weeks" if lang == 'en' else "2 недели",
            "success_criteria": [
                ("3 of 3 scheduled habits completed" if lang == 'en' else "Выполнить 3 из 3 запланированных привычек"),
                ("Weekly reflection done" if lang == 'en' else "Сделан недельный разбор"),
            ],
        }
        # Evidence
        evidence = {
            "data_points": p.get("problems", [])[:3] + p.get("goals", [])[:3],
            "correlations": [],
            "historical_success": 0.0,
        }
        recs.append({
            "recommendation_id": f"rec_{user_id}_{s}_{int(now.timestamp())}",
            "timestamp": ts,
            "sphere": s,
            "type": rtype,
            "priority": round(base_prio, 2),
            "data": {
                "title": desc[:60] or ("Recommendation" if lang == 'en' else "Рекомендация"),
                "description": desc,
                "action_steps": steps,
                "metrics": metrics,
                "related_spheres": [],
                "evidence": evidence,
            },
        })
    return recs 