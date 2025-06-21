"""
Тестовый скрипт для проверки AI-рекомендаций.
"""

import logging
import os

from logging_config import setup_logging

# Настраиваем логирование
setup_logging()

# Загружаем переменные окружения
logging.debug("Загружаем переменные окружения...")


def main():
    """Основная функция тестирования."""
    logging.debug("Начало выполнения main()")

    # Проверяем наличие API ключа
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY не найден в .env файле")
        return
    else:
        logging.debug("API ключ найден")

    try:
        logging.debug("Импортируем необходимые модули...")
        from src.dashboard.ai import AIRecommendationEngine
        from src.dashboard.test_data import get_test_history, get_test_pro_data

        # Получаем тестовые данные
        logging.debug("Получаем тестовые данные...")
        pro_data = get_test_pro_data()
        history = get_test_history()

        # Создаем движок рекомендаций
        logging.debug("Создаем движок рекомендаций...")
        engine = AIRecommendationEngine()

        # Тестируем генерацию для сферы "Карьера"
        logging.info("Генерирую рекомендацию для сферы 'Карьера'...")
        recommendation = engine.generate_recommendation(
            sphere="Карьера", pro_data=pro_data, history=history
        )

        if recommendation:
            logging.info("Рекомендация успешно сгенерирована:")
            logging.info(f"Название: {recommendation.title}")
            logging.info(f"Описание: {recommendation.description}")
            logging.info("\nШаги:")
            for i, step in enumerate(recommendation.action_steps, 1):
                logging.info(f"{i}. {step.description}")
                logging.info(f"   - Ожидаемый эффект: {step.expected_impact:.2f}")
                logging.info(f"   - Оценка времени: {step.estimated_time}")

            logging.info("\nДоказательная база:")
            for point in recommendation.evidence.data_points:
                logging.info(f"- {point}")
        else:
            logging.error("Не удалось сгенерировать рекомендацию")

    except Exception as e:
        logging.error(
            f"Ошибка при тестировании: {e}",
            exc_info=True,
        )


def test_sphere_normalization():
    """
    Проверяет, что все ключи сфер в данных пользователя соответствуют
    master-списку сфер из базы вопросов.
    """
    import os

    from src.dashboard.normalizers import SphereNormalizer
    from src.dashboard.parsers.questions import QuestionsDatabaseParser
    from src.dashboard.test_data import get_test_pro_data

    # Путь к базе вопросов
    db_path = os.path.join(os.path.dirname(__file__), "database", "questions.md")
    parser = QuestionsDatabaseParser(db_path)
    master_spheres = set(parser.parse_spheres_master_list())
    normalizer = SphereNormalizer()

    pro_data = get_test_pro_data()

    # Собираем все сферы из данных пользователя
    all_spheres = set()
    all_spheres.update(pro_data.scores.keys())
    all_spheres.update(pro_data.problems.keys())
    all_spheres.update(pro_data.goals.keys())
    all_spheres.update(pro_data.blockers.keys())
    all_spheres.update(pro_data.achievements.keys())
    all_spheres.update([m.sphere for m in pro_data.metrics])

    # Проверяем, что все сферы нормализованы и есть в master-списке
    for sphere in all_spheres:
        normalized = normalizer.normalize(sphere)
        assert normalized in master_spheres, (
            f"Сфера '{sphere}' (нормализовано: '{normalized}') "
            f"отсутствует в master-списке: {master_spheres}"
        )
    print(
        "[TEST PASSED] Все сферы в данных пользователя "
        "соответствуют master-списку сфер."
    )


if __name__ == "__main__":
    logging.debug("Запуск скрипта")
    main()
    # Запуск теста на нормализацию сфер
    test_sphere_normalization()
