"""
Базовое тестирование системы HPI без AI-компонента.
"""
import os
import sys

# Добавляем корневую директорию проекта в PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.calculator import calculate_sphere_score, calculate_total_hpi, normalize_sphere_score

def test_sphere_score_calculation():
    """Тест расчета оценки для сферы."""
    # Тестовые ответы (6 вопросов, оценки от 1 до 4)
    answers = [3, 4, 2, 3, 4, 3]
    raw_score, normalized_score = calculate_sphere_score(answers)
    
    # Проверяем что оценка в диапазоне 1-10
    assert 1.0 <= normalized_score <= 10.0
    print(f"Тест расчета сферы пройден. Оценка: {normalized_score}")

def test_total_hpi_calculation():
    """Тест расчета общего HPI."""
    # Тестовые оценки по сферам
    sphere_scores = {
        "1": 7.5,  # Отношения с любимыми
        "2": 8.0,  # Отношения с родными
        "3": 6.5,  # Друзья
        "4": 7.0,  # Карьера
        "5": 8.5,  # Физическое здоровье
        "6": 7.5,  # Ментальное здоровье
        "7": 6.0,  # Хобби
        "8": 7.0   # Благосостояние
    }
    
    hpi = calculate_total_hpi(sphere_scores)
    
    # Проверяем что HPI в диапазоне 20-100
    assert 20.0 <= hpi <= 100.0
    print(f"Тест расчета HPI пройден. Значение: {hpi}")

if __name__ == "__main__":
    print("Запуск базовых тестов HPI...")
    test_sphere_score_calculation()
    test_total_hpi_calculation()
    print("Все тесты успешно пройдены!") 