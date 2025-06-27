#!/usr/bin/env python3
"""
Запуск Telegram-бота HPI
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота."""
    try:
        # Проверяем наличие токена
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN не найден в .env файле")
            logger.info("Создайте файл .env и добавьте: TELEGRAM_BOT_TOKEN=ваш_токен")
            return
        
        # Импортируем и запускаем бота
        from src.telegram_bot.bot import HPIBot
        bot = HPIBot(token)
        bot.run()
    except ImportError as e:
        logger.error(f"Ошибка импорта: {e}")
        logger.info("Убедитесь, что установлены все зависимости: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    main() 