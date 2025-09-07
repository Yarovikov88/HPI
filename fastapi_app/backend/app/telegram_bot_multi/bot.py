"""
Основной файл запуска мультиязычного Telegram-бота HPI
"""
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from .handlers import HPIBotHandlers, CHOOSING_ACTION, ANSWERING_QUESTIONS, COLLECTING_PRO

# Используем полноценный SessionManager с UserSession
from src.telegram_bot_multi.states import SessionManager
session_manager = SessionManager()

load_dotenv()

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError('TELEGRAM_BOT_TOKEN не найден в переменных окружения')
    application = Application.builder().token(token).build()
    handlers = HPIBotHandlers(session_manager)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start_command),
            CommandHandler("help", handlers.help_command),
            CommandHandler("menu", handlers.menu_command),
            CommandHandler("language", handlers.language_command),
        ],
        states={
            CHOOSING_ACTION: [
                CallbackQueryHandler(handlers.choose_language_handler, pattern="^lang_(ru|en)$"),
                CallbackQueryHandler(handlers.button_handler),
                MessageHandler(filters.ALL, handlers.fallback_handler),
            ],
            ANSWERING_QUESTIONS: [
                CallbackQueryHandler(handlers._handle_answer, pattern="^answer_\\d+$"),
                CallbackQueryHandler(handlers.button_handler),
                MessageHandler(filters.ALL, handlers.fallback_handler),
            ],
            COLLECTING_PRO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers._handle_pro_answer),
                CallbackQueryHandler(handlers.button_handler),
                MessageHandler(filters.ALL, handlers.fallback_handler),
            ]
        },
        fallbacks=[
            CommandHandler("start", handlers.start_command),
            MessageHandler(filters.ALL, handlers.fallback_handler),
        ],
        allow_reentry=True
    )
    application.add_handler(conv_handler)
    # Дополнительные команды вне ConversationHandler
    application.add_handler(CommandHandler("dashboard", handlers.show_dashboard))
    application.add_handler(CommandHandler("pro_dashboard", handlers.show_pro_dashboard))
    application.add_handler(CommandHandler("recommendations", handlers.show_recommendations))
    application.add_handler(CommandHandler("trend", handlers.show_trend))
    application.add_handler(CommandHandler("radar", handlers.show_radar))
    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main() 