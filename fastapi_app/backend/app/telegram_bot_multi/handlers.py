# ВОССТАНОВЛЕННЫЙ ФАЙЛ: src/telegram_bot_multi/handlers.py
# Последняя актуальная версия с поддержкой устойчивой генерации рекомендаций через GPT, fallback, логированием и мультиязычностью

import os
import json
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from src.telegram_bot_multi.localization import LOCALES
from src.calculator import HPICalculator

CHOOSING_ACTION = 0
ANSWERING_QUESTIONS = 1
COLLECTING_PRO = 2

class HPIBotHandlers:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = getattr(update, 'callback_query', None)
        if not query or not hasattr(query, 'from_user') or not hasattr(query, 'data'):
            return CHOOSING_ACTION
        telegram_id = query.from_user.id
        session = await self.session_manager.get_session(telegram_id)
        lang = getattr(session, 'language', 'ru')
        lang = lang or 'ru'
        texts = LOCALES[lang]

        # --- Меню дашборда и основные разделы ---
        if query.data == "show_dashboard":
            return await self.show_dashboard(update, context)
        if query.data == "show_answers":
            return await self.show_answers(update, context)
        if query.data == "show_trend":
            return await self.show_trend(update, context)
        if query.data == "show_radar":
            return await self.show_radar(update, context)
        if query.data == "show_problems":
            return await self.show_problems(update, context)
        if query.data == "show_goals":
            return await self.show_goals(update, context)
        if query.data == "show_blockers":
            return await self.show_blockers(update, context)
        if query.data == "show_metrics":
            return await self.show_metrics(update, context)
        if query.data == "show_basic_recs":
            return await self.show_basic_recs(update, context)
        if query.data == "show_ai_recs":
            return await self.show_ai_recs(update, context)
        if query.data == "show_achievements":
            return await self.show_achievements(update, context)
        if query.data == "hide_dashboard":
            return await self.hide_dashboard(update, context)
        
        # --- Смена языка ---
        if query.data == "change_language":
            return await self.language_command(update, context)
        if query.data.startswith("lang_"):
            return await self.choose_language_handler(update, context)
        
        # --- Опрос и PRO-часть ---
        if query.data == "start_survey":
            return await self.start_survey(update, context)
        if query.data == "start_pro":
            return await self.start_pro_survey(update, context)
        if query.data == "start_pro_survey":
            return await self.start_pro_survey(update, context)
        if query.data == "finish_without_pro":
            return await self._finish_without_pro(query, session)
        if query.data == "pro_help":
            return await self._show_pro_help(query, context)
        if query.data == "back_to_menu":
            return await self._back_to_menu(query, context)
        if query.data == "pro_collapse":
            session = await self.session_manager.get_session(query.from_user.id)
            return await self._show_pro_question(query, session, context)
        
        # --- Остальное ---
        # ...
        # Далее — существующая логика (опрос, рекомендации и т.д.)
        # ...
        return CHOOSING_ACTION

    async def start_command(self, update, context):
        user = update.effective_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        session.language = lang
        
        # Проверяем, есть ли UTM-параметр в команде
        if context.args and len(context.args) > 0:
            utm_param = context.args[0]
            if utm_param.startswith('user_'):
                # Пытаемся получить дашборд по UTM
                try:
                    dashboard_data = await self.get_user_dashboard_by_utm(utm_param)
                    if dashboard_data:
                        await self.send_dashboard_by_utm(update, context, dashboard_data, texts)
                        return CHOOSING_ACTION
                except Exception as e:
                    print(f"Error getting dashboard by UTM: {e}")
                    # Если не удалось получить дашборд, продолжаем как обычно
        
        # Обычное приветствие
        await context.bot.send_message(
            chat_id=user.id,
            text=texts['welcome'],
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(texts['start_survey'], callback_data='start_survey')],
                [InlineKeyboardButton(texts['change_language'], callback_data='change_language')],
            ])
        )
        return CHOOSING_ACTION

    async def help_command(self, update, context):
        user = update.effective_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        await context.bot.send_message(
            chat_id=user.id,
            text=texts['help'],
            parse_mode=ParseMode.HTML
        )
        return CHOOSING_ACTION

    async def menu_command(self, update, context):
        user = update.effective_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        await context.bot.send_message(
            chat_id=user.id,
            text=texts['menu'],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(texts['menu_full'], callback_data='start_survey')],
                [InlineKeyboardButton(texts['menu_pro'], callback_data='start_pro')],
                [InlineKeyboardButton(texts['menu_dashboard'], callback_data='show_dashboard')],
                [InlineKeyboardButton(texts['menu_answers'], callback_data='show_answers')],
                [InlineKeyboardButton(texts['change_language'], callback_data='change_language')],
            ])
        )
        return CHOOSING_ACTION

    async def language_command(self, update, context):
        # Обрабатываем как callback query, так и обычную команду
        if hasattr(update, 'callback_query') and update.callback_query:
            query = update.callback_query
            user = query.from_user
            await query.answer()
        else:
            user = update.effective_user
            
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        # Создаем клавиатуру с кнопками выбора языка
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru'), 
             InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')]
        ])
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await query.edit_message_text(
                text=texts['choose_language'],
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=user.id,
                text=texts['choose_language'],
                reply_markup=keyboard
            )
        return CHOOSING_ACTION

    async def choose_language_handler(self, update, context):
        query = update.callback_query
        user = query.from_user
        data = query.data
        session = await self.session_manager.get_session(user.id)
        
        # Меняем язык
        if data == 'lang_ru':
            session.language = 'ru'
        elif data == 'lang_en':
            session.language = 'en'
        
        lang = session.language
        texts = LOCALES[lang]
        
        # Очищаем кэш рекомендаций при смене языка
        session.recommendations_lang = None
        session.ai_recommendations_lang = None
        
        await query.answer()
        
        # Показываем главное меню на новом языке
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(texts['start_survey'], callback_data='start_survey')],
            [InlineKeyboardButton(texts['change_language'], callback_data='change_language')],
        ])
        
        await query.edit_message_text(
            text=texts['welcome'], 
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        return CHOOSING_ACTION

    async def start_survey(self, update, context):
        """Начинает полный опрос"""
        query = update.callback_query
        user = query.from_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        # Инициализируем сессию для опроса
        session.current_question = 0
        session.current_sphere = 1
        session.answers = {}
        session.survey_start_time = query.message.date
        
        await query.answer()
        
        # Получаем первую сферу и вопрос
        from src.telegram_bot_multi.questions import QuestionsManager
        qm = QuestionsManager(lang)
        sphere = qm.get_sphere(1)
        if not sphere:
            await query.edit_message_text("Ошибка загрузки вопросов. Попробуйте позже.")
            return CHOOSING_ACTION
            
        question = sphere.questions[0]
        
        # Формируем текст вопроса
        question_text = f"<b>{sphere.name}</b>\n\n{question['text']}"
        progress_text = f"📊 <b>Прогресс:</b> 1/48 вопросов"
        
        # Создаем клавиатуру с вариантами ответов
        keyboard = []
        for i, option in enumerate(question['options']):
            keyboard.append([InlineKeyboardButton(
                option, 
                callback_data=f"answer_{i}"
            )])
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton(
            texts.get('back', 'Назад'), 
            callback_data='back_to_menu'
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{question_text}\n\n{progress_text}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return ANSWERING_QUESTIONS
    
    async def start_pro_survey(self, update, context):
        """Начинает PRO-опрос"""
        query = update.callback_query
        user = query.from_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        # Инициализируем сессию для PRO-опроса
        session.current_category_index = 0
        session.current_sphere = 1
        session.current_pro_question = 0
        session.pro_data = {}
        session.pro_categories_order = [
            "problems", "goals", "blockers", "metrics", "achievements"
        ]
        session._pro_questions_cache = {}
        session.user_id = user.id  # Добавляем user_id для отправки сообщений
        
        await query.answer()
        
        # Начинаем с первого PRO-вопроса
        return await self._show_pro_question(query, session, context)
    
    async def ask_question(self, update, context):
        """Задает вопрос пользователю"""
        user = update.effective_user
        session = await self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        from src.telegram_bot_multi.questions import QuestionsManager
        qm = QuestionsManager(lang)
        
        # Получаем текущую сферу
        sphere = qm.get_sphere(session.current_sphere)
        if not sphere:
            # Опрос завершен
            await context.bot.send_message(
                chat_id=user.id,
                text=texts['survey_complete'],
                parse_mode=ParseMode.HTML
            )
            return CHOOSING_ACTION
        
        # Получаем текущий вопрос
        questions = sphere.questions
        if session.current_question > len(questions):
            # Переходим к следующей сфере
            session.current_sphere += 1
            session.current_question = 1
            return await self.ask_question(update, context)
        
        question = questions[session.current_question - 1]
        
        # Создаем кнопки с вариантами ответов
        keyboard = []
        for i, option in enumerate(question['options']):
            keyboard.append([InlineKeyboardButton(
                option, 
                callback_data=f"answer_{session.current_sphere}_{session.current_question}_{i}"
            )])
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton(
            texts.get('back', 'Назад'), 
            callback_data='back_to_menu'
        )])
        
        await context.bot.send_message(
            chat_id=user.id,
            text=f"<b>{sphere.name}</b>\n\n{question['text']}",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return ANSWERING_QUESTIONS
    
    async def _ask_pro_survey(self, query, session):
        """Спрашивает пользователя, хочет ли он пройти pro-часть опроса."""
        lang = getattr(session, 'language', 'ru') or 'ru'
        texts = LOCALES[lang]
        
        pro_text = (
            "🎉 <b>Отлично! Вы завершили базовый опрос.</b>\n\n"
            "Теперь у вас есть возможность пройти <b>расширенную часть</b> опроса, "
            "где вы сможете детально описать:\n\n"
            "🔴 <b>Ваши проблемы</b> в каждой сфере\n"
            "🎯 <b>Ваши цели</b> и планы\n"
            "⛔ <b>Блокеры</b>, которые мешают развитию\n"
            "📊 <b>Метрики</b> для отслеживания прогресса\n\n"
            "Это поможет получить более персонализированные рекомендации.\n\n"
            "Хотите пройти расширенную часть?"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ Да, пройти pro-часть", callback_data="start_pro_survey")],
            [InlineKeyboardButton("❌ Нет, показать результаты", callback_data="finish_without_pro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            pro_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return CHOOSING_ACTION

    async def _show_pro_question(self, query, session, context=None):
        """Показывает PRO-вопрос пользователю"""
        try:
            print(f"[PRO] show_pro_question: category_idx={session.current_category_index}, sphere={session.current_sphere}, pro_q={session.current_pro_question}")
            
            # Проверяем завершение всех категорий
            if session.current_category_index >= len(session.pro_categories_order):
                print("[PRO] Все категории пройдены, завершаем PRO-опрос")
                if query:
                    return await self._finish_pro_survey(query, session, context)
                else:
                    return CHOOSING_ACTION
            
            category = session.pro_categories_order[session.current_category_index]
            
            # Получаем PRO-вопросы для текущей сферы и фильтруем по категории
            from src.telegram_bot_multi.questions import QuestionsManager
            qm = QuestionsManager(getattr(session, 'language', 'ru') or 'ru')
            all_pro_questions = qm.get_pro_questions(session.current_sphere)
            
            # Фильтруем вопросы по текущей категории
            pro_questions = []
            for q in all_pro_questions:
                if isinstance(q, dict):
                    q_category = q.get('category', '')
                elif isinstance(q, (list, tuple)) and len(q) > 1:
                    q_category = q[1] if isinstance(q[1], str) else ''
                else:
                    q_category = ''
                
                if q_category == category:
                    pro_questions.append(q)
            
            print(f"[PRO] Получено {len(pro_questions) if pro_questions else 0} PRO-вопросов для сферы {session.current_sphere}")
            
            # Если нет вопросов или все вопросы пройдены, переходим к следующей сфере
            if not pro_questions or session.current_pro_question >= len(pro_questions):
                session.current_sphere += 1
                session.current_pro_question = 0
                
                # Если все сферы пройдены, переходим к следующей категории
                if session.current_sphere > 8:
                    session.current_category_index += 1
                    session.current_sphere = 1
                    print(f"[PRO] Переходим к категории {session.current_category_index}")
                    
                    # Проверяем, завершен ли PRO-опрос
                    if session.current_category_index >= len(session.pro_categories_order):
                        print("[PRO] Все категории пройдены, завершаем PRO-опрос")
                        if query:
                            return await self._finish_pro_survey(query, session, context)
                        else:
                            return CHOOSING_ACTION
                
                # Рекурсивно вызываем для следующего вопроса
                return await self._show_pro_question(query, session, context)
            
            pro_q = pro_questions[session.current_pro_question]
            print(f"[PRO] Обрабатываем вопрос: {pro_q}")
            
            # Обрабатываем разные форматы PRO-вопросов
            if isinstance(pro_q, dict):
                pro_text = pro_q.get('text', '')
                fields = pro_q.get('fields', {})
            elif isinstance(pro_q, (list, tuple)):
                pro_text = pro_q[2] if len(pro_q) > 2 else str(pro_q)
                fields = pro_q[3] if len(pro_q) > 3 else {}
            else:
                pro_text = str(pro_q)
                fields = {}
            
            # Получаем название сферы для заголовка
            sphere_emojis = {
                1: '💖', 2: '🏡', 3: '🤝', 4: '💼', 
                5: '🏋️', 6: '🧠', 7: '🎨', 8: '💰'
            }
            sphere_names = {
                1: 'Отношения с любимыми', 2: 'Отношения с родными', 
                3: 'Друзья', 4: 'Карьера', 5: 'Физическое здоровье', 
                6: 'Ментальное здоровье', 7: 'Хобби и увлечения', 8: 'Благосостояние'
            }
            
            sphere_emoji = sphere_emojis.get(session.current_sphere, '')
            sphere_name = sphere_names.get(session.current_sphere, f'Сфера {session.current_sphere}')
            
            # Формируем заголовок сферы
            sphere_header = f"{sphere_emoji} {sphere_name}"
            
            # Получаем описание из pro_q
            description = ""
            if isinstance(pro_q, dict):
                description = pro_q.get('description', '')
            elif isinstance(pro_q, (list, tuple)) and len(pro_q) > 3:
                description = pro_q[3] if isinstance(pro_q[3], str) else ""
            
            # Формируем текст с вопросами из fields
            questions_text = ""
            if fields and isinstance(fields, dict):
                for i, (field_name, field_data) in enumerate(fields.items(), 1):
                    if isinstance(field_data, dict) and 'question' in field_data:
                        questions_text += f"{i}. {field_data['question']}\n"
                    else:
                        questions_text += f"{i}. {field_name}\n"
            
            # Собираем полный текст
            full_text = f"<b>{pro_text}</b>"
            if description:
                full_text += f"\n{description}"
            if questions_text:
                full_text += f"\n\n{questions_text}"
            
            # Сохраняем данные вопроса для обработки ответа
            session.current_pro_question_data = {
                'category': category,
                'sphere': session.current_sphere,
                'question_index': session.current_pro_question,
                'field_names': list(fields.keys()) if fields else [],
                'field_variants': {}
            }
            
            # Создаем клавиатуру с кнопками помощи
            keyboard = [
                [InlineKeyboardButton("📝 Помощь", callback_data="pro_help")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            lang = getattr(session, 'language', 'ru') or 'ru'
            texts = LOCALES[lang]
            
            if query:
                await query.edit_message_text(
                    f"{sphere_header}\n\n{full_text}",
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
            else:
                # Если query=None, отправляем новое сообщение
                if context and hasattr(context, 'bot'):
                    await context.bot.send_message(
                        chat_id=session.user_id if hasattr(session, 'user_id') else None,
                        text=f"{sphere_header}\n\n{full_text}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
            
            return COLLECTING_PRO
            
        except Exception as e:
            print(f"[PRO] Ошибка в _show_pro_question: {e}")
            import traceback
            traceback.print_exc()
            if query:
                await query.edit_message_text("Ошибка загрузки PRO-вопроса. Попробуйте позже.")
            return CHOOSING_ACTION

    async def _finish_pro_survey(self, query, session, context=None):
        """Завершает PRO-опрос и показывает результаты"""
        lang = getattr(session, 'language', 'ru') or 'ru'
        texts = LOCALES[lang]
        
        await query.edit_message_text(
            texts['pro_complete'],
            parse_mode=ParseMode.HTML
        )
        
        return CHOOSING_ACTION

    async def _finish_without_pro(self, query, session):
        """Завершает опрос без PRO-части"""
        await query.edit_message_text(
            "✅ Опрос завершен! Теперь вы можете посмотреть результаты в дашборде.",
            parse_mode=ParseMode.HTML
        )
        return CHOOSING_ACTION

    async def _show_pro_help(self, query, context):
        """Показывает справку по PRO-вопросам"""
        help_text = (
            "📝 <b>Как отвечать на PRO-вопросы:</b>\n\n"
            "1️⃣ <b>Отвечайте по порядку</b> - каждый ответ на новой строке\n"
            "2️⃣ <b>Будьте конкретны</b> - описывайте реальные ситуации\n"
            "3️⃣ <b>Используйте числа</b> для оценки серьёзности (1-10)\n"
            "4️⃣ <b>Указывайте даты</b> когда заметили проблему"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к вопросу", callback_data="pro_collapse")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        
        return COLLECTING_PRO

    async def _back_to_menu(self, query, context):
        """Возвращает к главному меню"""
        user = query.from_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        await query.edit_message_text(
            text=texts['welcome'],
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(texts['start_survey'], callback_data='start_survey')],
                [InlineKeyboardButton(texts['change_language'], callback_data='change_language')],
            ])
        )
        return CHOOSING_ACTION

    async def ask_pro_question(self, update, context):
        """Задает PRO-вопрос пользователю"""
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        from src.telegram_bot_multi.questions import QuestionsManager
        qm = QuestionsManager(lang)
        
        if session.current_sphere > 8:
            # PRO-опрос завершен
            await context.bot.send_message(
                chat_id=user.id,
                text=texts['pro_complete'],
                parse_mode=ParseMode.HTML
            )
            return CHOOSING_ACTION
        
        # Получаем PRO-вопросы для текущей сферы
        pro_questions = qm.get_pro_questions(session.current_sphere)
        if not pro_questions or session.current_pro_question >= len(pro_questions):
            # Переходим к следующей сфере
            session.current_sphere += 1
            session.current_pro_question = 0
            return await self.ask_pro_question(update, context)
        
        pro_q = pro_questions[session.current_pro_question]
        pro_text = pro_q.get('text') if isinstance(pro_q, dict) else (pro_q[2] if isinstance(pro_q, (list, tuple)) and len(pro_q) > 2 else str(pro_q))
        
        await context.bot.send_message(
            chat_id=user.id,
            text=f"<b>{texts['pro_question']}</b>\n\n{pro_text}\n\n{texts['pro_help']}",
            parse_mode=ParseMode.HTML
        )
        
        return COLLECTING_PRO

    async def fallback_handler(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        await context.bot.send_message(
            chat_id=user.id,
            text=texts['error'].format(error='Неизвестная команда или сообщение.' if lang == 'ru' else 'Unknown command or message.'),
            parse_mode=ParseMode.HTML
        )
        return CHOOSING_ACTION

    async def _handle_answer(self, update, context):
        query = update.callback_query
        user = query.from_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
        data = query.data
        
        if data == 'back_to_menu':
            await query.answer()
            await query.edit_message_text(
                text=texts['welcome'],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(texts['start_survey'], callback_data='start_survey')],
                    [InlineKeyboardButton(texts['change_language'], callback_data='change_language')],
                ])
            )
            return CHOOSING_ACTION
        
        # Обрабатываем ответ на вопрос
        if data.startswith('answer_'):
            answer_index = int(data.split('_')[1])
            
            # Сохраняем ответ
            sphere_key = str(session.current_sphere)
            if sphere_key not in session.answers:
                session.answers[sphere_key] = []
            
            # Получаем вопрос для определения балла
            from src.telegram_bot_multi.questions import QuestionsManager
            qm = QuestionsManager(lang)
            sphere = qm.get_sphere(session.current_sphere)
            if sphere and session.current_question < len(sphere.questions):
                question = sphere.questions[session.current_question]
                if answer_index < len(question['scores']):
                    score = question['scores'][answer_index]
                    session.answers[sphere_key].append(score)
                    
                    # Сохраняем ответ в БД
                    try:
                        from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id, save_answer
                        
                        user_id = get_user_id_by_telegram_id(user.id)
                        if not user_id:
                            # Создаем пользователя если его нет
                            from src.telegram_bot_multi.db_async import save_user
                            user_id = await save_user(user.id, user.username, user.first_name, user.last_name)
                        
                        if user_id:
                            question_id = f"{sphere_key}.{session.current_question}"
                            await save_answer(user_id, sphere_key, question_id, score)
                            print(f"[DB] Сохранен ответ: сфера {sphere_key}, вопрос {session.current_question}, балл {score}")
                            
                    except Exception as e:
                        print(f"[DB] Ошибка сохранения ответа в БД: {e}")
            
            # Переходим к следующему вопросу
            session.current_question += 1
            
            await query.answer()
            
            # Проверяем, нужно ли перейти к следующей сфере
            if sphere and session.current_question >= len(sphere.questions):
                session.current_sphere += 1
                session.current_question = 0
            
            # Проверяем, завершен ли опрос
            if session.current_sphere > 8:
                return await self._ask_pro_survey(query, session)
            
            # Задаем следующий вопрос
            sphere = qm.get_sphere(session.current_sphere)
            if not sphere:
                await query.edit_message_text("Ошибка загрузки вопросов. Попробуйте позже.")
                return CHOOSING_ACTION
            
            question = sphere.questions[session.current_question]
            question_text = f"<b>{sphere.name}</b>\n\n{question['text']}"
            total_answered = sum(len(answers) for answers in session.answers.values())
            progress_text = f"📊 <b>Прогресс:</b> {total_answered}/48 вопросов"
            
            # Создаем клавиатуру с вариантами ответов
            keyboard = []
            for i, option in enumerate(question['options']):
                keyboard.append([InlineKeyboardButton(
                    option, 
                    callback_data=f"answer_{i}"
                )])
            
            # Добавляем кнопку "Назад"
            keyboard.append([InlineKeyboardButton(
                texts.get('back', 'Назад'), 
                callback_data='back_to_menu'
            )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{question_text}\n\n{progress_text}",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            
            return ANSWERING_QUESTIONS
        
        await query.answer()
        return ANSWERING_QUESTIONS

    async def _handle_pro_answer(self, update, context):
        try:
            if update.message:
                await update.message.reply_text("✅ Сообщение получено ботом!")
            print(f"[DEBUG] Сообщение получено в боте: {update.message.text if update.message else ''}")
            
            user = update.effective_user
            session = self.session_manager.get_session(user.id)
            print(f"[PRO] id(session) при ответе: {id(session)}, telegram_id={user.id}")
            
            if not hasattr(session, 'current_pro_question_data') or session.current_pro_question_data is None:
                print(f"[PRO] Нет current_pro_question_data в сессии!")
                return CHOOSING_ACTION
            
            pro_data = session.current_pro_question_data
            user_text = update.message.text if update.message else ""
            answers_list = [a.strip() for a in user_text.split('\n') if a.strip()]
            field_names = pro_data['field_names']
            field_variants = pro_data.get('field_variants', {})
            
            # Проверяем количество ответов
            if len(answers_list) != len(field_names):
                if len(answers_list) > len(field_names):
                    extra_fields = answers_list[len(field_names):]
                    await update.message.reply_text(
                        f"Вы ввели {len(answers_list)} ответов, а нужно {len(field_names)}. Лишние: {', '.join(extra_fields)}",
                        parse_mode=ParseMode.HTML
                    )
                else:
                    missing_fields = field_names[len(answers_list):]
                    await update.message.reply_text(
                        f"Вы ввели {len(answers_list)} ответов, а нужно {len(field_names)}. Не хватает: {', '.join(missing_fields)}",
                        parse_mode=ParseMode.HTML
                    )
                return COLLECTING_PRO
            
            # Сохраняем ответы
            category = pro_data['category']
            sphere = pro_data['sphere']
            
            if category not in session.pro_data:
                session.pro_data[category] = {}
            if sphere not in session.pro_data[category]:
                session.pro_data[category][sphere] = []
            
            # Создаем объект с ответами
            answer_obj = {}
            for i, field_name in enumerate(field_names):
                answer_obj[field_name] = answers_list[i]
            
            session.pro_data[category][sphere].append(answer_obj)
            
            # Сохраняем в БД
            try:
                from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id, save_problem, save_goal, save_blocker, save_metric, save_achievement
                
                user_id = await get_user_id_by_telegram_id(user.id)
                if not user_id:
                    # Создаем пользователя если его нет
                    from src.telegram_bot_multi.db_async import save_user
                    user_id = await save_user(user.id, user.username, user.first_name, user.last_name)
                
                if user_id:
                    sphere_key = str(sphere)
                    
                    if category == 'problems':
                        text = answer_obj.get('text', '')
                        status = answer_obj.get('status', 'active')
                        severity = int(answer_obj.get('severity', 5))
                        date_noticed = answer_obj.get('date_noticed', '2024-01-01')
                        await save_problem(user_id, sphere_key, text, status, severity, date_noticed)
                        print(f"[DB] Сохранена проблема: {text}")
                        
                    elif category == 'goals':
                        text = answer_obj.get('text', '')
                        status = answer_obj.get('status', 'planned')
                        deadline = answer_obj.get('deadline', '')
                        priority = int(answer_obj.get('priority', 5))
                        save_goal(user_id, sphere_key, text, deadline, priority, status)
                        print(f"[DB] Сохранена цель: {text}")
                        
                    elif category == 'blockers':
                        text = answer_obj.get('text', '')
                        impact_level = answer_obj.get('impact_level', 'medium')
                        status = answer_obj.get('status', 'active')
                        resolution_plan = answer_obj.get('resolution_plan', '')
                        save_blocker(user_id, sphere_key, text, impact_level, status, resolution_plan)
                        print(f"[DB] Сохранен блокер: {text}")
                        
                    elif category == 'metrics':
                        name = answer_obj.get('name', '')
                        current_value = float(answer_obj.get('current_value', 0))
                        target_value = float(answer_obj.get('target_value', 0))
                        unit = answer_obj.get('unit', '')
                        type_ = answer_obj.get('type', 'number')
                        save_metric(user_id, sphere_key, name, current_value, target_value, type_)
                        print(f"[DB] Сохранена метрика: {name}")
                        
                    elif category == 'achievements':
                        description = answer_obj.get('text', '')
                        date_achieved = answer_obj.get('date_achieved', '')
                        impact_areas = answer_obj.get('impact_areas', '')
                        save_achievement(user_id, sphere_key, description, date_achieved, impact_areas)
                        print(f"[DB] Сохранено достижение: {description}")
                        
            except Exception as e:
                print(f"[DB] Ошибка сохранения в БД: {e}")
            
            # Переходим к следующему вопросу
            session.current_pro_question += 1
            
            # Переходим к следующему вопросу
            session.current_pro_question += 1
            
            # Проверяем, нужно ли перейти к следующей сфере
            from src.telegram_bot_multi.questions import QuestionsManager
            qm = QuestionsManager(getattr(session, 'language', 'ru') or 'ru')
            all_pro_questions = qm.get_pro_questions(session.current_sphere)
            
            # Фильтруем вопросы по текущей категории
            category = session.pro_categories_order[session.current_category_index]
            pro_questions = []
            for q in all_pro_questions:
                if isinstance(q, dict):
                    q_category = q.get('category', '')
                elif isinstance(q, (list, tuple)) and len(q) > 1:
                    q_category = q[1] if isinstance(q[1], str) else ''
                else:
                    q_category = ''
                
                if q_category == category:
                    pro_questions.append(q)
            
            if session.current_pro_question >= len(pro_questions):
                # Переходим к следующей сфере
                session.current_sphere += 1
                session.current_pro_question = 0
                
                if session.current_sphere > 8:
                    # Все сферы пройдены, переходим к следующей категории
                    session.current_category_index += 1
                    session.current_sphere = 1
                    
                    if session.current_category_index >= len(session.pro_categories_order):
                        await update.message.reply_text(
                            "✅ PRO-опрос завершен! Теперь у вас есть полные данные для анализа.",
                            parse_mode=ParseMode.HTML
                        )
                        return CHOOSING_ACTION
            
            # Задаем следующий PRO-вопрос
            return await self._show_pro_question(None, session, context)
            
        except Exception as e:
            print(f"[PRO] Ошибка в _handle_pro_answer: {e}")
            await update.message.reply_text("Произошла ошибка при обработке ответа. Попробуйте еще раз.")
            return COLLECTING_PRO

    async def show_dashboard(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        from src.calculator import HPICalculator
        hpi_total, sphere_scores = '—', {}
        answers = session.answers
        pro_data = session.pro_data
        print('[DEBUG] session.answers:', answers)
        print('[DEBUG] session.pro_data:', pro_data)
        # Оставляем только ключи '1'-'8' для расчёта HPI
        filtered_answers = {str(i): answers.get(str(i), []) for i in range(1, 9)}
        # --- DEBUG: выводим количество ответов ---
        print(f"[DEBUG] Ответы по сферам: {{ {', '.join(f'{k}: {len(v)}' for k, v in filtered_answers.items())} }}")
        is_full = all(len(filtered_answers[str(i)]) == 6 for i in range(1, 9))
        if is_full:
            try:
                hpi_total, sphere_scores = HPICalculator().calculate_from_answers(filtered_answers)
            except Exception:
                hpi_total, sphere_scores = '—', {}
        # Формируем красивый дашборд
        lines = []
        # Красивый блок HPI
        sphere_emojis = {
            '1': '💖',
            '2': '🏡',
            '3': '🤝',
            '4': '💼',
            '5': '🏋️',
            '6': '🧠',
            '7': '🎨',
            '8': '💰',
        }
        sphere_names = {
            '1': 'Отношения с любимыми' if lang == 'ru' else 'Relationships with loved ones',
            '2': 'Отношения с родными' if lang == 'ru' else 'Family relationships',
            '3': 'Друзья' if lang == 'ru' else 'Friends',
            '4': 'Карьера' if lang == 'ru' else 'Career',
            '5': 'Физическое здоровье' if lang == 'ru' else 'Physical health',
            '6': 'Ментальное здоровье' if lang == 'ru' else 'Mental health',
            '7': 'Хобби и увлечения' if lang == 'ru' else 'Hobbies and interests',
            '8': 'Благосостояние' if lang == 'ru' else 'Well-being',
        }
        def color_emoji(val):
            if not isinstance(val, (int, float)):
                return '⚪'
            if val >= 8:
                return '🟢'
            elif val >= 6:
                return '🟡'
            elif val >= 4:
                return '🟠'
            else:
                return '🔴'
        lines.append('🏆 <b>HPI (Human Performance Index)</b>')
        if isinstance(hpi_total, (int, float)):
            lines.append(f'<b>{"Общий HPI:" if lang == "ru" else "Overall HPI:"}</b> <b>{hpi_total:.1f}</b> {color_emoji(hpi_total)}\n')
        else:
            lines.append(f'<b>{"Общий HPI:" if lang == "ru" else "Overall HPI:"}</b> <b>{hpi_total}</b>\n')
        for k in map(str, range(1, 9)):
            emoji = sphere_emojis.get(k, '')
            name = sphere_names.get(k, f'Sphere {k}')
            val = sphere_scores.get(k, '—')
            color = color_emoji(val)
            lines.append(f'{emoji} <b>{name}:</b> {val if isinstance(val, str) else f"{val:.1f}"} {color}')
        # Новый порядок кнопок, как в русском боте
        keyboard = [
            [InlineKeyboardButton(texts.get('trend', '📈 Динамика HPI'), callback_data='show_trend')],
            [InlineKeyboardButton(texts.get('radar', '⚖️ Баланс по сферам'), callback_data='show_radar')],
            [InlineKeyboardButton('— ' + texts.get('pro_sections', 'ПРО РАЗДЕЛЫ') + ' —', callback_data='noop')],
            [InlineKeyboardButton('🔴 ' + texts.get('problems', 'Мои проблемы'), callback_data='show_problems')],
            [InlineKeyboardButton('🎯 ' + texts.get('goals', 'Мои цели'), callback_data='show_goals')],
            [InlineKeyboardButton('⛔ ' + texts.get('blockers', 'Мои блокеры'), callback_data='show_blockers')],
            [InlineKeyboardButton('📊 ' + texts.get('metrics', 'Мои метрики'), callback_data='show_metrics')],
            [InlineKeyboardButton('🏆 ' + texts.get('achievements', 'Мои достижения'), callback_data='show_achievements')],
            [InlineKeyboardButton('💡 ' + texts.get('basic_recs', 'Базовые рекомендации'), callback_data='show_basic_recs')],
            [InlineKeyboardButton('🤖 ' + texts.get('ai_recs', 'AI рекомендации'), callback_data='show_ai_recs')],
            [InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')],
        ]
        await context.bot.send_message(
            chat_id=user.id,
            text='\n'.join(lines),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSING_ACTION

    async def show_pro_dashboard(self, update, context):
        """Показывает сокращенный дашборд с PRO-разделами"""
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        
                # Загружаем данные из БД
        from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id, get_user_problems, get_user_goals, get_user_blockers, get_user_metrics
        
        user_id = await get_user_id_by_telegram_id(user.id)
        if not user_id:
            await context.bot.send_message(
                chat_id=user.id,
                text="Пользователь не найден в базе. Пройдите опрос сначала.",
                parse_mode=ParseMode.HTML
            )
            return CHOOSING_ACTION
        
        # Загружаем PRO-данные из БД
        session.problems = await get_user_problems(user_id)
        session.goals = await get_user_goals(user_id)
        session.blockers = await get_user_blockers(user_id)
        session.metrics = await get_user_metrics(user_id)
        
        # Проверяем, есть ли базовые ответы для расчета HPI
        answers = session.answers
        if not (isinstance(answers, dict) and len(answers) == 8 and all(len(answers.get(str(i), [])) == 6 for i in range(1, 9))):
            await context.bot.send_message(
                chat_id=user.id,
                text="Невозможно рассчитать HPI: не все сферы заполнены. Пройдите базовую часть полностью.",
                parse_mode=ParseMode.HTML
            )
            return CHOOSING_ACTION
        
        # Генерируем рекомендации если их нет
        if not hasattr(session, 'recommendations') or not session.recommendations:
            await self._generate_metrics_and_recommendations(session)
        
        # Рассчитываем HPI
        from src.calculator import HPICalculator
        try:
            hpi_total, sphere_scores = HPICalculator().calculate_from_answers(answers)
        except Exception as e:
            hpi_total = 0.0
            print(f"Ошибка расчёта HPI: {e}")
        
        # Формируем текст
        main_text = (
            f"<b>{'HPI человека (Полная версия)' if lang == 'ru' else 'Human HPI (Full Version)'}</b>\n\n"
            f"{'Текущий HPI:' if lang == 'ru' else 'Current HPI:'} <b>{hpi_total:.1f if isinstance(hpi_total, (int, float)) else hpi_total}</b>\n\n"
            f"{'Вы прошли расширенную часть опроса! Теперь у вас есть доступ к полным данным.' if lang == 'ru' else 'You have completed the extended survey! Now you have access to full data.'}\n\n"
            f"{'Выберите раздел для просмотра подробностей:' if lang == 'ru' else 'Choose a section to view details:'}"
        )
        
        # Создаем клавиатуру
        menu_keyboard = [
            [InlineKeyboardButton(texts.get('trend', '📈 Динамика HPI'), callback_data='show_trend')],
            [InlineKeyboardButton(texts.get('radar', '⚖️ Баланс по сферам'), callback_data='show_radar')],
            [InlineKeyboardButton('— ' + texts.get('pro_sections', 'ПРО РАЗДЕЛЫ') + ' —', callback_data='noop')],
            [InlineKeyboardButton('🔴 ' + texts.get('problems', 'Мои проблемы'), callback_data='show_problems')],
            [InlineKeyboardButton('🎯 ' + texts.get('goals', 'Мои цели'), callback_data='show_goals')],
            [InlineKeyboardButton('⛔ ' + texts.get('blockers', 'Мои блокеры'), callback_data='show_blockers')],
            [InlineKeyboardButton('📊 ' + texts.get('metrics', 'Мои метрики'), callback_data='show_metrics')],
            [InlineKeyboardButton('💡 ' + texts.get('basic_recs', 'Базовые рекомендации'), callback_data='show_basic_recs')],
            [InlineKeyboardButton('🤖 ' + texts.get('ai_recs', 'AI рекомендации'), callback_data='show_ai_recs')],
        ]
        
        reply_markup = InlineKeyboardMarkup(menu_keyboard)
        
        await context.bot.send_message(
            chat_id=user.id,
            text=main_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return CHOOSING_ACTION

    async def show_basic_recs(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        try:
            hpi_total, sphere_scores = HPICalculator().calculate_from_answers(session.answers)
        except Exception:
            hpi_total, sphere_scores = '—', {}
        
        # Проверяем, нужно ли перегенерировать рекомендации для нового языка
        current_lang = getattr(session, 'recommendations_lang', None)
        if current_lang != lang or not session.recommendations:
            print(f'[DEBUG] Перегенерируем рекомендации для языка {lang}...')
            session.recommendations_lang = lang
            await self._generate_metrics_and_recommendations(session)
            print('[DEBUG] После генерации session.recommendations:', session.recommendations)
        
        print('[DEBUG] session.recommendations:', session.recommendations)
        text = self.format_recommendations(session.recommendations, lang, sphere_scores)
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_ai_recs(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        try:
            hpi_total, sphere_scores = HPICalculator().calculate_from_answers(session.answers)
        except Exception:
            hpi_total, sphere_scores = '—', {}
        
        # Проверяем, нужно ли перегенерировать AI рекомендации для нового языка
        current_lang = getattr(session, 'ai_recommendations_lang', None)
        if current_lang != lang or not session.ai_recommendations:
            print(f'[DEBUG] Перегенерируем AI рекомендации для языка {lang}...')
            session.ai_recommendations_lang = lang
            await self._generate_metrics_and_recommendations(session)
        
        print('[DEBUG] session.ai_recommendations:', session.ai_recommendations)
        text = self.format_ai_recommendations(session.ai_recommendations, lang, sphere_scores)
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_recommendations(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        try:
            hpi_total, sphere_scores = HPICalculator().calculate_from_answers(session.answers)
        except Exception:
            hpi_total, sphere_scores = '—', {}
        print('[DEBUG] session.recommendations:', session.recommendations)
        text = self.format_recommendations(session.recommendations, lang, sphere_scores)
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_trend(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        try:
            from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id
            from src.trend import plot_hpi_trend_for_telegram
            db_user_id = await get_user_id_by_telegram_id(user.id)
            buf = await plot_hpi_trend_for_telegram(db_user_id, lang=lang)
            if buf:
                keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
                await context.bot.send_photo(chat_id=user.id, photo=buf, caption=texts['trend'], reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
                await context.bot.send_message(chat_id=user.id, text=texts['trend'] + '\n<i>Нет данных для графика.</i>', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
            await context.bot.send_message(chat_id=user.id, text=f"Ошибка построения графика: {e}", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_radar(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        try:
            from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id
            from src.radar import plot_radar_chart_for_telegram
            db_user_id = await get_user_id_by_telegram_id(user.id)
            buf = await plot_radar_chart_for_telegram(db_user_id, lang=lang)
            if buf:
                keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
                await context.bot.send_photo(chat_id=user.id, photo=buf, caption=texts['radar'], reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
                await context.bot.send_message(chat_id=user.id, text=texts['radar'] + '\n<i>Нет данных для графика.</i>', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
            await context.bot.send_message(chat_id=user.id, text=f"Ошибка построения графика: {e}", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_problems(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        problems = []
        print('[DEBUG] session.problems:', session.problems)
        # Оставляем только последние записи по каждой сфере
        last_by_sphere = {}
        for p in session.problems:
            sphere = p.get('sphere') if isinstance(p, dict) else p['sphere']
            created = p.get('created_at') if isinstance(p, dict) else p['created_at']
            if sphere not in last_by_sphere or created > last_by_sphere[sphere].get('created_at', created):
                last_by_sphere[sphere] = p
        for p in last_by_sphere.values():
            sphere = p.get('sphere') if isinstance(p, dict) else p['sphere']
            text = p.get('text') if isinstance(p, dict) else p['text']
            severity = p.get('severity') if isinstance(p, dict) else p['severity']
            status = p.get('status') if isinstance(p, dict) else p['status']
            date = p.get('created_at') if isinstance(p, dict) else p['created_at']
            translated_sphere = self._translate_sphere_name(sphere, lang)
            lines = [f"<b>{translated_sphere}</b>"]
            if text:
                lines.append(("📝 Описание:" if lang=='ru' else '📝 Description:') + f" {text}")
            if severity:
                lines.append(("Серьёзность:" if lang=='ru' else 'Severity:') + f" {severity}")
            if status:
                lines.append(("Статус:" if lang=='ru' else 'Status:') + f" {status}")
            if date:
                lines.append(("📅 Дата:" if lang=='ru' else '📅 Date:') + f" {date}")
            lines.append("━━━━━━━━━━━━━━")
            problems.append("\n".join(lines))
        if problems:
            msg = '<b>' + texts.get('problems', 'Problems') + '</b>\n' + '\n'.join(problems)
        else:
            msg = ('🔴 <i>Нет данных о проблемах.</i>' if lang=='ru' else '🔴 <i>No problem data.</i>')
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_goals(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        goals = []
        print('[DEBUG] session.goals:', session.goals)
        # Оставляем только последние записи по каждой сфере
        last_by_sphere = {}
        if getattr(session, 'goals', None):
            for g in session.goals:
                sphere = g.get('sphere', '')
                created = g.get('created_at', g.get('deadline', ''))
                if sphere not in last_by_sphere or created > last_by_sphere[sphere].get('created_at', last_by_sphere[sphere].get('deadline', '')):
                    last_by_sphere[sphere] = g
            for g in last_by_sphere.values():
                sphere = g.get('sphere', '')
                text = g.get('text', '')
                priority = g.get('priority', '')
                status = g.get('status', '')
                date = g.get('deadline', '')
                translated_sphere = self._translate_sphere_name(sphere, lang)
                lines = [f"<b>{translated_sphere}</b>"]
                if text:
                    lines.append(("📝 Описание:" if lang=='ru' else '📝 Description:') + f" {text}")
                if priority:
                    lines.append(("Приоритет:" if lang=='ru' else 'Priority:') + f" {priority}")
                if status:
                    lines.append(("Статус:" if lang=='ru' else 'Status:') + f" {status}")
                if date:
                    lines.append(("📅 Дата:" if lang=='ru' else '📅 Date:') + f" {date}")
                lines.append("━━━━━━━━━━━━━━")
                goals.append("\n".join(lines))
        if goals:
            msg = '<b>' + texts.get('goals', 'Goals') + '</b>\n' + '\n'.join(goals)
        else:
            msg = ('🎯 <i>Нет данных о целях.</i>' if lang=='ru' else '🎯 <i>No goal data.</i>')
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_blockers(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        blockers = []
        print('[DEBUG] session.blockers:', session.blockers)
        # Оставляем только последние записи по каждой сфере
        last_by_sphere = {}
        if getattr(session, 'blockers', None):
            for b in session.blockers:
                sphere = b.get('sphere', '')
                created = b.get('created_at', '')
                if sphere not in last_by_sphere or created > last_by_sphere[sphere].get('created_at', ''):
                    last_by_sphere[sphere] = b
            for b in last_by_sphere.values():
                sphere = b.get('sphere', '')
                text = b.get('text', '')
                impact = b.get('impact_level', '')
                related = b.get('related_goals', '')
                date = b.get('created_at', '')
                translated_sphere = self._translate_sphere_name(sphere, lang)
                lines = [f"<b>{translated_sphere}</b>"]
                if text:
                    lines.append(("📝 Описание:" if lang=='ru' else '📝 Description:') + f" {text}")
                if impact:
                    lines.append(("Степень влияния:" if lang=='ru' else 'Impact level:') + f" {impact}")
                if related:
                    lines.append(("Связанные цели:" if lang=='ru' else 'Related goals:') + f" {related}")
                if date:
                    lines.append(("📅 Дата:" if lang=='ru' else '📅 Date:') + f" {date}")
                lines.append("━━━━━━━━━━━━━━")
                blockers.append("\n".join(lines))
        if blockers:
            msg = '<b>' + texts.get('blockers', 'Blockers') + '</b>\n' + '\n'.join(blockers)
        else:
            msg = ('⛔ <i>Нет данных о барьерах.</i>' if lang=='ru' else '⛔ <i>No blocker data.</i>')
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_metrics(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        metrics = []
        print('[DEBUG] session.metrics:', session.metrics)
        # Оставляем только последние записи по каждой сфере
        last_by_sphere = {}
        if getattr(session, 'metrics', None):
            for m in session.metrics:
                sphere = m.get('sphere', '')
                created = m.get('created_at', '')
                if sphere not in last_by_sphere or created > last_by_sphere[sphere].get('created_at', ''):
                    last_by_sphere[sphere] = m
            for m in last_by_sphere.values():
                sphere = m.get('sphere', '')
                name = m.get('name', '')
                current = m.get('current_value', '')
                target = m.get('target_value', '')
                unit = m.get('unit', '')
                type_ = m.get('type', '')
                date = m.get('created_at', '')
                translated_sphere = self._translate_sphere_name(sphere, lang)
                lines = [f"<b>{translated_sphere}</b>"]
                if name:
                    lines.append(("📝 Описание:" if lang=='ru' else '📝 Description:') + f" {name}")
                if current:
                    lines.append(("📊 Текущее:" if lang=='ru' else '📊 Current:') + f" {current} {unit}")
                if target:
                    lines.append(("🎯 Цель:" if lang=='ru' else '🎯 Target:') + f" {target} {unit}")
                if type_:
                    lines.append(("Тип:" if lang=='ru' else 'Type:') + f" {type_}")
                if date:
                    lines.append(("📅 Дата:" if lang=='ru' else '📅 Date:') + f" {date}")
                lines.append("━━━━━━━━━━━━━━")
                metrics.append("\n".join(lines))
        if metrics:
            msg = '<b>' + texts.get('metrics', 'Metrics') + '</b>\n' + '\n'.join(metrics)
        else:
            msg = ('📊 <i>Нет данных о метриках.</i>' if lang=='ru' else '📊 <i>No metric data.</i>')
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_achievements(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        print('[DEBUG] session.achievements:', getattr(session, 'achievements', None))
        achievements = []
        # Оставляем только последние записи по каждой сфере
        last_by_sphere = {}
        if getattr(session, 'achievements', None):
            for a in session.achievements:
                sphere = a.get('sphere', '')
                created = a.get('date_achieved', a.get('created_at', ''))
                if sphere not in last_by_sphere or created > last_by_sphere[sphere].get('date_achieved', last_by_sphere[sphere].get('created_at', '')):
                    last_by_sphere[sphere] = a
            for a in last_by_sphere.values():
                sphere = a.get('sphere', '')
                desc = a.get('description', '')
                impact = a.get('impact_areas', '')
                date = a.get('date_achieved', '')
                translated_sphere = self._translate_sphere_name(sphere, lang)
                lines = [f"<b>{translated_sphere}</b>"]
                if desc:
                    # Переводим содержимое описания
                    translated_desc = desc
                    if desc == "Описание достижения" and lang == 'en':
                        translated_desc = texts.get('achievement_description', 'Achievement description')
                    lines.append(("📝 Описание:" if lang=='ru' else '📝 Description:') + f" {translated_desc}")
                if impact:
                    # Переводим содержимое областей влияния
                    translated_impact = impact
                    if impact == "Сферы, на которые это повлияло" and lang == 'en':
                        translated_impact = texts.get('achievement_impact_areas', 'Areas that this affected')
                    lines.append(("Области влияния:" if lang=='ru' else 'Impact areas:') + f" {translated_impact}")
                if date:
                    lines.append(("📅 Дата:" if lang=='ru' else '📅 Date:') + f" {date}")
                lines.append("━━━━━━━━━━━━━━")
                achievements.append("\n".join(lines))
        if achievements:
            msg = '<b>' + texts.get('achievements', 'Achievements') + '</b>\n' + '\n'.join(achievements)
        else:
            msg = ('🏆 <i>Нет данных о достижениях.</i>' if lang=='ru' else '🏆 <i>No achievement data.</i>')
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def show_answers(self, update, context):
        user = update.effective_user
        session = self.session_manager.get_session(user.id)
        lang = session.language or 'ru'
        texts = LOCALES[lang]
        answers = session.answers
        if not answers or not isinstance(answers, dict) or not any(answers.values()):
            keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
            await context.bot.send_message(chat_id=user.id, text='<i>Нет сохранённых ответов. Пройдите опрос!</i>' if lang == 'ru' else '<i>No saved answers. Take the survey!</i>', parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
            return CHOOSING_ACTION
        lines = ["<b>Ваши ответы по сферам:</b>" if lang == 'ru' else "<b>Your answers by spheres:</b>"]
        for i in range(1, 9):
            key = str(i)
            sphere_answers = answers.get(key) or []
            if not sphere_answers:
                continue
            # Получаем название сферы
            from src.telegram_bot_multi.questions import QuestionsManager
            qm = QuestionsManager(lang)
            sphere = qm.get_sphere(i)
            sphere_name = getattr(sphere, 'name', f'Sphere {i}')
            emoji = getattr(sphere, 'emoji', '')
            lines.append(f"{emoji} <b>{sphere_name}</b>:")
            for idx, ans in enumerate(sphere_answers, 1):
                lines.append(f"{idx}. {ans+1 if isinstance(ans, int) else ans}")
        keyboard = [[InlineKeyboardButton('🗑️ ' + (texts.get('hide', 'Свернуть') if lang == 'ru' else 'Hide'), callback_data='hide_dashboard')]]
        await context.bot.send_message(chat_id=user.id, text='\n'.join(lines), parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_ACTION

    async def hide_dashboard(self, update, context):
        query = getattr(update, 'callback_query', None)
        if query and hasattr(query, 'message'):
            try:
                await query.message.delete()
            except Exception as e:
                print(f"[DEBUG] Ошибка при удалении сообщения: {e}")
        return CHOOSING_ACTION

    async def _generate_metrics_and_recommendations(self, session):
        import openai
        import os
        print('[DEBUG] Начинаем генерацию рекомендаций...')
        user_data = []
        # Добавляем баллы по сферам
        if hasattr(session, 'answers') and session.answers:
            calculator = HPICalculator()
            try:
                hpi_total, scores = calculator.calculate_from_answers(session.answers)
                for i in range(1, 9):
                    sphere_name = self._get_sphere_info(str(i))[1]
                    score = scores.get(str(i), 0)
                    user_data.append(f"[score] {sphere_name}: {score}")
            except Exception as e:
                print(f"Ошибка расчёта баллов: {e}")
        # Добавляем PRO-данные
        for sphere_key, sphere_data in session.pro_data.items():
            for category, items in sphere_data.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            user_data.append(f"[{category}] {item.get('emoji','')} {item.get('sphere_name','')}: {item.get('text','')}")
                        else:
                            user_data.append(f"[{category}] {sphere_key}: {str(item)}")
                else:
                    # Если items - это строка
                    user_data.append(f"[{category}] {sphere_key}: {str(items)}")
        # Определяем язык для генерации
        lang = getattr(session, 'language', 'ru')
        lang = lang or 'ru'
        
        # Создаем промпт на нужном языке
        if lang == 'en':
            prompt = (
                "You are a human development expert. Create recommendations for ALL 8 life areas based on user data.\n\n"
                "MUST create recommendations for ALL 8 areas:\n"
                "1. Relationships with loved ones (💖)\n"
                "2. Family relationships (🏡)\n"
                "3. Friends (👥)\n"
                "4. Career (💼)\n"
                "5. Physical health (💪)\n"
                "6. Mental health (🧠)\n"
                "7. Hobbies and interests (🎨)\n"
                "8. Well-being (💰)\n\n"
                "Return ONLY valid JSON with recommendations for ALL 8 areas:\n"
                "{\n"
                '  "recommendations": [\n'
                '    {"sphere": "Relationships with loved ones", "emoji": "💖", "text": "Brief recommendation"},\n'
                '    {"sphere": "Family relationships", "emoji": "🏡", "text": "Brief recommendation"},\n'
                '    {"sphere": "Friends", "emoji": "👥", "text": "Brief recommendation"},\n'
                '    {"sphere": "Career", "emoji": "💼", "text": "Brief recommendation"},\n'
                '    {"sphere": "Physical health", "emoji": "💪", "text": "Brief recommendation"},\n'
                '    {"sphere": "Mental health", "emoji": "🧠", "text": "Brief recommendation"},\n'
                '    {"sphere": "Hobbies and interests", "emoji": "🎨", "text": "Brief recommendation"},\n'
                '    {"sphere": "Well-being", "emoji": "💰", "text": "Brief recommendation"}\n'
                '  ],\n'
                '  "ai_recommendations": [\n'
                '    {"sphere": "Relationships with loved ones", "emoji": "💖", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Family relationships", "emoji": "🏡", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Friends", "emoji": "👥", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Career", "emoji": "💼", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Physical health", "emoji": "💪", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Mental health", "emoji": "🧠", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Hobbies and interests", "emoji": "🎨", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"},\n'
                '    {"sphere": "Well-being", "emoji": "💰", "title": "Plan title", "desc": "Description", "steps": "1. Step 1\\n2. Step 2"}\n'
                '  ]\n'
                "}\n\n"
                "User data:\n" + "\n".join(user_data)
            )
        else:
            prompt = (
                "Ты эксперт по развитию человека. Создай рекомендации для ВСЕХ 8 сфер жизни на основе данных пользователя.\n\n"
                "ОБЯЗАТЕЛЬНО создай рекомендации для ВСЕХ 8 сфер:\n"
                "1. Отношения с любимыми (💖)\n"
                "2. Отношения с родными (🏡)\n"
                "3. Друзья (👥)\n"
                "4. Карьера (💼)\n"
                "5. Физическое здоровье (💪)\n"
                "6. Ментальное здоровье (🧠)\n"
                "7. Хобби и увлечения (🎨)\n"
                "8. Благосостояние (💰)\n\n"
                "Верни ТОЛЬКО валидный JSON с рекомендациями для ВСЕХ 8 сфер:\n"
                "{\n"
                '  "recommendations": [\n'
                '    {"sphere": "Отношения с любимыми", "emoji": "💖", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Отношения с родными", "emoji": "🏡", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Друзья", "emoji": "👥", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Карьера", "emoji": "💼", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Физическое здоровье", "emoji": "💪", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Ментальное здоровье", "emoji": "🧠", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Хобби и увлечения", "emoji": "🎨", "text": "Краткая рекомендация"},\n'
                '    {"sphere": "Благосостояние", "emoji": "💰", "text": "Краткая рекомендация"}\n'
                '  ],\n'
                '  "ai_recommendations": [\n'
                '    {"sphere": "Отношения с любимыми", "emoji": "💖", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Отношения с родными", "emoji": "🏡", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Друзья", "emoji": "👥", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Карьера", "emoji": "💼", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Физическое здоровье", "emoji": "💪", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Ментальное здоровье", "emoji": "🧠", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Хобби и увлечения", "emoji": "🎨", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"},\n'
                '    {"sphere": "Благосостояние", "emoji": "💰", "title": "Заголовок плана", "desc": "Описание", "steps": "1. Шаг 1\\n2. Шаг 2"}\n'
                '  ]\n'
                "}\n\n"
                "Данные пользователя:\n" + "\n".join(user_data)
            )
        try:
            from openai import AsyncOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            print(f'[DEBUG] OpenAI API Key: {"Есть" if api_key else "НЕТ!"}')
            if not api_key:
                print('[DEBUG] Нет OpenAI API ключа! Создаем базовые рекомендации...')
                # Создаем простые базовые рекомендации без AI
                session.recommendations = [
                    {"sphere": "Отношения с любимыми", "emoji": "💖", "text": "Выделите больше времени на общение с близкими. Планируйте совместные мероприятия."},
                    {"sphere": "Отношения с родными", "emoji": "🏡", "text": "Регулярно звоните родным и интересуйтесь их делами."},
                    {"sphere": "Друзья", "emoji": "🤝", "text": "Инициативно организуйте встречи с друзьями. Поддерживайте связи."},
                    {"sphere": "Карьера", "emoji": "💼", "text": "Определите карьерные цели и составьте план развития навыков."},
                    {"sphere": "Физическое здоровье", "emoji": "🏋️", "text": "Начните с простых упражнений 3 раза в неделю по 30 минут."},
                    {"sphere": "Ментальное здоровье", "emoji": "🧠", "text": "Практикуйте медитацию или дыхательные упражнения."},
                    {"sphere": "Хобби и увлечения", "emoji": "🎨", "text": "Найдите время для любимых занятий хотя бы раз в неделю."},
                    {"sphere": "Благосостояние", "emoji": "💰", "text": "Ведите учет доходов и расходов. Создайте финансовую подушку."}
                ]
                session.ai_recommendations = []
                return
            client = AsyncOpenAI(api_key=api_key)
            print('[DEBUG] Отправляем запрос к OpenAI...')
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            import json
            content = response.choices[0].message.content
            print(f'[DEBUG] OpenAI ответ получен: {content[:200] if content else "НЕТ КОНТЕНТА"}...')
            if content is not None:
                try:
                    print('[DEBUG] Парсим JSON...')
                    data = json.loads(content)
                    print(f'[DEBUG] JSON распарсен: metrics={len(data.get("metrics", []))}, recommendations={len(data.get("recommendations", []))}, ai_recommendations={len(data.get("ai_recommendations", []))}')
                    session.metrics = data.get("metrics", [])
                    session.recommendations = data.get("recommendations", [])
                    session.ai_recommendations = data.get("ai_recommendations", [])
                    
                    # Если базовых рекомендаций нет, создаем их из AI рекомендаций
                    if not session.recommendations and session.ai_recommendations:
                        print('[DEBUG] Создаем базовые рекомендации из AI...')
                        session.recommendations = []
                        for ai_rec in session.ai_recommendations:
                            sphere = ai_rec.get('sphere', '')
                            emoji = ai_rec.get('emoji', '')
                            title = ai_rec.get('title', '')
                            # Создаем краткую версию из заголовка AI рекомендации
                            basic_text = title if title else "Рекомендация по улучшению"
                            session.recommendations.append({
                                "sphere": sphere,
                                "emoji": emoji,
                                "text": basic_text
                            })
                except Exception as e:
                    print(f'[DEBUG] Ошибка парсинга JSON: {e}')
                    fixed = content[:content.rfind('}')] + '}' if content.rfind('}') != -1 else content
                    try:
                        print('[DEBUG] Пробуем исправить JSON...')
                        data = json.loads(fixed)
                        print(f'[DEBUG] Исправленный JSON: metrics={len(data.get("metrics", []))}, recommendations={len(data.get("recommendations", []))}, ai_recommendations={len(data.get("ai_recommendations", []))}')
                        session.metrics = data.get("metrics", [])
                        session.recommendations = data.get("recommendations", [])
                        session.ai_recommendations = data.get("ai_recommendations", [])
                        
                        # Если базовых рекомендаций нет, создаем их из AI рекомендаций
                        if not session.recommendations and session.ai_recommendations:
                            print('[DEBUG] Создаем базовые рекомендации из AI (исправленный JSON)...')
                            session.recommendations = []
                            for ai_rec in session.ai_recommendations:
                                sphere = ai_rec.get('sphere', '')
                                emoji = ai_rec.get('emoji', '')
                                title = ai_rec.get('title', '')
                                # Создаем краткую версию из заголовка AI рекомендации
                                basic_text = title if title else "Рекомендация по улучшению"
                                session.recommendations.append({
                                    "sphere": sphere,
                                    "emoji": emoji,
                                    "text": basic_text
                                })
                    except Exception as e2:
                        print(f'[DEBUG] Вторая ошибка парсинга JSON: {e2}')
                        session.metrics = []
                        session.recommendations = []
                        session.ai_recommendations = []
                        print(f"JSON parse error: {e}\nSecond attempt: {e2}\nOpenAI raw response:\n{content}")
            else:
                session.metrics = []
                session.recommendations = []
                session.ai_recommendations = []
        except Exception as e:
            session.metrics = []
            session.recommendations = []
            session.ai_recommendations = []
            print(f"Error generating recommendations via OpenAI: {e}")

    def _get_sphere_info(self, sphere_raw):
        SPHERE_MAP = {
            "1": ("💖", "Отношения с любимыми"),
            "2": ("🏡", "Отношения с родными"),
            "3": ("🤝", "Друзья"),
            "4": ("💼", "Карьера"),
            "5": ("🏋️", "Физическое здоровье"),
            "6": ("🧠", "Ментальное здоровье"),
            "7": ("🎨", "Хобби и увлечения"),
            "8": ("💰", "Благосостояние"),
            # Английские варианты:
            "romantic relationships": ("💖", "Отношения с любимыми"),
            "family relationships": ("🏡", "Отношения с родными"),
            "friends": ("🤝", "Друзья"),
            "career": ("💼", "Карьера"),
            "physical health": ("🏋️", "Физическое здоровье"),
            "mental health": ("🧠", "Ментальное здоровье"),
            "hobbies and interests": ("🎨", "Хобби и увлечения"),
            "wealth": ("💰", "Благосостояние"),
        }
        key = str(sphere_raw).strip().lower()
        return SPHERE_MAP.get(key, ("•", key))

    def _translate_sphere_name(self, sphere_name, lang='ru'):
        """Переводит название сферы на нужный язык"""
        sphere_translations = {
            # Русские названия
            "отношения с любимыми": "Relationships with loved ones" if lang == 'en' else "отношения с любимыми",
            "отношения с родными": "Family relationships" if lang == 'en' else "отношения с родными",
            "друзья": "Friends" if lang == 'en' else "друзья",
            "карьера": "Career" if lang == 'en' else "карьера",
            "физическое здоровье": "Physical health" if lang == 'en' else "физическое здоровье",
            "ментальное здоровье": "Mental health" if lang == 'en' else "ментальное здоровье",
            "хобби и увлечения": "Hobbies and interests" if lang == 'en' else "хобби и увлечения",
            "благосостояние": "Well-being" if lang == 'en' else "благосостояние",
            # Английские названия
            "relationships with loved ones": "Relationships with loved ones" if lang == 'en' else "отношения с любимыми",
            "family relationships": "Family relationships" if lang == 'en' else "отношения с родными",
            "friends": "Friends" if lang == 'en' else "друзья",
            "career": "Career" if lang == 'en' else "карьера",
            "physical health": "Physical health" if lang == 'en' else "физическое здоровье",
            "mental health": "Mental health" if lang == 'en' else "ментальное здоровье",
            "hobbies and interests": "Hobbies and interests" if lang == 'en' else "хобби и увлечения",
            "well-being": "Well-being" if lang == 'en' else "благосостояние",
        }
        return sphere_translations.get(sphere_name.lower(), sphere_name)

    # ... (сюда можно добавить остальные методы класса, если нужно восстановить полный функционал)

    def format_recommendations(self, recs, lang='ru', sphere_scores=None):
        texts = LOCALES[lang]
        sphere_names = [
            ('💖', 'Отношения с любимыми', 'Relationships with loved ones'),
            ('🏡', 'Отношения с родными', 'Family relationships'),
            ('🤝', 'Друзья', 'Friends'),
            ('💼', 'Карьера', 'Career'),
            ('🏋️', 'Физическое здоровье', 'Physical health'),
            ('🧠', 'Ментальное здоровье', 'Mental health'),
            ('🎨', 'Хобби и увлечения', 'Hobbies and interests'),
            ('💰', 'Благосостояние', 'Well-being'),
        ]
        
        if not recs:
            return f"<b>{texts.get('basic_recs', 'Базовые рекомендации')}</b>\n\n<i>{texts.get('recommendations_will_be_generated', 'Рекомендации будут сгенерированы после прохождения полного теста.')}</i>"
        
        lines = [f"<b>{texts.get('basic_recs', 'Базовые рекомендации')}</b>\n"]
        
        # Если recs - это список
        if isinstance(recs, list):
            for rec in recs:
                sphere_name = rec.get('sphere', '')
                emoji = rec.get('emoji', '')
                # Переводим название сферы
                translated_sphere = self._translate_sphere_name(sphere_name, lang)
                score = None
                if sphere_scores and isinstance(sphere_scores, dict):
                    # Ищем балл по русскому или английскому названию
                    score = sphere_scores.get(sphere_name) or sphere_scores.get(translated_sphere)
                score_str = f"<b>{score}</b>" if score is not None else "—"
                rec_text = rec.get('text') or rec.get('title') or str(rec)
                lines.append(f"{emoji} <b>{translated_sphere}</b> — {score_str}")
                lines.append(f"💡 {rec_text}")
                lines.append("━━━━━━━━━━━━━━")
        # Если recs - это словарь
        elif isinstance(recs, dict):
            for i, (sphere_key, rec) in enumerate(recs.items()):
                if i >= len(sphere_names):
                    break
                emoji, ru, en = sphere_names[i]
                sphere = ru if lang == 'ru' else en
                score = None
                if sphere_scores and isinstance(sphere_scores, dict):
                    score = sphere_scores.get(ru) or sphere_scores.get(en)
                score_str = f"<b>{score}</b>" if score is not None else "—"
                rec_text = rec.get('text') or rec.get('title') or str(rec)
                lines.append(f"{emoji} <b>{sphere}</b> — {score_str}")
                lines.append(f"💡 {rec_text}")
                lines.append("━━━━━━━━━━━━━━")
        else:
            lines.append(f"<i>Нет данных для рекомендаций.</i>")
            
        return "\n".join(lines)

    def format_ai_recommendations(self, ai, lang='ru', sphere_scores=None):
        texts = LOCALES[lang]
        sphere_names = [
            ('💖', 'Отношения с любимыми', 'Relationships with loved ones'),
            ('🏡', 'Отношения с родными', 'Family relationships'),
            ('🤝', 'Друзья', 'Friends'),
            ('💼', 'Карьера', 'Career'),
            ('🏋️', 'Физическое здоровье', 'Physical health'),
            ('🧠', 'Ментальное здоровье', 'Mental health'),
            ('🎨', 'Хобби и увлечения', 'Hobbies and interests'),
            ('💰', 'Благосостояние', 'Well-being'),
        ]
        
        if not ai:
            return f"<b>{texts.get('ai_recs', 'AI рекомендации')}</b>\n\n<i>{texts.get('recommendations_will_be_generated', 'AI рекомендации будут сгенерированы после прохождения полного теста.')}</i>"
        
        lines = [f"<b>{texts.get('ai_recs', 'AI рекомендации')}</b>\n"]
        
        # Если ai - это список
        if isinstance(ai, list):
            for rec in ai:
                sphere_name = rec.get('sphere', '')
                emoji = rec.get('emoji', '')
                # Переводим название сферы
                translated_sphere = self._translate_sphere_name(sphere_name, lang)
                score = None
                if sphere_scores and isinstance(sphere_scores, dict):
                    # Ищем балл по русскому или английскому названию
                    score = sphere_scores.get(sphere_name) or sphere_scores.get(translated_sphere)
                score_str = f"<b>{score}</b>" if score is not None else "—"
                
                # Получаем данные рекомендации
                title = rec.get('title') or rec.get('text') or str(rec)
                desc = rec.get('desc', '') or rec.get('description', '')
                steps = rec.get('steps', '') or rec.get('action_steps', '')
                
                # Форматируем с разделителями
                lines.append(f"{emoji} <b>{translated_sphere}</b> — {score_str}")
                lines.append(f"🎯 <b>{title}</b>")
                if desc:
                    lines.append(f"📝 {desc}")
                if steps:
                    # Разбиваем шаги на отдельные строки для лучшего отображения
                    steps_lines = steps.split('\\n') if '\\n' in steps else [steps]
                    for step in steps_lines:
                        if step.strip():
                            lines.append(f"➡️ {step.strip()}")
                lines.append("━━━━━━━━━━━━━━")
        # Если ai - это словарь
        elif isinstance(ai, dict):
            for i, (sphere_key, rec) in enumerate(ai.items()):
                if i >= len(sphere_names):
                    break
                emoji, ru, en = sphere_names[i]
                sphere = ru if lang == 'ru' else en
                score = None
                if sphere_scores and isinstance(sphere_scores, dict):
                    score = sphere_scores.get(ru) or sphere_scores.get(en)
                score_str = f"<b>{score}</b>" if score is not None else "—"
                
                # Получаем данные рекомендации
                title = rec.get('title') or rec.get('text') or str(rec)
                desc = rec.get('desc', '') or rec.get('description', '')
                steps = rec.get('steps', '') or rec.get('action_steps', '')
                
                # Форматируем с разделителями
                lines.append(f"{emoji} <b>{sphere}</b> — {score_str}")
                lines.append(f"🎯 <b>{title}</b>")
                if desc:
                    lines.append(f"📝 {desc}")
                if steps:
                    # Разбиваем шаги на отдельные строки для лучшего отображения
                    steps_lines = steps.split('\\n') if '\\n' in steps else [steps]
                    for step in steps_lines:
                        if step.strip():
                            lines.append(f"➡️ {step.strip()}")
                lines.append("━━━━━━━━━━━━━━")
        else:
            lines.append(f"<i>Нет данных для AI рекомендаций.</i>")
            
        return "\n".join(lines) 