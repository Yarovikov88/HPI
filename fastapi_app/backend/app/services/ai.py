from typing import Dict, List, Optional
import os
import asyncio
import json
from datetime import datetime, timedelta
from app.cache import cache_manager

WEAK_THRESHOLD = 6.0
STRONG_THRESHOLD = 8.0

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

# Кэш для AI рекомендаций
AI_CACHE_TTL = 3600  # 1 час


def _title(lang: str, sphere: str) -> str:
    return (SPHERE_TITLES_EN if lang == "en" else SPHERE_TITLES_RU).get(sphere, sphere)


def _fallback_recommendations(lang: str, sphere_scores: Dict[str, float]) -> List[Dict[str, str]]:
    """Генерирует базовые рекомендации без AI"""
    recs: List[Dict[str, str]] = []
    for sphere, score in sphere_scores.items():
        if sphere not in [str(i) for i in range(1, 9)]:
            continue
        t = _title(lang, sphere)
        if score < WEAK_THRESHOLD and score > 0:
            if lang == "en":
                text = f"{t}: pick one small habit to improve this week (15–30 min, 3x/week). Track progress and reflect on blockers."
            else:
                text = f"{t}: выбери одну маленькую привычку на неделю (15–30 минут, 3 раза/нед). Отслеживай прогресс и причины срывов."
        elif score >= STRONG_THRESHOLD:
            if lang == "en":
                text = f"{t}: lock in what's working. Schedule a weekly review to maintain the level and spot early dips."
            else:
                text = f"{t}: закрепи работающие практики. Делай недельный обзор, чтобы удерживать уровень и вовремя замечать просадки."
        else:
            if lang == "en":
                text = f"{t}: choose one optimization (timeboxing, accountability partner, or clear metric). Review in 2 weeks."
            else:
                text = f"{t}: выбери одну оптимизацию (таймбокс, партнёр по ответственности или метрика). Пересмотри через 2 недели."
        recs.append({"sphere": sphere, "text": text})
    return recs


def _format_scores_for_prompt(lang: str, hpi: float, sphere_scores: Dict[str, float]) -> str:
    """Форматирует оценки для AI промпта"""
    lines = []
    lines.append(("HPI:", "Итоговый HPI:")[lang != "en"] + f" {hpi:.1f}")
    for i in range(1, 9):
        s = str(i)
        lines.append(f"{_title(lang, s)}: {sphere_scores.get(s, 0.0):.1f}")
    return "\n".join(lines)


