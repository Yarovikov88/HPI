"""
Тестовый скрипт для проверки AI-рекомендаций.
"""
import os
import logging
from datetime import datetime

from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,  # Изменено на DEBUG для более подробного вывода
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Загружаем переменные окружения
logging.debug("Загружаем переменные окружения...")
load_dotenv()

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
        from src.dashboard.test_data import get_test_pro_data, get_test_history
        
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
            sphere="Карьера",
            pro_data=pro_data,
            history=history
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
        logging.error(f"Ошибка при тестировании: {e}", exc_info=True)

if __name__ == "__main__":
    logging.debug("Запуск скрипта")
    main() 