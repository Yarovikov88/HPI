import os
import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.getenv("CHANNEL_BOT_TOKEN", "8371425767:AAHE31OsvZSftj2YNxFa8oaSV7YShvdPk6w")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@hpi_expert_chat")
API_BASE_URL = os.getenv("API_BASE_URL", "https://hpi.expert/api")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

class ChannelBot:
    # Атрибуты класса для доступа к конфигурации
    BOT_TOKEN = BOT_TOKEN
    API_BASE_URL = API_BASE_URL
    CHANNEL_ID = CHANNEL_ID
    
    def __init__(self):
        self.api_base_url = self.API_BASE_URL
        self.processed_utms = set()  # Кэш обработанных UTM-меток
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений в канале"""
        message = update.message
        
        logger.info(f"Получено сообщение в чате: {message.chat.username} (тип: {message.chat.type})")
        
        # Проверяем, что сообщение из нужного канала
        if message.chat.username != "hpi_expert_chat":
            logger.info(f"Сообщение не из нужного канала: {message.chat.username}")
            return
            
        # Проверяем, что это пересланное сообщение
        if not message.forward_from:
            logger.info("Сообщение не переслано")
            return
            
        logger.info(f"Пересланное сообщение от пользователя: {message.forward_from.id}")
            
        try:
            # Получаем текст сообщения
            text = message.text or message.caption or ""
            
            # Ищем UTM-метку в конце сообщения
            utm_match = re.search(r'user_(\d+)_(\d+)$', text)
            
            if not utm_match:
                return
                
            user_id = utm_match.group(1)
            utm_timestamp = utm_match.group(2)
            full_utm = f"user_{user_id}_{utm_timestamp}"
            
            # Проверяем, не обрабатывали ли мы уже эту UTM-метку
            if full_utm in self.processed_utms:
                return
                
            # Добавляем в кэш
            self.processed_utms.add(full_utm)
            
            # Выдаем PRO-статус пользователю
            success = await self.grant_pro_status(user_id)
            
            if success:
                # Логируем успешную выдачу
                logger.info(f"PRO статус выдан пользователю {user_id} через UTM {full_utm}")
                
                # Уведомляем админа (если настроен)
                if ADMIN_CHAT_ID:
                    await self.notify_admin(user_id, full_utm, context)
            else:
                logger.error(f"Не удалось выдать PRO статус пользователю {user_id}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
    
    async def grant_pro_status(self, user_id: str):
        """Выдает PRO-статус пользователю через API"""
        try:
            logger.info(f"Пытаемся выдать PRO статус пользователю {user_id}")
            
            # Здесь должен быть вызов вашего API для выдачи PRO-статуса
            url = f"{self.api_base_url}/profile/{user_id}/grant-pro"
            logger.info(f"Отправляем запрос к: {url}")
            
            response = requests.post(
                url,
                headers={"Authorization": "Bearer admin_token"}  # Нужен админский токен
            )
            
            logger.info(f"Ответ API: статус {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Ошибка API: {response.text}")
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Ошибка при выдаче PRO статуса: {e}")
            return False
    

    
    async def notify_admin(self, user_id: str, utm: str, context: ContextTypes.DEFAULT_TYPE):
        """Уведомляет админа о выдаче PRO-статуса"""
        try:
            admin_text = f"""
✅ PRO статус выдан

👤 Пользователь ID: {user_id}
🏷️ UTM: {utm}
⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            """.strip()
            
            # Отправляем уведомление админу
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_text
            )
            
        except Exception as e:
            logger.error(f"Ошибка при уведомлении админа: {e}")

async def main():
    """Запуск бота"""
    bot = ChannelBot()
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик сообщений
    application.add_handler(
        MessageHandler(
            filters.ChatType.CHANNEL & filters.TEXT,
            bot.handle_message
        )
    )
    
    # Запускаем бота
    logger.info("Channel Bot запущен")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 