async def _openai_generate_async(lang: str, hpi: float, sphere_scores: Dict[str, float]) -> List[Dict[str, str]]:
    """Асинхронная генерация рекомендаций через OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []
    
    try:
        # Импортируем OpenAI асинхронно
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=api_key)
        locale = "ru" if lang != "en" else "en"
        
        system = (
            "You are an HPI coach. Create one short, actionable recommendation per sphere (8 spheres)."
            if lang == "en"
            else "Ты HPI-коуч. Сформируй по одной короткой, применимой рекомендации на каждую из 8 сфер."
        )
        
        user = (
            "Generate recommendations based on scores (1-10 per sphere, HPI 20-100). Return JSON array of {sphere: '1'..'8', text}."
            if lang == "en"
            else "Сгенерируй рекомендации на основе оценок (1-10 по сферам, HPI 20-100). Верни JSON-массив объектов {sphere: '1'..'8', text}."
        )
        
        payload = _format_scores_for_prompt(lang, hpi, sphere_scores)
        msg = f"{user}\n\nScores:\n{payload}"
        
        # Асинхронный вызов OpenAI с таймаутом
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": msg},
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                    max_tokens=1000,
                ),
                timeout=15.0  # 15 секунд таймаут
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Обрабатываем ответ
            arr = data.get("recommendations") if isinstance(data, dict) else None
            if arr is None and isinstance(data, list):
                arr = data
            if not isinstance(arr, list):
                return []
            
            # Валидируем и очищаем данные
            out: List[Dict[str, str]] = []
            for item in arr:
                sphere = str(item.get("sphere"))
                text = str(item.get("text", "")).strip()
                if sphere in [str(i) for i in range(1, 9)] and text:
                    out.append({"sphere": sphere, "text": text})
            
            return out
            
        except asyncio.TimeoutError:
            print("OpenAI API timeout")
            return []
            
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return []


async def _openai_generate(lang: str, hpi: float, sphere_scores: Dict[str, float]) -> List[Dict[str, str]]:
    """Синхронная обертка для совместимости"""
    return await _openai_generate_async(lang, hpi, sphere_scores)


async def generate_ai_recommendations_async(
    user_id: int, 
    lang: str, 
    hpi: float, 
    sphere_scores: Dict[str, float]
) -> List[Dict[str, str]]:
    """Асинхронная генерация AI рекомендаций с кэшированием"""
    
    # Генерируем ключ кэша
    cache_key = f"ai_recs:{user_id}:{lang}:{hpi:.1f}:{hash(frozenset(sphere_scores.items()))}"
    
    # Пытаемся получить из кэша
    cached_recs = await cache_manager.get(cache_key)
    if cached_recs:
        return cached_recs
    
    # Если нет в кэше, генерируем новые
    try:
        # Пытаемся использовать OpenAI
        recs = await _openai_generate_async(lang, hpi, sphere_scores)
        
        if recs:
            # Сохраняем в кэш
            await cache_manager.set(cache_key, recs, AI_CACHE_TTL)
            return recs
        
        # Fallback к локальным правилам
        fallback_recs = _fallback_recommendations(lang, sphere_scores)
        await cache_manager.set(cache_key, fallback_recs, AI_CACHE_TTL)
        return fallback_recs
        
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        # В случае ошибки возвращаем fallback
        fallback_recs = _fallback_recommendations(lang, sphere_scores)
        await cache_manager.set(cache_key, fallback_recs, AI_CACHE_TTL)
        return fallback_recs


def generate_ai_recommendations(
    user_id: int, 
    lang: str, 
    hpi: float, 
    sphere_scores: Dict[str, float]
) -> List[Dict[str, str]]:
    """Синхронная обертка для совместимости"""
    # Запускаем асинхронную функцию в event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если loop уже запущен, используем fallback
            return _fallback_recommendations(lang, sphere_scores)
        else:
            return loop.run_until_complete(
                generate_ai_recommendations_async(user_id, lang, hpi, sphere_scores)
            )
    except RuntimeError:
        # Нет event loop, используем fallback
        return _fallback_recommendations(lang, sphere_scores)


async def batch_generate_recommendations(
    users_data: List[Dict]
) -> Dict[int, List[Dict[str, str]]]:
    """Пакетная генерация рекомендаций для нескольких пользователей"""
    tasks = []
    user_ids = []
    
    for user_data in users_data:
        user_id = user_data["user_id"]
        lang = user_data["lang"]
        hpi = user_data["hpi"]
        sphere_scores = user_data["sphere_scores"]
        
        task = generate_ai_recommendations_async(user_id, lang, hpi, sphere_scores)
        tasks.append(task)
        user_ids.append(user_id)
    
    # Выполняем все задачи параллельно
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Формируем результат
    recommendations = {}
    for user_id, result in zip(user_ids, results):
        if isinstance(result, Exception):
            # В случае ошибки используем fallback
            lang = next((u["lang"] for u in users_data if u["user_id"] == user_id), "ru")
            sphere_scores = next((u["sphere_scores"] for u in users_data if u["user_id"] == user_id), {})
            recommendations[user_id] = _fallback_recommendations(lang, sphere_scores)
        else:
            recommendations[user_id] = result
    
    return recommendations


async def clear_ai_cache(user_id: Optional[int] = None):
    """Очищает кэш AI рекомендаций"""
    if user_id:
        pattern = f"ai_recs:{user_id}:*"
    else:
        pattern = "ai_recs:*"
    
    return await cache_manager.delete_pattern(pattern) 