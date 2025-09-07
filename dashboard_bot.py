import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения (@myhpibot)
BOT_TOKEN = os.getenv("DASHBOARD_BOT_TOKEN", "8479171638:AAEsGz-TcfxbDkfiJ4a5D4Fr24BUdQmarmM")
API_BASE_URL = os.getenv("API_BASE_URL", "https://hpi.expert/api")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/hpi_expert_chat")

class DashboardBot:
    # Атрибуты класса для доступа к конфигурации
    BOT_TOKEN = BOT_TOKEN
    API_BASE_URL = API_BASE_URL
    CHANNEL_LINK = CHANNEL_LINK
    
    def __init__(self):
        self.api_base_url = self.API_BASE_URL
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Получаем параметр из команды
        start_param = context.args[0] if context.args else None
        
        logger.info(f"Получена команда /start от пользователя {user.id}, параметр: {start_param}")
        
        if not start_param:
            await update.message.reply_text(
                "Привет! Для получения дашборда используйте ссылку с нашего сайта."
            )
            return
        
        # Если параметр начинается с "feedback_", запускаем процесс обратной связи с UTM
        if start_param.startswith("feedback_"):
            utm_param = start_param.replace("feedback_", "")
            logger.info(f"Запускаем процесс обратной связи для пользователя {user.id} с UTM: {utm_param}")
            await self.feedback_with_utm(update, context, utm_param)
            return
            
        try:
            # Получаем данные пользователя и его дашборд по UTM-метке
            logger.info(f"Запрашиваем данные дашборда для UTM: {start_param}")
            dashboard_data = await self.get_user_dashboard(start_param)
            
            if dashboard_data:
                logger.info(f"Данные дашборда получены успешно для UTM: {start_param}")
                # Создаем дашборд
                dashboard_text = self.create_dashboard_text(dashboard_data, start_param)
                
                # Добавляем UTM-метку в конец
                dashboard_text += f"\n\n{start_param}"
                
                # Создаем клавиатуру с кнопкой для пересылки
                keyboard = [
                    [InlineKeyboardButton("📤 Переслать в канал", url=CHANNEL_LINK)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    dashboard_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                logger.error(f"Не удалось получить данные дашборда для UTM: {start_param}")
                await update.message.reply_text(
                    "Не удалось получить данные дашборда. Убедитесь, что вы зарегистрированы на сайте."
                )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке команды start: {e}")
            await update.message.reply_text(
                "Произошла ошибка при получении дашборда. Попробуйте позже."
            )

    async def feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /feedback для отправки улучшений/ошибок"""
        user = update.effective_user
        
        logger.info(f"Получена команда /feedback от пользователя {user.id}")
        logger.info(f"Текущее состояние пользователя: {context.user_data.get('feedback_state', 'none')}")
        
        # Инициализируем состояние для пользователя
        context.user_data['feedback_state'] = 'waiting_text'
        context.user_data['feedback_data'] = {}
        
        logger.info(f"Установлено состояние 'waiting_text' для пользователя {user.id}")
        
        await update.message.reply_text(
            "📝 <b>Отправка обратной связи</b>\n\n"
            "🎁 <b>Бонус:</b> За любую обратную связь вы получите PRO-статус!\n\n"
            "Пожалуйста, напишите ваш отзыв, предложение или сообщение об ошибке:",
            parse_mode='HTML'
        )

    async def handle_feedback_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текста обратной связи"""
        user = update.effective_user
        text = update.message.text
        
        # Проверяем, что пользователь находится в состоянии ожидания текста
        if context.user_data.get('feedback_state') != 'waiting_text':
            return
        
        logger.info(f"Получен текст обратной связи от пользователя {user.id}")
        
        # Сохраняем текст
        context.user_data['feedback_data']['text'] = text
        context.user_data['feedback_state'] = 'waiting_photo'
        
        await update.message.reply_text(
            "✅ <b>Текст получен!</b>\n\n"
            "Теперь отправьте фото/скриншот (или отправьте /skip если фото не нужно):",
            parse_mode='HTML'
        )

    async def handle_feedback_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик фото для обратной связи"""
        user = update.effective_user
        message = update.message
        
        # Проверяем, что пользователь находится в состоянии ожидания фото
        if context.user_data.get('feedback_state') != 'waiting_photo':
            return
        
        logger.info(f"Получено фото для обратной связи от пользователя {user.id}")
        
        # Сохраняем фото
        photo = message.photo[-1]  # Берем самое большое фото
        context.user_data['feedback_data']['photo'] = photo
        context.user_data['feedback_state'] = 'completed'
        
        # Отправляем обратную связь
        if context.user_data.get('utm_param'):
            await self.send_feedback_to_admin_with_utm(user, context.user_data['feedback_data'], context)
        else:
            await self.send_feedback_to_admin(user, context.user_data['feedback_data'], context)
        
        # Очищаем данные пользователя
        context.user_data.clear()

    async def handle_feedback_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /skip для пропуска фото"""
        user = update.effective_user
        
        # Проверяем, что пользователь находится в состоянии ожидания фото
        if context.user_data.get('feedback_state') != 'waiting_photo':
            await update.message.reply_text("❌ Нет активного процесса обратной связи.")
            return
        
        logger.info(f"Пользователь {user.id} пропустил отправку фото")
        
        context.user_data['feedback_state'] = 'completed'
        
        # Отправляем обратную связь без фото
        if context.user_data.get('utm_param'):
            await self.send_feedback_to_admin_with_utm(user, context.user_data['feedback_data'], context)
        else:
            await self.send_feedback_to_admin(user, context.user_data['feedback_data'], context)
        
        # Очищаем данные пользователя
        context.user_data.clear()

    async def send_feedback_to_admin(self, user, feedback_data, context):
        """Отправляет обратную связь админу и выдает PRO-статус"""
        try:
            text = feedback_data.get('text', '')
            photo = feedback_data.get('photo')
            
            # Отправляем в админский чат
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                feedback_message = f"""
📝 <b>Новая обратная связь</b>

👤 <b>Пользователь:</b> {user.first_name} (@{user.username or 'без username'})
🆔 <b>ID:</b> {user.id}
📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

�� <b>Сообщение:</b>
{text}
                """.strip()
                
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=feedback_message,
                    parse_mode='HTML'
                )
                
                # Если есть фото, отправляем его
                if photo:
                    await context.bot.send_photo(
                        chat_id=admin_chat_id,
                        photo=photo.file_id,
                        caption=f"📸 Фото от пользователя {user.first_name} (ID: {user.id})"
                    )
                
                logger.info(f"Обратная связь отправлена в админский чат от пользователя {user.id}")
            
            # Выдаем PRO-статус пользователю
            await self.grant_pro_status(user.id, context)
            
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ <b>Спасибо за обратную связь!</b>\n\n"
                     "🎉 <b>Вам выдан PRO-статус!</b>\n\n"
                     "Ваше сообщение отправлено разработчикам. "
                     "Обновите страницу на сайте, чтобы увидеть PRO-функции.",
                parse_mode='HTML'
            )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке обратной связи: {e}")
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Произошла ошибка при отправке обратной связи. Попробуйте позже."
            )

    async def grant_pro_status(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Выдает PRO-статус пользователю через API"""
        try:
            logger.info(f"Пытаемся выдать PRO статус пользователю {user_id}")
            
            # Вызываем API для выдачи PRO-статуса
            url = f"{self.api_base_url}/profile/{user_id}/grant-pro"
            logger.info(f"Отправляем запрос к: {url}")
            
            response = requests.post(
                url,
                headers={"Authorization": "Bearer admin_token"},  # Нужен админский токен
                timeout=10
            )
            
            logger.info(f"Ответ API: статус {response.status_code}")
            if response.status_code == 200:
                logger.info(f"PRO статус успешно выдан пользователю {user_id}")
                return True
            else:
                logger.error(f"Ошибка API при выдаче PRO: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при выдаче PRO статуса: {e}")
            return False

    async def handle_media_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик медиа-файлов для обратной связи"""
        user = update.effective_user
        message = update.message
        
        logger.info(f"Получен медиа-файл от пользователя {user.id} для обратной связи")
        
        try:
            # Определяем тип медиа
            media_type = None
            media_file = None
            caption = message.caption or "Без описания"
            
            if message.photo:
                media_type = "фото"
                media_file = message.photo[-1]  # Берем самое большое фото
            elif message.video:
                media_type = "видео"
                media_file = message.video
            elif message.document:
                media_type = "документ"
                media_file = message.document
            elif message.animation:
                media_type = "анимация"
                media_file = message.animation
            else:
                await update.message.reply_text(
                    "❌ Неподдерживаемый тип файла. Отправьте фото, видео или документ."
                )
                return
            
            # Отправляем в админский чат
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                # Сначала отправляем информацию о пользователе
                info_message = f"""
📸 <b>Новая обратная связь с медиа</b>

👤 <b>Пользователь:</b> {user.first_name} (@{user.username or 'без username'})
🆔 <b>ID:</b> {user.id}
📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📁 <b>Тип файла:</b> {media_type}

💬 <b>Описание:</b>
{caption}
                """.strip()
                
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=info_message,
                    parse_mode='HTML'
                )
                
                # Затем отправляем сам медиа-файл
                if media_type == "фото":
                    await context.bot.send_photo(
                        chat_id=admin_chat_id,
                        photo=media_file.file_id,
                        caption=f"📸 Файл от пользователя {user.first_name} (ID: {user.id})"
                    )
                elif media_type == "видео":
                    await context.bot.send_video(
                        chat_id=admin_chat_id,
                        video=media_file.file_id,
                        caption=f"🎥 Видео от пользователя {user.first_name} (ID: {user.id})"
                    )
                elif media_type == "документ":
                    await context.bot.send_document(
                        chat_id=admin_chat_id,
                        document=media_file.file_id,
                        caption=f"📄 Документ от пользователя {user.first_name} (ID: {user.id})"
                    )
                elif media_type == "анимация":
                    await context.bot.send_animation(
                        chat_id=admin_chat_id,
                        animation=media_file.file_id,
                        caption=f"🎬 Анимация от пользователя {user.first_name} (ID: {user.id})"
                    )
                
                logger.info(f"Медиа-файл отправлен в админский чат от пользователя {user.id}")
            else:
                # Если админский чат не настроен, сохраняем в лог
                logger.info(f"Медиа-файл от пользователя {user.id}: {media_type} - {caption}")
            
            # Выдаем PRO-статус пользователю
            await self.grant_pro_status(user.id, context)
            
            await update.message.reply_text(
                "✅ <b>Спасибо за обратную связь!</b>\n\n"
                f"🎉 <b>Вам выдан PRO-статус!</b>\n\n"
                f"Ваш {media_type} отправлен разработчикам вместе с описанием. "
                "Обновите страницу на сайте, чтобы увидеть PRO-функции.",
                parse_mode='HTML'
            )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке медиа-файла: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при отправке файла. Попробуйте позже."
            )
    
    async def get_user_dashboard(self, utm_param: str):
        """Получает данные дашборда пользователя по UTM-метке"""
        try:
            logger.info(f"Начинаем получение данных для UTM: {utm_param}")
            logger.info(f"API URL: {self.api_base_url}")
            
            # Запрос к API для получения данных по UTM-метке
            utm_url = f"{self.api_base_url}/dashboard/utm/{utm_param}"
            logger.info(f"Запрашиваем данные по UTM: {utm_url}")
            
            response = requests.get(utm_url, timeout=10)
            
            logger.info(f"Ответ API: статус {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Ошибка API: {response.text}")
                return None
                
            data = response.json()
            logger.info(f"Данные получены успешно для UTM: {utm_param}")
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных дашборда: {e}")
            return None
    

    
    def create_dashboard_text(self, data: dict, utm_param: str):
        """Создает текст дашборда"""
        # Данные приходят напрямую от API в формате:
        # {"user_id": 179, "user_info": {...}, "hpi": 20.0, "sphere_scores": {...}, "answers": [...]}
        
        user_info = data.get("user_info", {})
        hpi_value = data.get("hpi", "N/A")
        sphere_scores = data.get("sphere_scores", {})
        answers = data.get("answers", [])
        
        # Итоговый HPI (уже получен выше)
        
        # Динамика (тренд) - пока упростим
        trend_text = "📈 Динамика: 📊 Нет данных"
        
        # Баланс по сферам
        balance_text = "🎯 Баланс по сферам:\n"
        if sphere_scores:
            sphere_names = [
                "Отношения с любимыми", "Отношения с родными", "Друзья",
                "Карьера", "Физическое здоровье", "Ментальное здоровье",
                "Хобби и увлечения", "Благосостояние"
            ]
            
            for i, name in enumerate(sphere_names, 1):
                value = sphere_scores.get(str(i), 0)
                balance_text += f"• {name}: {value}/10\n"
        else:
            balance_text += "📊 Данные не доступны"
        
        # Подпись
        user_name = user_info.get("username", user_info.get("first_name", "Пользователь"))
        
        # Формируем итоговый текст
        dashboard_text = f"""
📊 <b>Дашборд HPI.EXPERT</b>

🎯 <b>Итоговый HPI:</b> {hpi_value}

{trend_text}

{balance_text}

—
👤 {user_name}
📅 {datetime.now().strftime('%d.%m.%Y')}
        """.strip()
        
        return dashboard_text

    async def feedback_with_utm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, utm_param: str):
        """Обработчик команды /feedback с UTM для отправки улучшений/ошибок"""
        user = update.effective_user
        
        logger.info(f"Получена команда /feedback с UTM от пользователя {user.id}, UTM: {utm_param}")
        logger.info(f"Текущее состояние пользователя: {context.user_data.get('feedback_state', 'none')}")
        
        # Инициализируем состояние для пользователя с UTM
        context.user_data['feedback_state'] = 'waiting_text'
        context.user_data['feedback_data'] = {}
        context.user_data['utm_param'] = utm_param  # Сохраняем UTM
        
        logger.info(f"Установлено состояние 'waiting_text' для пользователя {user.id} с UTM: {utm_param}")
        
        await update.message.reply_text(
            "📝 <b>Отправка обратной связи</b>\n\n"
            "🎁 <b>Бонус:</b> За любую обратную связь вы получите PRO-статус!\n\n"
            "Пожалуйста, напишите ваш отзыв, предложение или сообщение об ошибке:",
            parse_mode='HTML'
        )

    async def send_feedback_to_admin_with_utm(self, user, feedback_data, context):
        """Отправляет обратную связь админу и выдает PRO-статус по UTM"""
        try:
            text = feedback_data.get('text', '')
            photo = feedback_data.get('photo')
            utm_param = context.user_data.get('utm_param', '')
            
            # Отправляем в админский чат
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                feedback_message = f"""
📝 <b>Новая обратная связь</b>

👤 <b>Пользователь:</b> {user.first_name} (@{user.username or 'без username'})
🆔 <b>Telegram ID:</b> {user.id}
📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🔗 <b>UTM:</b> {utm_param}

💬 <b>Сообщение:</b>
{text}
                """.strip()
                
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=feedback_message,
                    parse_mode='HTML'
                )
                
                # Если есть фото, отправляем его
                if photo:
                    await context.bot.send_photo(
                        chat_id=admin_chat_id,
                        photo=photo.file_id,
                        caption=f"📸 Фото от пользователя {user.first_name} (Telegram ID: {user.id}, UTM: {utm_param})"
                    )
                
                logger.info(f"Обратная связь отправлена в админский чат от пользователя {user.id} с UTM: {utm_param}")
            
            # Выдаем PRO-статус пользователю по UTM
            await self.grant_pro_status_by_utm(utm_param, context)
            
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ <b>Спасибо за обратную связь!</b>\n\n"
                     "🎉 <b>Вам выдан PRO-статус!</b>\n\n"
                     "Ваше сообщение отправлено разработчикам. "
                     "Обновите страницу на сайте, чтобы увидеть PRO-функции.",
                parse_mode='HTML'
            )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке обратной связи: {e}")
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Произошла ошибка при отправке обратной связи. Попробуйте позже."
            )

    async def grant_pro_status_by_utm(self, utm_param: str, context: ContextTypes.DEFAULT_TYPE):
        """Выдает PRO-статус пользователю по UTM-метке"""
        try:
            logger.info(f"Пытаемся выдать PRO статус по UTM: {utm_param}")
            
            # Получаем данные пользователя по UTM
            dashboard_data = await self.get_user_dashboard(utm_param)
            if not dashboard_data:
                logger.error(f"Не удалось получить данные пользователя по UTM: {utm_param}")
                return False
            
            user_id = dashboard_data.get("user_id")
            if not user_id:
                logger.error(f"Не найден user_id в данных по UTM: {utm_param}")
                return False
            
            logger.info(f"Найден user_id: {user_id} для UTM: {utm_param}")
            
            # Вызываем API для выдачи PRO-статуса
            url = f"{self.api_base_url}/profile/{user_id}/grant-pro"
            logger.info(f"Отправляем запрос к: {url}")
            
            response = requests.post(
                url,
                headers={"Authorization": "Bearer admin_token"},  # Нужен админский токен
                timeout=10
            )
            
            logger.info(f"Ответ API: статус {response.status_code}")
            if response.status_code == 200:
                logger.info(f"PRO статус успешно выдан пользователю {user_id} по UTM: {utm_param}")
                return True
            else:
                logger.error(f"Ошибка API при выдаче PRO: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при выдаче PRO статуса по UTM: {e}")
            return False

    async def send_feedback_from_website(self, feedback_data: dict):
        """Отправляет обратную связь с сайта в админский чат"""
        try:
            # Получаем данные из feedback_data
            feedback_type = feedback_data.get('type', 'unknown')
            message = feedback_data.get('message', '')
            user_id = feedback_data.get('user_id', '')
            user_email = feedback_data.get('user_email', '')
            user_agent = feedback_data.get('userAgent', '')
            url = feedback_data.get('url', '')
            
            # Отправляем в админский чат (ваш Telegram ID)
            admin_chat_id = "1014395380"  # Ваш Telegram ID
            
            feedback_message = f"""
📝 <b>Новая обратная связь с сайта</b>

👤 <b>Пользователь:</b> {user_email or 'Неизвестный'}
🆔 <b>User ID:</b> {user_id}
📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
🌐 <b>Страница:</b> {url}
🔧 <b>Тип:</b> {'🐛 Ошибка' if feedback_type == 'bug' else '💡 Предложение'}

💬 <b>Сообщение:</b>
{message}

📱 <b>User Agent:</b>
{user_agent}
            """.strip()
            
            # Создаем временный бот для отправки (нужно будет настроить)
            # Пока что просто логируем
            logger.info(f"Обратная связь с сайта: {feedback_message}")
            
            # TODO: Настроить отправку в Telegram
            # Для этого нужно создать экземпляр бота или использовать webhook
            
            return True
                
        except Exception as e:
            logger.error(f"Ошибка при отправке обратной связи с сайта: {e}")
            return False

async def main():
    """Запуск бота"""
    bot = DashboardBot()
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("feedback", bot.feedback))
    application.add_handler(CommandHandler("skip", bot.handle_feedback_skip))
    
    # Добавляем обработчики для интерактивной обратной связи
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_feedback_text))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_feedback_photo))
    
    # Запускаем бота
    logger.info("Dashboard Bot запущен")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 