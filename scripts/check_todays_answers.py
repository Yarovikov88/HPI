import sys
import os
from sqlalchemy import func
from datetime import date

# Добавляем корневую директорию проекта в sys.path
# Это гарантирует, что мы сможем импортировать 'packages'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.api_server.database import get_db, Base
from packages.api_server import models

def check_answers():
    db = next(get_db())
    user_id_to_check = 179
    today = date.today()

    print(f"--- Проверка ответов для пользователя ID: {user_id_to_check} за {today} ---")

    # Получаем вопросы базовой диагностики, чтобы сгруппировать ответы
    basic_questions = db.query(models.Question).filter(models.Question.category == None).all()
    questions_by_sphere = {}
    for q in basic_questions:
        if q.sphere_id not in questions_by_sphere:
            questions_by_sphere[q.sphere_id] = []
        questions_by_sphere[q.sphere_id].append(q.id)
    
    # Получаем все сегодняшние ответы пользователя
    todays_answers = db.query(models.Answer).filter(
        models.Answer.user_id == user_id_to_check,
        func.date(models.Answer.created_at) == today
    ).all()

    if not todays_answers:
        print("!!! В базе данных НЕТ ответов за сегодня для этого пользователя.")
        return

    print(f"Найдено всего ответов за сегодня: {len(todays_answers)}")
    print("-" * 20)

    # Группируем найденные ответы по сферам
    answers_by_sphere = {}
    for answer in todays_answers:
        # Находим, к какой сфере относится вопрос
        sphere_id_for_answer = None
        for sphere_id, question_ids in questions_by_sphere.items():
            if answer.question_id in question_ids:
                sphere_id_for_answer = sphere_id
                break
        
        if sphere_id_for_answer:
            if sphere_id_for_answer not in answers_by_sphere:
                answers_by_sphere[sphere_id_for_answer] = 0
            answers_by_sphere[sphere_id_for_answer] += 1

    # Выводим статистику
    all_spheres_complete = True
    for sphere_id, question_ids in questions_by_sphere.items():
        # Получаем имя сферы для более читаемого вывода
        sphere_name = db.query(models.Sphere.name).filter(models.Sphere.id == sphere_id).scalar() or sphere_id
        count = answers_by_sphere.get(sphere_id, 0)
        expected_count = len(question_ids)
        is_complete = "✅" if count == expected_count else "❌"
        if count != expected_count:
            all_spheres_complete = False
        print(f"Сфера '{sphere_name}': Найдено {count}/{expected_count} ответов. {is_complete}")
    
    print("-" * 20)
    if all_spheres_complete:
        print("✅ Все сферы в базе данных выглядят завершенными. Проблема, скорее всего, в логике роутера дашборда.")
    else:
        print("❌ Не все сферы в базе данных завершены. Проблема может быть в сохранении ответов или в том, как фронтенд определяет 'завершенность'.")


if __name__ == "__main__":
    check_answers() 