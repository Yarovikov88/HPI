"""
Lightweight HPI scoring core for API usage.
Contains only scoring logic and constants; no heavy dashboard imports.
"""
from typing import Dict, List, Optional, Tuple

MIN_ANSWER = 1
MAX_ANSWER = 4
QUESTIONS_PER_SPHERE = 6

FIBONACCI_SCORES = {1: 1.0, 2: 2.0, 3: 3.0, 4: 5.0}

SPHERE_CONFIG = [
    {"number": "1", "name": "Отношения с любимыми", "emoji": "💖"},
    {"number": "2", "name": "Отношения с родными", "emoji": "🏡"},
    {"number": "3", "name": "Друзья", "emoji": "🤝"},
    {"number": "4", "name": "Карьера", "emoji": "💼"},
    {"number": "5", "name": "Физическое здоровье", "emoji": "♂️"},
    {"number": "6", "name": "Ментальное здоровье", "emoji": "🧠"},
    {"number": "7", "name": "Хобби и увлечения", "emoji": "🎨"},
    {"number": "8", "name": "Благосостояние", "emoji": "💰"},
]

SPHERE_WEIGHTS = {str(i): 1.0 / 8.0 for i in range(1, 9)}


def apply_fibonacci_score(answer: int, inverse: bool = False) -> float:
    if inverse:
        answer = MAX_ANSWER - answer + 1
    return FIBONACCI_SCORES[answer]


def normalize_sphere_score(raw_score: float) -> float:
    min_possible = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[MIN_ANSWER]
    max_possible = QUESTIONS_PER_SPHERE * FIBONACCI_SCORES[MAX_ANSWER]
    normalized = ((raw_score - min_possible) / (max_possible - min_possible)) * 9 + 1
    return round(max(1.0, min(10.0, normalized)), 1)


def calculate_sphere_score(answers: List[int], inverse_questions: Optional[List[bool]] = None) -> Tuple[float, float]:
    if len(answers) != QUESTIONS_PER_SPHERE:
        raise ValueError(f"Требуется ровно {QUESTIONS_PER_SPHERE} ответов")
    if not all(MIN_ANSWER <= a <= MAX_ANSWER for a in answers):
        raise ValueError(f"Все ответы должны быть числами от {MIN_ANSWER} до {MAX_ANSWER}")
    if inverse_questions is None:
        inverse_questions = [False] * QUESTIONS_PER_SPHERE
    raw_score = sum(apply_fibonacci_score(a, inv) for a, inv in zip(answers, inverse_questions))
    normalized_score = normalize_sphere_score(raw_score)
    return raw_score, normalized_score


def calculate_total_hpi(sphere_scores: Dict[str, float]) -> float:
    total_weighted_score = 0.0
    total_weight = 0.0
    for sphere, score in sphere_scores.items():
        weight = SPHERE_WEIGHTS.get(sphere)
        if weight is not None and isinstance(score, (int, float)):
            total_weighted_score += score * weight
            total_weight += weight
    if total_weight == 0:
        return 0.0
    hpi_score = ((total_weighted_score / total_weight - 1) * (80 / 9)) + 20
    return round(max(20.0, min(100.0, hpi_score)), 1)


class HPICalculator:
    def calculate_from_answers(self, answers: Dict[str, List[int]]) -> Tuple[float, Dict[str, float]]:
        sphere_scores: Dict[str, float] = {}
        for sphere in SPHERE_CONFIG:
            key = sphere["number"]
            ans = answers.get(key, [])
            if len(ans) == QUESTIONS_PER_SPHERE:
                # Конвертируем строки в числа
                try:
                    numeric_ans = [int(a) for a in ans]
                except (ValueError, TypeError):
                    sphere_scores[key] = 0.0
                    continue
                
                inverse_questions = [False] * QUESTIONS_PER_SPHERE
                if key in ["4", "6", "8"]:
                    inverse_questions[-1] = True
                try:
                    _, normalized = calculate_sphere_score(numeric_ans, inverse_questions)
                except Exception:
                    normalized = 0.0
                sphere_scores[key] = normalized
            else:
                sphere_scores[key] = 0.0
        hpi_total = calculate_total_hpi(sphere_scores)
        return hpi_total, sphere_scores 