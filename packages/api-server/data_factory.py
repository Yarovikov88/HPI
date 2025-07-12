"""
HPI Data Factory
Version: 1.2
Status: Production
Модуль для генерации реалистичных наборов тестовых данных
для различных сценариев пользовательского опыта.
"""
print("--- DEBUG: data_factory.py (version 1.2) is being imported ---")

from sqlalchemy.orm import Session
import logging
from . import models
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import joinedload

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Канонический маппинг русских названий сфер в их ID
SPHERE_NAME_TO_ID = {
    "Отношения с любимыми": "love",
    "Отношения с родными": "family",
    "Друзья": "friends",
    "Карьера": "career",
    "Физическое здоровье": "physical",
    "Ментальное здоровье": "mental",
    "Хобби и увлечения": "hobby",
    "Благосостояние": "wealth",
    # Алиасы, используемые в сценариях
    "Здоровье": "physical",
    "Обучение": "hobby",
    "Финансы": "wealth",
}

def clear_user_data(db: Session, user_id: int):
    """
    Полностью удаляет все базовые и Pro-ответы для указанного пользователя.
    """
    logging.info(f"Начало полной очистки данных для пользователя ID: {user_id}")
    
    models_to_clear = [
        models.Answer, models.Problem, models.Goal,
        models.Blocker, models.Achievement, models.Metric
    ]

    total_deleted = 0
    for model in models_to_clear:
        table_name = model.__tablename__
        try:
            deleted_rows = db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
            logging.info(f"Удалено {deleted_rows} записей из таблицы '{table_name}'.")
            total_deleted += deleted_rows
        except Exception as e:
            logging.error(f"Ошибка при удалении данных из таблицы '{table_name}': {e}")
            db.rollback()
            raise

    db.commit()
    logging.info(f"Данные для пользователя ID: {user_id} успешно очищены. Всего удалено {total_deleted} записей.")


def _create_answers_for_date(db: Session, user_id: int, questions: list, date: datetime, trends: dict):
    """Вспомогательная функция для создания ответов на одну дату."""
    created_answers = []
    for q_data in questions:
        sphere_name = q_data['sphere_name']
        trend_function = trends.get(sphere_name, lambda d: random.randint(5, 8))
        value = trend_function(date)
        
        answer = models.Answer(
            question_id=q_data['id'],
            user_id=user_id,
            sphere_id=q_data['sphere_id'],
            answer=value,
            created_at=date
        )
        db.add(answer)
        created_answers.append(answer)
    return created_answers


def generate_burnout_scenario(db: Session, user_id: int):
    """
    Генерирует данные по сценарию "Профессиональное выгорание" и возвращает их.
    """
    logging.info(f"Генерация сценария 'Выгорание' для пользователя ID: {user_id}")
    
    # Загружаем вопросы и создаем удобный словарь для работы
    questions = db.query(models.Question).options(joinedload(models.Question.sphere)).all()
    questions_dict = [{"id": q.id, "sphere_id": q.sphere_id, "sphere_name": q.sphere.name} for q in questions if q.sphere]

    dates = [(datetime.now() - timedelta(weeks=i*2)) for i in range(5)][::-1]
    start_date, end_date = dates[0], dates[-1]
    total_days = (end_date - start_date).days or 1
    
    # Тренды основаны на русских названиях сфер
    trends = {
        "Карьера": lambda d: int(8 - 4 * ((d - start_date).days / total_days)),
        "Здоровье": lambda d: int(7 - 3 * ((d - start_date).days / total_days))
    }

    all_generated_answers = []
    all_generated_pro_answers = []

    for date in dates:
        all_generated_answers.extend(_create_answers_for_date(db, user_id, questions_dict, date, trends))
    
    pro_items = [
        models.Problem(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Карьера"], text="Чувствую полный застой и отсутствие интересных задач.", created_at=dates[-1]),
        models.Blocker(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Карьера"], text="Высокая нагрузка по текущим проектам не оставляет времени на обучение.", created_at=dates[-2]),
        models.Problem(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Здоровье"], text="Постоянная усталость и проблемы со сном.", created_at=dates[-1])
    ]
    db.add_all(pro_items)
    all_generated_pro_answers.extend(pro_items)

    db.commit()
    return {"answers": all_generated_answers, "pro_answers": all_generated_pro_answers}


def generate_growth_scenario(db: Session, user_id: int):
    """
    Генерирует данные по сценарию "Личностный рост".
    """
    logging.info(f"Генерация сценария 'Личностный рост' для пользователя ID: {user_id}")
    
    questions = db.query(models.Question).options(joinedload(models.Question.sphere)).all()
    questions_dict = [{"id": q.id, "sphere_id": q.sphere_id, "sphere_name": q.sphere.name} for q in questions if q.sphere]
    
    dates = [(datetime.now() - timedelta(weeks=i*2)) for i in range(5)][::-1]
    start_date, end_date = dates[0], dates[-1]
    total_days = (end_date - start_date).days or 1
    
    trends = {
        "Обучение": lambda d: int(5 + 4 * ((d - start_date).days / total_days)),
        "Финансы": lambda d: int(6 + 2 * ((d - start_date).days / total_days)),
        "Карьера": lambda d: int(6 + 3 * ((d - start_date).days / total_days)),
    }

    all_generated_answers = []
    all_generated_pro_answers = []

    for date in dates:
        all_generated_answers.extend(_create_answers_for_date(db, user_id, questions_dict, date, trends))
    
    pro_items = [
        models.Goal(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Карьера"], text="Получить повышение до Senior-разработчика в течение 6 месяцев.", created_at=dates[1]),
        models.Achievement(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Обучение"], description="Завершил продвинутый курс по Python.", created_at=dates[-2]),
        models.Achievement(user_id=user_id, sphere_id=SPHERE_NAME_TO_ID["Финансы"], description="Создал финансовую подушку на 3 месяца.", created_at=dates[-1])
    ]
    db.add_all(pro_items)
    all_generated_pro_answers.extend(pro_items)

    db.commit()
    return {"answers": all_generated_answers, "pro_answers": all_generated_pro_answers}

SCENARIOS = {
    "burnout": generate_burnout_scenario,
    "growth": generate_growth_scenario,
}

def seed_scenario(db: Session, user_id: int, scenario_name: str):
    """
    Главная функция. Очищает старые данные, генерирует новые и ВОЗВРАЩАЕТ их.
    """
    if scenario_name not in SCENARIOS:
        logging.error(f"Сценарий '{scenario_name}' не найден.")
        raise ValueError(f"Unknown scenario: {scenario_name}")

    clear_user_data(db, user_id)
    scenario_function = SCENARIOS[scenario_name]
    generated_data = scenario_function(db, user_id)

    logging.info(f"Сценарий '{scenario_name}' успешно сгенерирован для пользователя ID: {user_id}")
    return generated_data 
