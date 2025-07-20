import requests
import random
from datetime import datetime

# --- Конфигурация ---
API_BASE_URL = "http://localhost:8000/api/v1"
USER_ID = 179 # ID пользователя для тестов
DATES_TO_SEED = [
    "2025-07-01",
    "2025-07-04",
    "2025-07-07",
    "2025-07-09",
]

def get_basic_questions():
    """Получает список базовых вопросов с сервера."""
    try:
        response = requests.get(f"{API_BASE_URL}/questions")
        response.raise_for_status()
        all_questions = response.json()
        # Фильтруем, чтобы оставить только базовые вопросы (без категории)
        basic_questions = [q for q in all_questions if q.get('category') is None]
        print(f"Найдено {len(basic_questions)} базовых вопросов.")
        return basic_questions
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении вопросов: {e}")
        return []

def submit_answer(question_id, answer_value, date_str):
    """Отправляет один ответ на сервер с указанной датой."""
    payload = {
        "questionId": question_id,
        "userId": USER_ID,
        "value": answer_value,
        "created_at": f"{date_str}T12:00:00Z" # Добавляем время, чтобы было валидно
    }
    try:
        response = requests.post(f"{API_BASE_URL}/answer", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке ответа для вопроса {question_id}: {e}")
        print(f"Ответ сервера: {e.response.text if e.response else 'N/A'}")
        return None

def main():
    """Главная функция для генерации данных."""
    print("Запуск скрипта для заполнения базы данных ответами...")
    questions = get_basic_questions()
    if not questions:
        print("Вопросы не найдены. Завершение работы.")
        return

    total_answers_sent = 0
    for date_str in DATES_TO_SEED:
        print(f"\n--- Генерация ответов для даты: {date_str} ---")
        answers_for_date = 0
        for question in questions:
            # Генерируем случайный ответ от 1 до 4
            random_answer = random.randint(1, 4)
            result = submit_answer(question['id'], random_answer, date_str)
            if result and result.get("status") == "success":
                answers_for_date += 1
        print(f"Успешно отправлено {answers_for_date} ответов для {date_str}.")
        total_answers_sent += answers_for_date

    print(f"\nСкрипт завершен. Всего отправлено ответов: {total_answers_sent}.")

if __name__ == "__main__":
    main() 