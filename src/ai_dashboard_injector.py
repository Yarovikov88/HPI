"""
HPI AI Dashboard Injector
Генерирует файл AI_Recommendations.md с актуальными рекомендациями для дашборда HPI.
"""
import locale
import os
import re
from datetime import datetime
from ai_recommendations import HPIRecommendationEngine
import random
import sys
from typing import Dict, List, Optional
import logging
from trend import generate_trend_chart
import json

# --- Принудительное использование UTF-8 ---
try:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except locale.Error:
    print("Warning: Could not set locale to C.UTF-8. Emoji support might be limited.")
# --- Конец принудительного использования UTF-8 ---

# --- КОНФИГУРАЦИЯ ---
# Абсолютные пути от корня проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(PROJECT_ROOT, 'reports_draft')
INTERFACES_DIR = os.path.join(PROJECT_ROOT, 'interfaces')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
REPORTS_FINAL_DIR = os.path.join(PROJECT_ROOT, 'reports_final')

# Конфигурация сфер, чтобы гарантировать порядок и наличие всех данных
SPHERES_CONFIG = [
    {"key": "Отношения с любимыми", "emoji": "💖"},
    {"key": "Отношения с родными", "emoji": "🏡"},
    {"key": "Друзья", "emoji": "🤝"},
    {"key": "Карьера", "emoji": "💼"},
    {"key": "Физическое здоровье", "emoji": "♂️"},
    {"key": "Ментальное здоровье", "emoji": "🧠"},
    {"key": "Хобби и увлечения", "emoji": "🎨"},
    {"key": "Благосостояние", "emoji": "💰"}
]

