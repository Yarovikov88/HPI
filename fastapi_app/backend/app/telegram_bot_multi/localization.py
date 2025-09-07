# src/telegram_bot_multi/localization.py

from src.telegram_bot_multi.questions import QuestionsManager

LOCALES = {
    'ru': {
        'welcome': (
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
        ),
        'help': (
            "📚 <b>Как работает HPI Bot:</b>\n\n"
            "1️⃣ <b>Опрос</b> - ответите на 48 вопросов (6 по каждой сфере)\n"
            "2️⃣ <b>Расчет</b> - система рассчитает ваш Human Performance Index\n"
            "3️⃣ <b>Анализ</b> - получите диаграммы и рекомендации\n\n"
            "⏱️ <b>Время прохождения:</b> 10-15 минут\n"
            "💾 <b>Данные:</b> сохраняются локально для анализа трендов\n\n"
            "🎯 <b>Цель:</b> помочь вам увидеть баланс жизни и найти области для улучшения"
        ),
        'start_survey': "🚀 Начать опрос",
        'how_it_works': "ℹ️ Как это работает",
        'questions_manager': lambda: QuestionsManager('ru'),
        'choose_language': 'Пожалуйста, выберите язык:',
        'change_language': '🌐 Сменить язык',
        'progress': 'Вопрос {current} из {total}',
        'pro_invite': '🎯 <b>Отлично! Основной опрос завершён.</b>\n\nТеперь вы можете пройти дополнительную PRO-часть для более глубокого анализа.\n\nPRO-часть включает:\n• Детальные проблемы по каждой сфере\n• Конкретные цели и метрики\n• Блокеры и достижения\n\nХотите пройти PRO-часть?',
        'button_pressed': 'Нажата кнопка: {button}',
        'pro_help': '📝 <b>Как отвечать на PRO-вопросы:</b>\n\n1️⃣ <b>Отвечайте по порядку</b> - каждый вопрос на новой строке\n2️⃣ <b>Будьте конкретны</b> - описывайте реальные ситуации\n3️⃣ <b>Используйте числа</b> для оценки серьёзности (1-10)\n4️⃣ <b>Указывайте даты</b> когда заметили проблему\n\n💡 <b>Пример ответа:</b>\nНедостаток времени на общение\nАктивна\n7\n2 месяца назад',
        'error': '❌ Произошла ошибка: {error}',
        'pro_thanks': '✅ Спасибо за ответ! Переходим к следующему вопросу...',
        'trend': '📈 Тренд',
        'radar': '📊 Радар',
        'menu_full': '📝 Пройти полный тест',
        'menu_pro': '🧩 Только PRO-часть',
        'menu_dashboard': '📊 Мой дашборд',
        'menu_answers': '📋 Мои ответы',
        'menu': 'Выберите действие из меню:',
        'dashboard_basic': 'Ваш HPI: {hpi}\n\n{note}',
        'basic_recs': '📝 Базовые рекомендации',
        'ai_recs': '🤖 AI-рекомендации',
        'dashboard_full': '<b>HPI человека (Полная версия)</b>\n\nТекущий HPI: <b>{hpi}</b>\n\nВы прошли расширенную часть опроса! Теперь у вас есть доступ к полным данным.\n\nВыберите раздел для просмотра подробностей:',
        'dashboard_basic': '<b>HPI человека (Базовая версия)</b>\n\nТекущий HPI: <b>{hpi}</b>\n\nВы завершили базовый опрос. Разделы ПРО будут пустыми, так как вы не прошли расширенную часть.\n\nВыберите раздел для просмотра подробностей:',
        'trend': '📈 Динамика HPI',
        'radar': '⚖️ Баланс по сферам',
        'problems': '🔴 Мои проблемы',
        'goals': '🎯 Мои цели',
        'blockers': '⛔ Мои блокеры',
        'metrics': '📊 Мои метрики',
        'basic_recs': '💡 Базовые рекомендации',
        'ai_recs_button': '�� AI рекомендации',
        'pro_too_many': "Вы ввели {got} ответов, а нужно {need}. Лишние: {fields}",
        'pro_too_few': "Вы ввели {got} ответов, а нужно {need}. Не хватает: {fields}",
        'pro_help_no_data': "Нет данных для текущего PRO-вопроса. Попробуйте ещё раз.",
        'problems': "Проблемы",
        'goals': "Цели",
        'blockers': "Барьеры",
        'metrics': "Метрики",
        'pro_sections': "ПРО РАЗДЕЛЫ",
        'recommendations_will_be_generated': "Рекомендации будут сгенерированы после прохождения полного теста.",
        'achievement_description': "Описание достижения",
        'achievement_impact_areas': "Сферы, на которые это повлияло",
        'survey_start': "🚀 Начинаем опрос! Ответьте на 48 вопросов для анализа ваших сфер жизни.",
        'survey_complete': "✅ Опрос завершен! Теперь вы можете посмотреть результаты в дашборде.",
        'pro_start': "🎯 Начинаем PRO-опрос! Опишите детально ваши проблемы, цели и блокеры.",
        'pro_complete': "✅ PRO-опрос завершен! Теперь у вас есть полные данные для анализа.",
        'pro_question': "PRO-вопрос",
        'back': "Назад",
    },
    'en': {
        'welcome': (
            "🎯 <b>Welcome to HPI Bot!</b>\n\n"
            "I will help you analyze your life spheres and get personalized recommendations.\n\n"
            "📊 <b>What we will assess:</b>\n"
            "💖 Relationships with loved ones\n"
            "🏡 Family relationships\n"
            "🤝 Friends\n"
            "💼 Career\n"
            "♂️ Physical health\n"
            "🧠 Mental health\n"
            "🎨 Hobbies and interests\n"
            "💰 Well-being\n\n"
            "Ready to start the analysis?"
        ),
        'help': (
            "📚 <b>How HPI Bot works:</b>\n\n"
            "1️⃣ <b>Survey</b> - answer 48 questions (6 for each sphere)\n"
            "2️⃣ <b>Calculation</b> - the system will calculate your Human Performance Index\n"
            "3️⃣ <b>Analysis</b> - you will get diagrams and recommendations\n\n"
            "⏱️ <b>Time required:</b> 10-15 minutes\n"
            "💾 <b>Data:</b> stored locally for trend analysis\n\n"
            "🎯 <b>Goal:</b> help you see your life balance and find areas for improvement"
        ),
        'start_survey': "🚀 Start survey",
        'how_it_works': "ℹ️ How it works",
        'questions_manager': lambda: QuestionsManager('en'),
        'choose_language': 'Please choose your language:',
        'change_language': '🌐 Change language',
        'progress': 'Question {current} of {total}',
        'pro_invite': '🎯 <b>Great! The main survey is completed.</b>\n\nNow you can take an additional PRO section for deeper analysis.\n\nThe PRO section includes:\n• Detailed problems for each sphere\n• Specific goals and metrics\n• Blockers and achievements\n\nWould you like to take the PRO section?',
        'button_pressed': 'Button pressed: {button}',
        'pro_help': '📝 <b>How to answer PRO questions:</b>\n\n1️⃣ <b>Answer in order</b> - each question on a new line\n2️⃣ <b>Be specific</b> - describe real situations\n3️⃣ <b>Use numbers</b> for seriousness assessment (1-10)\n4️⃣ <b>Indicate dates</b> when you noticed the problem\n\n💡 <b>Example answer:</b>\nLack of time for communication\nActive\n7\n2 months ago',
        'error': '❌ An error occurred: {error}',
        'pro_thanks': '✅ Thank you for your answer! Moving to the next question...',
        'trend': '📈 Trend',
        'radar': '📊 Radar',
        'menu_full': '📝 Take full test',
        'menu_pro': '🧩 PRO section only',
        'menu_dashboard': '📊 My dashboard',
        'menu_answers': '📋 My answers',
        'menu': 'Choose an action from the menu:',
        'dashboard_basic': 'Your HPI: {hpi}\n\n{note}',
        'basic_recs': '📝 Basic recommendations',
        'ai_recs': '🤖 AI recommendations',
        'dashboard_full': '<b>HPI (Full version)</b>\n\nCurrent HPI: <b>{hpi}</b>\n\nYou have completed the extended survey! Now you have access to full data.\n\nChoose a section to view details:',
        'dashboard_basic': '<b>HPI (Basic version)</b>\n\nCurrent HPI: <b>{hpi}</b>\n\nYou have completed the basic survey. PRO sections will be empty as you have not completed the extended part.\n\nChoose a section to view details:',
        'trend': '📈 HPI Trend',
        'radar': '⚖️ Sphere balance',
        'problems': '🔴 My problems',
        'goals': '🎯 My goals',
        'blockers': '⛔ My blockers',
        'metrics': '📊 My metrics',
        'basic_recs': '💡 Basic recommendations',
        'ai_recs_button': '🤖 AI recommendations',
        'pro_too_many': "You entered {got} answers, but {need} required. Extra: {fields}",
        'pro_too_few': "You entered {got} answers, but {need} required. Missing: {fields}",
        'pro_help_no_data': "No data for the current PRO question. Please try again.",
        'problems': "Problems",
        'goals': "Goals",
        'blockers': "Blockers",
        'metrics': "Metrics",
        'achievements': "Achievements",
        'hide': "Hide",
        'pro_sections': "PRO SECTIONS",
        'recommendations_will_be_generated': "Recommendations will be generated after completing the full test.",
        'achievement_description': "Achievement description",
        'achievement_impact_areas': "Areas that this affected",
        'survey_start': "🚀 Starting the survey! Answer 48 questions to analyze your life spheres.",
        'survey_complete': "✅ Survey completed! Now you can view results in the dashboard.",
        'pro_start': "🎯 Starting PRO survey! Describe in detail your problems, goals and blockers.",
        'pro_complete': "✅ PRO survey completed! Now you have full data for analysis.",
        'pro_question': "PRO question",
        'back': "Back",
    }
} 