#!/usr/bin/env python3
"""
Скрипт для одновременного запуска Dashboard Bot и Channel Bot
"""

import asyncio
import logging
import signal
import sys
from dashboard_bot import DashboardBot, main as dashboard_main
from channel_bot import ChannelBot, main as channel_main

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Флаг для graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Получен сигнал {signum}, начинаю graceful shutdown...")
    shutdown_event.set()

async def run_dashboard_bot():
    """Запуск Dashboard Bot"""
    try:
        logger.info("Запускаю Dashboard Bot...")
        bot = DashboardBot()
        
        # Создаем приложение
        from telegram.ext import Application, CommandHandler
        application = Application.builder().token(DashboardBot.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("feedback", bot.feedback))
        application.add_handler(CommandHandler("skip", bot.handle_feedback_skip))
        
        # Добавляем обработчики для интерактивной обратной связи
        from telegram.ext import MessageHandler, filters
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_feedback_text))
        application.add_handler(MessageHandler(filters.PHOTO, bot.handle_feedback_photo))
        
        # Запускаем бота
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("Dashboard Bot запущен успешно")
        
        # Ждем сигнала завершения
        await shutdown_event.wait()
        
        # Останавливаем бота
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        
        logger.info("Dashboard Bot остановлен")
        
    except Exception as e:
        logger.error(f"Ошибка в Dashboard Bot: {e}")
        raise

async def run_channel_bot():
    """Запуск Channel Bot"""
    try:
        logger.info("Запускаю Channel Bot...")
        bot = ChannelBot()
        
        # Создаем приложение
        from telegram.ext import Application, MessageHandler, filters
        application = Application.builder().token(ChannelBot.BOT_TOKEN).build()
        
        # Добавляем обработчик сообщений (убираем ограничение по типу чата)
        application.add_handler(
            MessageHandler(
                filters.TEXT,
                bot.handle_message
            )
        )
        
        # Запускаем бота
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("Channel Bot запущен успешно")
        
        # Ждем сигнала завершения
        await shutdown_event.wait()
        
        # Останавливаем бота
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        
        logger.info("Channel Bot остановлен")
        
    except Exception as e:
        logger.error(f"Ошибка в Channel Bot: {e}")
        raise

async def main():
    """Главная функция - запуск обоих ботов"""
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Запускаю оба бота одновременно...")
    
    try:
        # Запускаем оба бота одновременно
        await asyncio.gather(
            run_dashboard_bot(),
            run_channel_bot(),
            return_exceptions=True
        )
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    
    logger.info("Все боты остановлены")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаю работу...")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1) 