"""
Основной файл Telegram-бота HPI
"""
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from typing import Optional

from .handlers import setup_handlers

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HPIBot:
    """Основной класс Telegram-бота HPI."""
    
    def __init__(self, token: Optional[str] = None):
        """Инициализация бота."""
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настраивает обработчики команд."""
        setup_handlers(self.application)
    
    def run(self):
        """Запускает бота (синхронно)."""
        logger.info("Запуск HPI Telegram-бота...")
        self.application.run_polling()
        logger.info("Бот успешно завершил работу.")


def main():
    """Основная функция для запуска бота."""
    try:
        bot = HPIBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    main() 