def parse_questions_database() -> Dict[str, List[str]]:
    """
    Парсит файл questions.md и извлекает все стандартные метрики для каждой сферы.
    Возвращает словарь, где ключ - название сферы, а значение - список названий метрик.
    """
    db_path = os.path.join(PROJECT_ROOT, 'database', 'questions.md')
    if not os.path.exists(db_path):
        logging.error(f"Файл базы данных вопросов не найден: {db_path}")
        return {}

    with open(db_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sphere_metrics = {}
    
    # Регулярное выражение для поиска JSON-блоков для каждой сферы
    # Ищет заголовок типа "## 💖 Отношения с любимыми" и следующий за ним блок ```json ... ```
    pattern = re.compile(r"##\s*(?P<emoji>[\U0001F000-\U0001FA95\s\S]+?)\s*(?P<name>.*?)\n```json\n([\s\S]+?)\n```", re.DOTALL)

    matches = pattern.finditer(content)
    
    for match in matches:
        sphere_name = match.group('name').strip()
        json_content = match.group(3)

        try:
            data = json.loads(json_content)
            for item in data:
                if item.get("category") == "metrics" and "metrics" in item:
                    # Собираем имена всех метрик для данной сферы
                    metric_names = [m.get("name") for m in item["metrics"] if m.get("name")]
                    if sphere_name in [s['key'] for s in SPHERES_CONFIG]:
                        sphere_metrics[sphere_name] = metric_names
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка декодирования JSON для сферы '{sphere_name}': {e}")
            continue
            
    logging.info(f"Из базы данных загружены стандартные метрики для {len(sphere_metrics)} сфер.")
    return sphere_metrics

# --- УТИЛИТЫ ---

def get_score_emoji(score: float, is_hpi: bool = False) -> str:
    """Конвертирует оценку в emoji-индикатор."""
    if is_hpi:
        if score >= 80: return "🟢"
        if score >= 60: return "🔵"
        if score >= 40: return "🟡"
        return "🔴"
    else:
        if score >= 8.0: return "🟢"
        if score >= 6.0: return "🔵"
        if score >= 4.0: return "🟡"
        return "🔴"

def collect_reports_history() -> List[Dict]:
    """
    Собирает историю HPI и оценок по сферам из всех финальных отчетов.
    Возвращает список словарей, каждый из которых представляет один отчет.
    """
    history = []
    if not os.path.exists(REPORTS_FINAL_DIR):
        logging.error(f"Папка с финальными отчетами не найдена: {REPORTS_FINAL_DIR}")
        return []

    report_files = [f for f in os.listdir(REPORTS_FINAL_DIR) if f.endswith("_report.md")]
    logging.info(f"Найдено {len(report_files)} отчетов для сбора истории.")

    for filename in report_files:
        try:
            date_str = filename.split('_')[0]
            report_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            filepath = os.path.join(REPORTS_FINAL_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            report_data = {'date': report_date, 'scores': {}}

            hpi_match = re.search(r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*([\d\.]+)\*\*\s*\|', content)
            if hpi_match:
                report_data['hpi'] = float(hpi_match.group(1))
            
            for sphere in SPHERES_CONFIG:
                pattern = rf"\| {re.escape(sphere['key'])} \| ([\d\.]+) \|"
                match = re.search(pattern, content)
                if match:
                    report_data['scores'][sphere['key']] = float(match.group(1))

            if 'hpi' in report_data:
                history.append(report_data)
            else:
                logging.warning(f"Не удалось найти HPI в отчете: {filename}")
        except Exception as e:
            logging.error(f"Ошибка при обработке отчета {filename} для истории: {e}")
            continue
    
    history.sort(key=lambda x: x['date'])
    logging.info(f"Собрано {len(history)} записей в истории.")
    return history

def normalize_sphere_name(name):
    """
    Убираем эмодзи, пробелы и приводим к нижнему регистру.
    """
    # Убираем эмодзи (они обычно занимают 2 байта)
    name = ''.join(c for c in name if len(c.encode('utf-8')) == 1)
    # Убираем пробелы и приводим к нижнему регистру
    return name.strip().lower()

class HPIRecommendationEngine:
    def __init__(self):
        self._emoji_to_sphere = {
            "💖": "Отношения с любимыми",
            "🏡": "Отношения с родными",
            "🤝": "Друзья",
            "💼": "Карьера",
            "♂️": "Физическое здоровье",
            "🧠": "Ментальное здоровье",
            "🎨": "Хобби и увлечения",
            "💰": "Благосостояние"
        }
        self._sphere_to_emoji = {v: k for k, v in self._emoji_to_sphere.items()}

    def _extract_sphere_values(self, report_content: str) -> Dict[str, float]:
        """
        Извлекает значения сфер из отчета.
        Возвращает словарь {сфера: значение}.
        """
        sphere_values = {}
        
        # Ищем строки с эмодзи и значениями
        pattern = r'([💖🏡🤝💼♂️🧠🎨💰])\s+([^:]+):\s+(\d+\.\d+)\s+[🟢🟡🔴]'
        matches = re.finditer(pattern, report_content)
        
        for match in matches:
            emoji = match.group(1)
            sphere = match.group(2).strip()
            value = float(match.group(3))
            
            # Преобразуем эмодзи в ключ сферы
            sphere_key = self._emoji_to_sphere.get(emoji)
            if sphere_key:
                sphere_values[sphere_key] = value
                logging.info(f"[AI DASHBOARD] Найдено значение для сферы {sphere_key}: {value}")
        
        if not sphere_values:
            logging.warning("[AI DASHBOARD] Не удалось извлечь значения сфер из отчета")
            
        return sphere_values

    def generate_recommendations(self, pro_data: Dict, report_content: str) -> Dict[str, str]:
        """
        Генерирует рекомендации на основе PRO-данных и значений сфер из отчета.
        """
        sphere_values = self._extract_sphere_values(report_content)
        logging.info(f"[AI DASHBOARD] sphere_values (из отчёта): {sphere_values}")
        
        recommendations = {}
        for sphere_config in SPHERES_CONFIG:
            sphere = sphere_config['key']
            emoji = sphere_config['emoji']
            
            # Получаем данные для сферы
            problem = pro_data.get('Мои проблемы', {}).get(sphere, 'Нет данных')
            goal = pro_data.get('Мои цели', {}).get(sphere, 'Нет данных')
            blocker = pro_data.get('Мои блокеры', {}).get(sphere, 'Нет данных')
            value = sphere_values.get(sphere, 0.0)
            
            # Генерируем рекомендацию
            recommendation = self._generate_sphere_recommendation(sphere, problem, goal, blocker, value)
            recommendations[sphere] = f"> | {emoji} | {recommendation} |"
            logging.info(f"[AI DASHBOARD] Итоговая строка: {recommendations[sphere]}")
        
        return recommendations

    def _generate_sphere_recommendation(self, sphere: str, problem: str, goal: str, blocker: str, value: float) -> str:
        """
        Генерирует рекомендацию для конкретной сферы на основе всех доступных данных.
        """
        if problem != 'Нет данных':
            if 'редко' in problem.lower():
                return f"Вы указали, что {problem.lower()}. Попробуйте запланировать регулярную встречу или звонок."
            elif 'выгорание' in problem.lower():
                return "Для борьбы с выгоранием важно найти баланс между работой и отдыхом. Начните с коротких перерывов каждые 2 часа."
            elif 'апатия' in problem.lower() or 'фокус' in problem.lower():
                return "Для улучшения концентрации попробуйте технику помодоро: 25 минут работы, 5 минут отдыха."
            elif 'расход' in problem.lower():
                return "Создайте таблицу учета расходов и ведите её ежедневно. Это поможет лучше контролировать траты."
        
        if goal != 'Нет данных':
            if 'отпуск' in goal.lower():
                return "Для планирования отпуска начните с составления бюджета и выбора примерных дат."
            elif 'звонить' in goal.lower() or 'звонки' in goal.lower():
                return "Внесите регулярные звонки в календарь и поставьте напоминания."
            elif 'встреч' in goal.lower():
                return "Создайте групповой чат или событие, чтобы согласовать удобное для всех время."
            elif 'работу' in goal.lower():
                return "Для поиска новой работы обновите резюме и начните ежедневно просматривать вакансии на 1-2 площадках."
            elif 'бежать' in goal.lower() or 'км' in goal.lower():
                return "Начните с небольших пробежек по 1-2 км, постепенно увеличивая дистанцию."
            elif 'курс' in goal.lower() or 'медитац' in goal.lower():
                return "Выделите в календаре конкретное время для занятий и создайте комфортное пространство."
            elif 'мастер' in goal.lower() or 'класс' in goal.lower():
                return "Исследуйте доступные мастер-классы онлайн и офлайн, составьте список интересных вариантов."
            elif 'доход' in goal.lower() or 'отклад' in goal.lower():
                return "Настройте автоматическое перечисление части зарплаты на сберегательный счет."
        
        if blocker != 'Нет данных':
            if 'время' in blocker.lower():
                return "Проведите аудит своего времени в течение недели, чтобы найти возможности для оптимизации."
            elif 'устал' in blocker.lower():
                return "Попробуйте перенести важные дела на утро, когда уровень энергии выше."
            elif 'страх' in blocker.lower() or 'неувер' in blocker.lower():
                return "Составьте список своих достижений и сильных сторон. Это поможет укрепить уверенность."
            elif 'лень' in blocker.lower():
                return "Используйте технику 'двух минут': начните с совсем небольшого действия."
            elif 'прокрастинац' in blocker.lower():
                return "Разбейте большую задачу на маленькие, легко выполнимые шаги."
            elif 'инфляц' in blocker.lower():
                return "Проанализируйте свои расходы и найдите возможности для оптимизации бюджета."
        
        # Базовые рекомендации по сферам
        base_recommendations = {
            "Отношения с любимыми": "Уделите время качественному общению. Запланируйте совместное мероприятие или романтический вечер.",
            "Отношения с родными": "Поддерживайте регулярный контакт с семьей. Запланируйте еженедельные звонки или встречи.",
            "Друзья": "Организуйте встречу с друзьями или онлайн-созвон для поддержания связи.",
            "Карьера": "Проанализируйте свои профессиональные цели и составьте план развития на ближайшие месяцы.",
            "Физическое здоровье": "Начните с простых привычек: утренняя зарядка, прогулки, правильное питание.",
            "Ментальное здоровье": "Выделите время на отдых и восстановление. Практикуйте техники релаксации.",
            "Хобби и увлечения": "Исследуйте новые интересы и найдите занятие, которое приносит удовольствие.",
            "Благосостояние": "Создайте финансовый план и начните вести учет доходов и расходов."
        }
        
        return base_recommendations.get(sphere, "Установите конкретные цели и отслеживайте прогресс.")

def find_latest_draft() -> str | None:
    """Находит последний по дате изменения черновик в папке."""
    logging.info("Поиск последнего черновика...")
    if not os.path.exists(DRAFTS_DIR):
        logging.error(f"Папка с черновиками не найдена: {DRAFTS_DIR}")
        return None
    
    drafts = [os.path.join(DRAFTS_DIR, f) for f in os.listdir(DRAFTS_DIR) if f.endswith("_draft.md")]
    if not drafts:
        logging.error("Черновики не найдены в директории: %s", DRAFTS_DIR)
        return None
    
    logging.info(f"Найдено {len(drafts)} черновиков. Выбираем последний...")
    latest_draft = max(drafts, key=os.path.getmtime)
    logging.info(f"Выбран черновик: {latest_draft}")
    return latest_draft

def parse_pro_data(md_content: str) -> Dict[str, Dict[str, str]]:
    """
    Извлекает все PRO-данные из черновика.
    Возвращает словарь, где ключ - название секции.
    Для обычных секций значение - словарь {сфера: ответ}.
    Для 'Мои метрики' значение - список словарей [{'sphere': сфера, 'metric': метрика, ...}].
    """
    logging.info("Начало парсинга PRO-секций из черновика.")
    pro_sections = ['Мои проблемы', 'Мои цели', 'Мои блокеры', 'Мои достижения', 'Мои метрики']
    all_pro_data = {}

    # Создаем словарь для быстрого поиска эмодзи по названию сферы
    emoji_map = {config['key']: config['emoji'] for config in SPHERES_CONFIG}
    # Создаем обратный словарь для поиска ключа по эмодзи
    emoji_to_key = {config['emoji']: config['key'] for config in SPHERES_CONFIG}

    for section_title in pro_sections:
        logging.debug(f"Поиск секции: '{section_title}'")
        lines = md_content.split('\n')
        
        for i, line in enumerate(lines):
            if section_title in line and line.strip().startswith('###'):
                logging.debug(f"Найдена строка с заголовком секции: '{line.strip()}'")
                
                # Специальная обработка для 'Мои метрики'
                if section_title == 'Мои метрики':
                    metrics_data = []
                    for table_line in lines[i+1:]:
                        if table_line.strip().startswith('###'): break
                        if not table_line.strip().startswith('|'): continue
                        
                        parts = [p.strip() for p in table_line.split('|') if p.strip()]
                        if len(parts) >= 4 and '---' not in parts[0]:
                            sphere_candidate = parts[0]
                            # Ищем, к какой сфере относится строка
                            for config in SPHERES_CONFIG:
                                if config['key'] in sphere_candidate or config['emoji'] in sphere_candidate:
                                    metrics_data.append({
                                        'sphere': config['key'],  # Здесь оставляем ключ для внутренней логики
                                        'metric': parts[1],
                                        'current': parts[2],
                                        'target': parts[3]
                                    })
                                    break
                    all_pro_data[section_title] = metrics_data
                    logging.info(f"Для секции '{section_title}' извлечены метрики: {metrics_data}")
                else:
                    # Стандартная обработка для остальных секций
                    section_data = {}
                    current_sphere_key = None
                    for table_line in lines[i+1:]:
                        if table_line.strip().startswith('###'): break
                        if not table_line.strip().startswith('|'): continue

                        parts = [p.strip() for p in table_line.split('|') if p.strip()]
                        if len(parts) >= 2:
                            sphere_candidate = parts[0]
                            answer = parts[1]
                            final_answer = answer if answer and answer.lower() not in ['нет', ''] else "Нет данных"

                            # Проверяем, новая ли это сфера
                            found_sphere = False
                            # Сначала проверяем эмодзи
                            for emoji in emoji_to_key:
                                if emoji in sphere_candidate:
                                    current_sphere_key = emoji_to_key[emoji]
                                    section_data[current_sphere_key] = final_answer
                                    found_sphere = True
                                    break
                            
                            # Если эмодзи не найден, ищем по названию сферы
                            if not found_sphere:
                                normalized_candidate = normalize_sphere_name(sphere_candidate)
                                for config in SPHERES_CONFIG:
                                    if normalize_sphere_name(config['key']) in normalized_candidate:
                                        current_sphere_key = config['key']
                                        section_data[current_sphere_key] = final_answer
                                        found_sphere = True
                                        break
                            
                            # Если сфера не найдена в первой колонке, используем предыдущую
                            if not found_sphere and current_sphere_key and section_data.get(current_sphere_key) != "Нет данных":
                               section_data[current_sphere_key] += f"\\n{final_answer}"

                    all_pro_data[section_title] = section_data
                    logging.info(f"Для секции '{section_title}' извлечены следующие данные: {section_data}")
                
                break
    
    logging.info(f"Парсинг PRO-секций завершен.")
    return all_pro_data

def get_latest_report() -> Optional[str]:
    """
    Находит путь к последнему финальному отчету.
    """
    reports_dir = os.path.join(PROJECT_ROOT, 'reports_final')
    if not os.path.exists(reports_dir):
        return None
    
    reports = [f for f in os.listdir(reports_dir) if f.endswith('_report.md')]
    if not reports:
        return None
    
    latest_report = max(reports)
    return os.path.join(reports_dir, latest_report)

def generate_dummy_recommendations(pro_data: Dict) -> Dict[str, str]:
    """
    Генерирует 'фальшивые' AI-рекомендации на основе PRO-данных.
    Это временная заглушка до реализации полноценного AI-модуля.
    """
    recommendations = {}
    
    # Получаем данные из PRO-секций
    problems = pro_data.get('Мои проблемы', {})
    goals = pro_data.get('Мои цели', {})
    blockers = pro_data.get('Мои блокеры', {})
    metrics = {m['sphere']: m for m in pro_data.get('Мои метрики', [])}
    
    # Для каждой сферы из конфигурации
    for sphere_config in SPHERES_CONFIG:
        sphere = sphere_config['key']
        problem = problems.get(sphere)
        goal = goals.get(sphere)
        blocker = blockers.get(sphere)
        metric = metrics.get(sphere)
        
        # Если есть какие-то данные для сферы
        if problem != 'Нет данных' or goal or blocker != 'Нет данных' or metric:
            recommendation = ""
            
            # Анализируем проблему
            if problem and problem != 'Нет данных':
                if 'редко' in problem.lower():
                    recommendation = f"Вы указали, что {problem.lower()}. Попробуйте запланировать регулярную встречу или звонок."
                elif 'выгорание' in problem.lower():
                    recommendation = "Для борьбы с выгоранием важно найти баланс между работой и отдыхом. Начните с коротких перерывов каждые 2 часа."
                elif 'апатия' in problem.lower() or 'фокус' in problem.lower():
                    recommendation = "Для улучшения концентрации попробуйте технику помодоро: 25 минут работы, 5 минут отдыха."
                elif 'расход' in problem.lower():
                    recommendation = "Создайте таблицу учета расходов и ведите её ежедневно. Это поможет лучше контролировать траты."
            
            # Анализируем цель
            if not recommendation and goal:
                if 'отпуск' in goal.lower():
                    recommendation = "Для планирования отпуска начните с составления бюджета и выбора примерных дат."
                elif 'звонить' in goal.lower() or 'звонки' in goal.lower():
                    recommendation = "Внесите регулярные звонки в календарь и поставьте напоминания."
                elif 'встреч' in goal.lower():
                    recommendation = "Создайте групповой чат или событие, чтобы согласовать удобное для всех время."
                elif 'работу' in goal.lower():
                    recommendation = "Для поиска новой работы обновите резюме и начните ежедневно просматривать вакансии на 1-2 площадках."
                elif 'бежать' in goal.lower() or 'км' in goal.lower():
                    recommendation = "Начните с небольших пробежек по 1-2 км, постепенно увеличивая дистанцию."
                elif 'курс' in goal.lower() or 'медитац' in goal.lower():
                    recommendation = "Выделите в календаре конкретное время для занятий и создайте комфортное пространство."
                elif 'мастер' in goal.lower() or 'класс' in goal.lower():
                    recommendation = "Исследуйте доступные мастер-классы онлайн и офлайн, составьте список интересных вариантов."
                elif 'доход' in goal.lower() or 'отклад' in goal.lower():
                    recommendation = "Настройте автоматическое перечисление части зарплаты на сберегательный счет."
            
            # Анализируем блокер
            if not recommendation and blocker and blocker != 'Нет данных':
                if 'время' in blocker.lower():
                    recommendation = "Проведите аудит своего времени в течение недели, чтобы найти возможности для оптимизации."
                elif 'устал' in blocker.lower():
                    recommendation = "Попробуйте перенести важные дела на утро, когда уровень энергии выше."
                elif 'страх' in blocker.lower() or 'неувер' in blocker.lower():
                    recommendation = "Составьте список своих достижений и сильных сторон. Это поможет укрепить уверенность."
                elif 'лень' in blocker.lower():
                    recommendation = "Используйте технику 'двух минут': начните с совсем небольшого действия."
                elif 'прокрастинац' in blocker.lower():
                    recommendation = "Разбейте большую задачу на маленькие, легко выполнимые шаги."
                elif 'инфляц' in blocker.lower():
                    recommendation = "Проанализируйте свои расходы и найдите возможности для оптимизации бюджета."
            
            # Анализируем метрики
            if not recommendation and metric:
                current = float(metric['current'])
                target = float(metric['target'])
                if current < target:
                    if 'шагов' in metric['metric'].lower():
                        recommendation = "Припаркуйте машину дальше от входа, выходите на одну остановку раньше, используйте лестницу вместо лифта."
                    elif 'стресс' in metric['metric'].lower():
                        recommendation = "Практикуйте техники дыхания и короткие медитации в течение дня."
                    elif 'хобби' in metric['metric'].lower():
                        recommendation = "Заблокируйте в календаре специальное время для хобби, относитесь к нему как к важной встрече."
                    elif 'сбережен' in metric['metric'].lower():
                        recommendation = "Создайте отдельный счет для сбережений и настройте автоматические переводы в день зарплаты."
            
            # Если не нашли специфичную рекомендацию, используем базовую
            if not recommendation:
                base_recommendations = {
                    "Отношения с любимыми": "Уделите время качественному общению. Запланируйте совместное мероприятие или романтический вечер.",
                    "Отношения с родными": "Поддерживайте регулярный контакт с семьей. Запланируйте еженедельные звонки или встречи.",
                    "Друзья": "Организуйте встречу с друзьями или онлайн-созвон для поддержания связи.",
                    "Карьера": "Проанализируйте свои профессиональные цели и составьте план развития на ближайшие месяцы.",
                    "Физическое здоровье": "Начните с простых привычек: утренняя зарядка, прогулки, правильное питание.",
                    "Ментальное здоровье": "Выделите время на отдых и восстановление. Практикуйте техники релаксации.",
                    "Хобби и увлечения": "Исследуйте новые интересы и найдите занятие, которое приносит удовольствие.",
                    "Благосостояние": "Создайте финансовый план и начните вести учет доходов и расходов."
                }
                recommendation = base_recommendations.get(sphere, "Установите конкретные цели и отслеживайте прогресс.")
            
            recommendations[sphere] = recommendation
    
    return recommendations

def run_injector():
    """
    Главная функция: находит черновик, парсит его и полностью пересоздает дашборд.
    """
    logging.info("--- 🚀 Запуск AI Dashboard Injector (метод регенерации) ---")

    latest_draft = find_latest_draft()
    if not latest_draft:
        logging.critical("Работа прервана: не найден актуальный черновик.")
        return

    logging.info(f"Чтение содержимого из файла: {latest_draft}")
    try:
        with open(latest_draft, 'r', encoding='utf-8') as f:
            draft_content = f.read()
    except FileNotFoundError:
        logging.critical(f"Файл черновика не найден по пути: {latest_draft}")
        return
    except Exception as e:
        logging.critical(f"Не удалось прочитать файл черновика: {e}", exc_info=True)
        return

    pro_data = parse_pro_data(draft_content)
    
    # Загружаем стандартные метрики из БД
    standard_metrics = parse_questions_database()

    reports_history = collect_reports_history()
    
    # --- Генерация графика тренда ---
    trend_chart_path = generate_trend_chart(reports_history)
    if not trend_chart_path:
        trend_chart_path = "hpi/docs/images/trend_placeholder.png"
        logging.warning("Не удалось создать график тренда, будет использована заглушка.")
        
    # --- Определение путей к последним графикам ---
    latest_report_date_str = ""
    if reports_history:
        latest_report_date_str = reports_history[-1]['date'].strftime('%Y-%m-%d')
    
    radar_chart_path = f"reports_final/images/{latest_report_date_str}_radar.png" if latest_report_date_str else "hpi/docs/images/radar_placeholder.png"

    # --- Таблица истории HPI ---
    hpi_history_rows = []
    if reports_history:
        for report in sorted(reports_history, key=lambda x: x['date'], reverse=True):
            hpi = report.get('hpi', 0.0)
            emoji = get_score_emoji(hpi, is_hpi=True)
            hpi_history_rows.append(f"| {report['date'].strftime('%Y-%m-%d')} | {hpi:.1f} | {emoji} |")
    
    # --- Таблица истории по сферам ---
    spheres_history_rows = []
    if reports_history:
        for report in sorted(reports_history, key=lambda x: x['date'], reverse=True):
            row = f"| {report['date'].strftime('%Y-%m-%d')} "
            for sphere_config in SPHERES_CONFIG:
                score = report.get('scores', {}).get(sphere_config['key'], '-')
                row += f"| {score} "
            row += "|"
            spheres_history_rows.append(row)

    hpi_history_table = "\n".join(hpi_history_rows) if hpi_history_rows else "| Нет данных для отображения. | | |"
    
    spheres_header = "| Дата | " + " | ".join([s['emoji'] for s in SPHERES_CONFIG]) + " |\n|:---|:" + "---:|:" * (len(SPHERES_CONFIG)-1) + "---:|"
    spheres_history_table = spheres_header + "\n" + "\n".join(spheres_history_rows) if spheres_history_rows else "| Нет данных |" + " |" * len(SPHERES_CONFIG)
    
    # --- AI Рекомендации ---
    recommendations = generate_dummy_recommendations(pro_data)
    
    # --- Сборка дашборда ---
    dashboard_content = []

    # Заголовок
    hpi_score = reports_history[-1]['hpi'] if reports_history else 0
    hpi_emoji = get_score_emoji(hpi_score, is_hpi=True)
    dashboard_content.append(f"## Human Performance Index: {hpi_score} {hpi_emoji}")

    # --- Динамика HPI (график + таблица) ---
    dinamika_content = []
    dinamika_content.append(f"![Динамика HPI](../../{trend_chart_path.replace(os.path.sep, '/')})")
    if hpi_history_table:
        dinamika_content.append("\n" + hpi_history_table)
    
    # Форматируем контент для callout
    dinamika_formatted = "\n> ".join("\n".join(dinamika_content).split("\n"))
    dashboard_content.append(f'\n> [!note]- 📈 Динамика HPI\n> {dinamika_formatted}')

    # --- Баланс по сферам (график + таблица) ---
    balans_content = []
    balans_content.append(f"![Баланс по сферам](../../{radar_chart_path.replace(os.path.sep, '/')})")
    if spheres_history_table:
        balans_content.append("\n" + spheres_history_table)

    # Форматируем контент для callout
    balans_formatted = "\n> ".join("\n".join(balans_content).split("\n"))
    dashboard_content.append(f'\n> [!note]- ⚖️ Баланс по сферам\n> {balans_formatted}')

    dashboard_content.append("\n---\n")
    dashboard_content.append("## PRO-разделы")

    pro_section_callout_type = "example"  # Единый стиль для всех PRO-подразделов

    # Мои проблемы
    if pro_data.get('Мои проблемы'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🔴 Мои проблемы')
        dashboard_content.append("> | Сфера | Проблема |")
        dashboard_content.append("> |:---:|:---|")
        for sphere in SPHERES_CONFIG:
            problem = pro_data.get('Мои проблемы', {}).get(sphere['key'], 'Нет данных')
            if problem != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} | {problem} |")

    # Мои цели
    if pro_data.get('Мои цели'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🎯 Мои цели')
        dashboard_content.append("> | Сфера | Цель |")
        dashboard_content.append("> |:---:|:---|")
        for sphere in SPHERES_CONFIG:
            goal = pro_data.get('Мои цели', {}).get(sphere['key'], 'Нет данных')
            if goal != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} | {goal} |")

    # Мои блокеры
    if pro_data.get('Мои блокеры'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🚧 Мои блокеры')
        dashboard_content.append("> | Сфера | Блокер |")
        dashboard_content.append("> |:---:|:---|")
        for sphere in SPHERES_CONFIG:
            blocker = pro_data.get('Мои блокеры', {}).get(sphere['key'], 'Нет данных')
            if blocker != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} | {blocker} |")

    # Мои достижения
    if pro_data.get('Мои достижения'):
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🏆 Мои достижения')
        dashboard_content.append("> | Сфера | Достижение |")
        dashboard_content.append("> |:---:|:---|")
        for sphere in SPHERES_CONFIG:
            achievement = pro_data.get('Мои достижения', {}).get(sphere['key'], 'Нет данных')
            if achievement != 'Нет данных':
                dashboard_content.append(f"> | {sphere['emoji']} | {achievement} |")

    # Мои метрики
    if pro_data.get('Мои метрики') or standard_metrics:
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 📊 Мои метрики')
        dashboard_content.append("> | Сфера | Метрика | Текущее значение | Целевое значение |")
        dashboard_content.append("> |:---:|:---|:---:|:---:|")
        
        # Получаем фактические данные из черновика
        actual_metrics_list = pro_data.get('Мои метрики', [])
        # Преобразуем их в словарь для быстрого доступа: {(сфера, название): {данные}}
        actual_metrics_map = {(m['sphere'], m['metric']): m for m in actual_metrics_list}

        # Итерируемся по стандартным метрикам из БД
        for sphere_config in SPHERES_CONFIG:
            sphere_key = sphere_config['key']
            sphere_emoji = sphere_config['emoji']
            
            # Проходим по всем стандартным метрикам для данной сферы
            for metric_name in standard_metrics.get(sphere_key, []):
                # Ищем фактические данные для этой стандартной метрики
                metric_data = actual_metrics_map.get((sphere_key, metric_name))
                if metric_data:
                    current = metric_data.get('current', '-')
                    target = metric_data.get('target', '-')
                    dashboard_content.append(f"> | {sphere_emoji} | {metric_name} | {current} | {target} |")

    # AI Рекомендации
    if recommendations:
        dashboard_content.append(f'\n> [!{pro_section_callout_type}]- 🤖 AI Рекомендации')
        dashboard_content.append("> | Сфера | Рекомендация |")
        dashboard_content.append("> |:---:|:---|")
        for sphere in SPHERES_CONFIG:
            recommendation = recommendations.get(sphere['key'])
            if recommendation:
                dashboard_content.append(f"> | {sphere['emoji']} | {recommendation} |")

    # --- Сохранение дашборда ---
    dashboard_path = os.path.join(INTERFACES_DIR, 'dashboard.md')
    try:
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dashboard_content))
        logging.info(f"Дашборд успешно сохранен в {dashboard_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении дашборда: {e}", exc_info=True)
        return

    logging.info("--- ✅ AI Dashboard Injector успешно завершил работу ---")


if __name__ == '__main__':
    # Настройка логирования для прямого запуска
    log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Вывод в консоль
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(log_formatter)
    
    # Корень логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(console)

    run_injector() 