"""
Калькулятор HPI для Telegram-бота
"""
from typing import Dict, List, Optional
import logging


class HPICalculator:
    """Калькулятор Human Performance Index."""
    
    def __init__(self):
        # Нелинейная шкала Фибоначчи для преобразования ответов
        self.fibonacci_scores = {
            1: 1.0,  # Базовый уровень
            2: 2.0,  # Средний уровень
            3: 3.0,  # Хороший уровень
            4: 5.0   # Отличный уровень
        }
        
        # Веса сфер (равные веса для всех сфер)
        self.sphere_weights = {
            "1": 0.125,  # Отношения с любимыми
            "2": 0.125,  # Отношения с родными
            "3": 0.125,  # Друзья
            "4": 0.125,  # Карьера
            "5": 0.125,  # Физическое здоровье
            "6": 0.125,  # Ментальное здоровье
            "7": 0.125,  # Хобби
            "8": 0.125   # Благосостояние
        }
        
        self.logger = logging.getLogger(__name__)
    
    def apply_fibonacci_score(self, answer: int, inverse: bool = False) -> float:
        """Применяет нелинейное преобразование Фибоначчи к ответу."""
        if inverse:
            answer = 5 - answer  # Инвертируем: 4->1, 3->2, 2->3, 1->4
        return self.fibonacci_scores[answer]
    
    def normalize_sphere_score(self, raw_score: float) -> float:
        """Нормализация оценки сферы в шкалу 1-10."""
        questions_per_sphere = 6
        min_possible = questions_per_sphere * self.fibonacci_scores[1]  # 6 * 1.0 = 6.0
        max_possible = questions_per_sphere * self.fibonacci_scores[4]  # 6 * 5.0 = 30.0
        
        normalized = ((raw_score - min_possible) / (max_possible - min_possible)) * 9 + 1
        return round(max(1.0, min(10.0, normalized)), 1)
    
    def calculate_sphere_score(self, answers: List[int], inverse_questions: Optional[List[bool]] = None) -> float:
        """Расчет нормализованного счета для сферы."""
        if len(answers) != 6:
            raise ValueError(f"Требуется ровно 6 ответов, получено {len(answers)}")
        
        if not all(1 <= a <= 4 for a in answers):
            raise ValueError(f"Все ответы должны быть числами от 1 до 4")
        
        if inverse_questions is None:
            inverse_questions = [False] * 6
        
        # Применяем шкалу Фибоначчи к каждому ответу
        raw_score = sum(self.apply_fibonacci_score(a, inv) for a, inv in zip(answers, inverse_questions))
        normalized_score = self.normalize_sphere_score(raw_score)
        
        return normalized_score
    
    def calculate_scores(self, answers: Dict[str, List[int]]) -> Dict[str, float]:
        """Рассчитывает оценки для всех сфер."""
        scores = {}
        
        for sphere_num, sphere_answers in answers.items():
            try:
                # Определяем, какие вопросы инвертированы
                inverse_questions = [False] * 6
                if sphere_num in ["4", "6", "8"]:  # Сферы с инвертированными вопросами
                    inverse_questions[-1] = True  # Последний вопрос инвертирован
                
                score = self.calculate_sphere_score(sphere_answers, inverse_questions)
                scores[sphere_num] = score
                
            except Exception as e:
                self.logger.error(f"Ошибка расчета для сферы {sphere_num}: {e}")
                scores[sphere_num] = 1.0  # Минимальная оценка при ошибке
        
        return scores
    
    def calculate_total_hpi(self, sphere_scores: Dict[str, float]) -> float:
        """Расчет итогового HPI с учетом весов сфер."""
        total_weighted_score = 0
        total_weight = 0
        
        for sphere, score in sphere_scores.items():
            weight = self.sphere_weights.get(sphere)
            if weight is not None and isinstance(score, (int, float)):
                total_weighted_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            raise ValueError("Не найдены веса для сфер")
        
        # Преобразование взвешенного среднего (1-10) в шкалу 20-100
        hpi_score = ((total_weighted_score / total_weight - 1) * (80/9)) + 20
        return round(max(20.0, min(100.0, hpi_score)), 1) 