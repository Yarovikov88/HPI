"""
Обработчики команд для Telegram-бота HPI
"""
import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode

from .states import UserState, SessionManager
from .questions import QuestionsManager
from .calculator import HPICalculator
from .visualizer import HPIVisualizer


# Состояния для ConversationHandler
CHOOSING_ACTION, ANSWERING_QUESTIONS, COLLECTING_PRO = range(3)

logger = logging.getLogger(__name__)


class HPIBotHandlers:
    """Обработчики команд для бота HPI."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.questions_manager = QuestionsManager()
        self.calculator = HPICalculator()
        self.visualizer = HPIVisualizer()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик команды /start."""
        user_id = update.effective_user.id if update.effective_user else None
        if user_id is None:
            return CHOOSING_ACTION
        session = self.session_manager.get_session(user_id)
        session.reset()
        if update.message and hasattr(update.message, 'date'):
            session.last_activity = update.message.date
        
        welcome_text = (
            "🎯 <b>Добро пожаловать в HPI Bot!</b>\n\n"
            "Я помогу вам проанализировать ваши сферы жизни и получить персональные рекомендации.\n\n"
            "📊 <b>Что мы будем оценивать:</b>\n"
            "💖 Отношения с любимыми\n"
            "🏡 Отношения с родными\n"
            "🤝 Друзья\n"
            "💼 Карьера\n"
            "♂️ Физическое здоровье\n"
            "🧠 Ментальное здоровье\n"
            "🎨 Хобби и увлечения\n"
            "💰 Благосостояние\n\n"
            "Готовы начать анализ?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Начать опрос", callback_data="start_survey")],
            [InlineKeyboardButton("ℹ️ Как это работает", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            logger.warning("update.message отсутствует, невозможно отправить приветствие пользователю.")
        
        return CHOOSING_ACTION
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик команды /help."""
        help_text = (
            "📚 <b>Как работает HPI Bot:</b>\n\n"
            "1️⃣ <b>Опрос</b> - ответите на 48 вопросов (6 по каждой сфере)\n"
            "2️⃣ <b>Расчет</b> - система рассчитает ваш Human Performance Index\n"
            "3️⃣ <b>Анализ</b> - получите диаграммы и рекомендации\n\n"
            "⏱️ <b>Время прохождения:</b> 10-15 минут\n"
            "💾 <b>Данные:</b> сохраняются локально для анализа трендов\n\n"
            "🎯 <b>Цель:</b> помочь вам увидеть баланс жизни и найти области для улучшения"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Начать опрос", callback_data="start_survey")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                help_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            logger.warning("update.message отсутствует, невозможно отправить help_text пользователю.")
        
        return CHOOSING_ACTION
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик нажатий на кнопки."""
        query = update.callback_query
        if not query or not query.from_user:
            return CHOOSING_ACTION
        await query.answer()
        user_id = query.from_user.id
        session = self.session_manager.get_session(user_id)
        if query.message and hasattr(query.message, 'date'):
            session.last_activity = query.message.date
        
        data = query.data
        if not data:
            return CHOOSING_ACTION
        if data == "start_survey":
            return await self._start_survey(query, session)
        elif data == "help":
            return await self._show_help(query)
        elif data == "back_to_start":
            return await self._back_to_start(query)
        elif data.startswith("answer_"):
            return await self._handle_answer(query, session)
        elif data == "skip_pro":
            return await self._finish_survey(query, session)
        elif data == "restart":
            return await self._restart_survey(query, session)
        
        return CHOOSING_ACTION
    
    async def _start_survey(self, query, session) -> int:
        """Начинает опрос."""
        session.state = UserState.ANSWERING_QUESTIONS
        session.current_sphere = 1
        session.current_question = 0
        session.survey_start_time = query.message.date
        
        sphere = self.questions_manager.get_sphere(1)
        if not sphere:
            await query.edit_message_text("Ошибка загрузки вопросов. Попробуйте позже.")
            return CHOOSING_ACTION
            
        question = sphere.questions[0]
        
        question_text = self.questions_manager.format_question_for_telegram(sphere, question)
        progress_text = f"📊 <b>Прогресс:</b> 1/48 вопросов"
        
        keyboard = self._create_answer_keyboard(question)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{question_text}\n\n{progress_text}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return ANSWERING_QUESTIONS
    
    async def _show_help(self, query) -> int:
        """Показывает справку."""
        help_text = (
            "📚 <b>Как работает HPI Bot:</b>\n\n"
            "1️⃣ <b>Опрос</b> - ответите на 48 вопросов (6 по каждой сфере)\n"
            "2️⃣ <b>Расчет</b> - система рассчитает ваш Human Performance Index\n"
            "3️⃣ <b>Анализ</b> - получите диаграммы и рекомендации\n\n"
            "⏱️ <b>Время прохождения:</b> 10-15 минут\n"
            "💾 <b>Данные:</b> сохраняются локально для анализа трендов\n\n"
            "🎯 <b>Цель:</b> помочь вам увидеть баланс жизни и найти области для улучшения"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Начать опрос", callback_data="start_survey")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return CHOOSING_ACTION
    
    async def _back_to_start(self, query) -> int:
        """Возвращает к началу."""
        welcome_text = (
            "🎯 <b>Добро пожаловать в HPI Bot!</b>\n\n"
            "Я помогу вам проанализировать ваши сферы жизни и получить персональные рекомендации.\n\n"
            "📊 <b>Что мы будем оценивать:</b>\n"
            "💖 Отношения с любимыми\n"
            "🏡 Отношения с родными\n"
            "🤝 Друзья\n"
            "💼 Карьера\n"
            "♂️ Физическое здоровье\n"
            "🧠 Ментальное здоровье\n"
            "🎨 Хобби и увлечения\n"
            "💰 Благосостояние\n\n"
            "Готовы начать анализ?"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Начать опрос", callback_data="start_survey")],
            [InlineKeyboardButton("ℹ️ Как это работает", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return CHOOSING_ACTION
    
    async def _handle_answer(self, query, session) -> int:
        """Обрабатывает ответ пользователя."""
        # Извлекаем ответ
        answer_data = query.data.split("_")
        answer = int(answer_data[1])
        
        # Сохраняем ответ
        sphere_key = str(session.current_sphere)
        if sphere_key not in session.answers:
            session.answers[sphere_key] = []
        session.answers[sphere_key].append(answer)
        
        # Переходим к следующему вопросу
        session.current_question += 1
        sphere = self.questions_manager.get_sphere(session.current_sphere)
        
        if not sphere:
            await query.edit_message_text("Ошибка загрузки вопросов. Попробуйте позже.")
            return CHOOSING_ACTION
        
        # Если вопросы в сфере закончились, переходим к следующей сфере
        if session.current_question >= len(sphere.questions):
            session.current_sphere += 1
            session.current_question = 0
            
            # Если все сферы пройдены, завершаем опрос
            if session.current_sphere > 8:
                return await self._finish_survey(query, session)
        
        # Показываем следующий вопрос
        sphere = self.questions_manager.get_sphere(session.current_sphere)
        if not sphere:
            await query.edit_message_text("Ошибка загрузки вопросов. Попробуйте позже.")
            return CHOOSING_ACTION
            
        question = sphere.questions[session.current_question]
        
        question_text = self.questions_manager.format_question_for_telegram(sphere, question)
        
        # Рассчитываем прогресс
        total_answered = sum(len(answers) for answers in session.answers.values())
        progress_text = f"📊 <b>Прогресс:</b> {total_answered}/48 вопросов"
        
        keyboard = self._create_answer_keyboard(question)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{question_text}\n\n{progress_text}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return ANSWERING_QUESTIONS
    
    async def _finish_survey(self, query, session) -> int:
        """Завершает опрос и показывает результаты."""
        # ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ПРОВЕРКИ ТАБЛИЦ
        session.problems = [
            {"emoji": "❤️", "text": "Недостаток качественного времени вдвоём."},
            {"emoji": "🏡", "text": "Редко видимся с родителями из-за расстояния."}
        ]
        session.goals = [
            {"emoji": "❤️", "text": "Проводить один вечер в неделю только вдвоём, без гаджетов."},
            {"emoji": "🏡", "text": "Звонить родителям минимум два раза в неделю."}
        ]
        session.blockers = [
            {"emoji": "❤️", "text": "Усталость после работы."},
            {"emoji": "🏡", "text": "Разница в часовых поясах."}
        ]
        session.metrics = [
            {"emoji": "❤️", "name": "Часы вместе", "value": 5, "goal": 8, "delta": "-3"},
            {"emoji": "🏡", "name": "Встречи в месяц", "value": 1, "goal": 2, "delta": "-1"}
        ]
        session.recommendations = [
            {"emoji": "❤️", "text": "Quality Time Together"},
            {"emoji": "🏡", "text": "Увеличение общения с родителями"}
        ]
        session.ai_recommendations = [
            {"emoji": "❤️", "title": "Quality Time Together", "desc": "Проводить время без гаджетов", "steps": "1. Запланировать вечер без гаджетов"}
        ]

        # Рассчитываем HPI
        scores = self.calculator.calculate_scores(session.answers)
        hpi_total = self.calculator.calculate_total_hpi(scores)

        # Получаем предыдущие результаты пользователя (пример: session.prev_scores)
        prev_scores = getattr(session, 'prev_scores', None)

        # Создаем визуализации
        if prev_scores:
            radar_image = self.visualizer.create_radar_chart_compare(prev_scores, scores)
        else:
            radar_image = self.visualizer.create_radar_chart(scores)
        trend_image = self.visualizer.create_trend_chart(scores, hpi_total)

        # Формируем результаты по новой структуре
        results_text = self._format_hpi_block(scores, hpi_total)
        pro_text = self._format_hpi_pro_block(session)
        ai_text = self._format_ai_block(session)
        full_text = f"{results_text}\n---\n{pro_text}\n---\n{ai_text}"

        # Отправляем результаты
        await query.edit_message_text(
            full_text,
            parse_mode=ParseMode.HTML
        )

        # Отправляем диаграммы
        if radar_image:
            await query.message.reply_photo(
                photo=radar_image,
                caption="📊 <b>Баланс по сферам жизни (сравнение прошлого и текущего)</b>",
                parse_mode=ParseMode.HTML
            )

        if trend_image:
            await query.message.reply_photo(
                photo=trend_image,
                caption="📈 <b>Динамика HPI</b>",
                parse_mode=ParseMode.HTML
            )

        # Предлагаем начать заново
        keyboard = [
            [InlineKeyboardButton("🔄 Пройти опрос заново", callback_data="restart")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "Хотите пройти опрос заново или сохранить результаты?",
            reply_markup=reply_markup
        )

        return CHOOSING_ACTION

    def _format_hpi_block(self, scores: Dict[str, float], hpi_total: float) -> str:
        """Формирует блок HPI: заголовок, текущий HPI, динамика, баланс сфер."""
        # Здесь можно добавить вычисление динамики и форматирование
        return (
            "<b>HPI</b>\n"
            f"Текущий HPI: <b>{hpi_total:.1f}</b>\n"
            f"Динамика: ...\n"
            f"Баланс сфер: см. радар ниже"
        )

    def format_problems(self, problems):
        if not problems:
            return "<b>Мои проблемы:</b> —"
        rows = ["Сфера | Проблема"]
        for p in problems:
            rows.append(f"{p['emoji']} | {p['text']}")
        return "<b>Мои проблемы:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def format_goals(self, goals):
        if not goals:
            return "<b>Мои цели:</b> —"
        rows = ["Сфера | Цель"]
        for g in goals:
            rows.append(f"{g['emoji']} | {g['text']}")
        return "<b>Мои цели:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def format_blockers(self, blockers):
        if not blockers:
            return "<b>Мои блокеры:</b> —"
        rows = ["Сфера | Блокер"]
        for b in blockers:
            rows.append(f"{b['emoji']} | {b['text']}")
        return "<b>Мои блокеры:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def format_metrics(self, metrics):
        if not metrics:
            return "<b>Мои метрики:</b> —"
        rows = ["Сфера | Метрика | Значение | Цель | Изм."]
        for m in metrics:
            rows.append(f"{m['emoji']} | {m['name']} | {m['value']} | {m['goal']} | {m['delta']}")
        return "<b>Мои метрики:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def format_recommendations(self, recs):
        if not recs:
            return "<b>Мои базовые рекомендации:</b> —"
        rows = ["Сфера | Рекомендация"]
        for r in recs:
            rows.append(f"{r['emoji']} | {r['text']}")
        return "<b>Мои базовые рекомендации:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def format_ai_recommendations(self, ai):
        if not ai:
            return "<b>AI рекомендации:</b> —"
        rows = ["Сфера | AI-рекомендация | Описание | Шаги"]
        for a in ai:
            rows.append(f"{a['emoji']} | {a['title']} | {a['desc']} | {a['steps']}")
        return "<b>AI рекомендации:</b>\n<pre>" + "\n".join(rows) + "</pre>"

    def _format_hpi_pro_block(self, session) -> str:
        return (
            "<b>HPI pro</b>\n"
            + self.format_problems(getattr(session, 'problems', [])) + "\n"
            + self.format_goals(getattr(session, 'goals', [])) + "\n"
            + self.format_blockers(getattr(session, 'blockers', [])) + "\n"
            + self.format_metrics(getattr(session, 'metrics', [])) + "\n"
            + self.format_recommendations(getattr(session, 'recommendations', []))
        )

    def _format_ai_block(self, session) -> str:
        return self.format_ai_recommendations(getattr(session, 'ai_recommendations', []))
    
    async def _restart_survey(self, query, session) -> int:
        """Перезапускает опрос."""
        session.reset()
        return await self._start_survey(query, session)
    
    def _create_answer_keyboard(self, question) -> list:
        """Создает клавиатуру с вариантами ответов."""
        keyboard = []
        for i, option in enumerate(question.options, 1):
            keyboard.append([InlineKeyboardButton(f"{i}. {option}", callback_data=f"answer_{i}")])
        return keyboard


def setup_handlers(application):
    """Настраивает обработчики для приложения."""
    handlers = HPIBotHandlers()
    
    # Создаем ConversationHandler для основного диалога
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start_command),
            CommandHandler("help", handlers.help_command)
        ],
        states={
            CHOOSING_ACTION: [
                CallbackQueryHandler(handlers.button_handler)
            ],
            ANSWERING_QUESTIONS: [
                CallbackQueryHandler(handlers.button_handler)
            ],
            COLLECTING_PRO: [
                CallbackQueryHandler(handlers.button_handler)
            ]
        },
        fallbacks=[
            CommandHandler("start", handlers.start_command)
        ]
    )
    
    application.add_handler(conv_handler) 