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
from typing import Dict, List
import logging

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

# --- УТИЛИТЫ ---

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
    Извлекает все PRO-данные (проблемы, цели и т.д.) из черновика.
    Возвращает словарь, где ключ - название секции, значение - словарь {сфера: ответ}.
    """
    logging.info("Начало парсинга PRO-секций из черновика.")
    pro_sections = ['Мои проблемы', 'Мои цели', 'Мои блокеры', 'Мои достижения']
    all_pro_data = {section: {} for section in pro_sections}

    for section_title in pro_sections:
        logging.debug(f"Поиск секции: '{section_title}'")
        section_data = {}
        in_section = False
        lines = md_content.split('\n')
        
        for i, line in enumerate(lines):
            if section_title in line and line.strip().startswith('###'):
                logging.debug(f"Найдена строка с заголовком секции: '{line.strip()}'")
                for table_line in lines[i+1:]:
                    if table_line.strip().startswith('###'):
                        logging.debug(f"Достигнут конец секции '{section_title}', найдена следующая: '{table_line.strip()}'")
                        break 
                    
                    if table_line.strip().startswith('|'):
                        parts = [p.strip() for p in table_line.split('|') if p.strip()]
                        logging.debug(f"Обработка строки таблицы: {parts}")
                        if len(parts) >= 2:
                            sphere_candidate = parts[0]
                            answer = parts[1]
                            # Обрабатываем случай, когда ответ "нет" или пустой
                            final_answer = answer if answer and answer.lower() not in ['нет', ''] else "Нет данных"

                            for config in SPHERES_CONFIG:
                                if config['key'] in sphere_candidate or config['emoji'] in sphere_candidate:
                                    section_data[config['key']] = final_answer
                                    logging.debug(f"Найдено соответствие: Сфера='{config['key']}', Ответ='{final_answer}'")
                                    break
                all_pro_data[section_title] = section_data
                logging.info(f"Для секции '{section_title}' извлечены следующие данные: {section_data}")
                break # Переходим к следующей PRO-секции
    
    logging.info(f"Парсинг PRO-секций завершен. Итоговые данные: {all_pro_data}")
    return all_pro_data

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
    # logging.info(f"Данные из PRO-секций извлечены: {pro_data}")

    dashboard_lines = [
        "# HPI", "",
        "> [!tip]- 📊 Мой HPI", ">",
        "> ## Динамика HPI", "> ![hpi trend](../reports_final/images/latest_trend.png)", ">",
        "> ## История измерений", "> | Дата | HPI | Тренд |", "> |------|-----|--------|", "",
        "> [!tip]- ⚖️ HPI баланс", ">",
        "> ![radar chart](../reports_final/images/latest_radar.png)", ">",
        "> ## История по сферам", "> | Дата | 💖 | 🏡 | 🤝 | 💼 | ♂️ | 🧠 | 🎨 | 💰 |",
        "> |------|------|------|------|------|------|------|------|------|", "",
        "# HPI PRO", ""
    ]

    section_map = {
        'Мои проблемы': '🛑', 'Мои цели': '🎯',
        'Мои блокеры': '🚧', 'Мои достижения': '🏆'
    }
    
    for section_title, emoji in section_map.items():
        dashboard_lines.extend([
            f"> [!info]- {emoji} {section_title}", ">",
            "> | Сфера | Ваши ответы |", "> |:------:|-------------|"
        ])
        
        section_answers = pro_data.get(section_title, {})
        
        for sphere_config in SPHERES_CONFIG:
            sphere_key = sphere_config['key']
            sphere_emoji = sphere_config['emoji']
            answer = section_answers.get(sphere_key, "Нет данных")
            dashboard_lines.append(f"> |  {sphere_emoji}  | {answer} |")
        
        dashboard_lines.append("")

    dashboard_path = os.path.join(INTERFACES_DIR, 'dashboard.md')
    final_dashboard_content = "\n".join(dashboard_lines)

    logging.info(f"Подготовлено финальное содержимое для дашборда по пути: {dashboard_path}")
    # Для отладки можно раскомментировать следующую строку, чтобы увидеть полный текст
    # logging.debug(f"Содержимое для записи:\n---\n{final_dashboard_content}\n---")

    try:
        logging.info("Попытка записи в файл дашборда...")
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(final_dashboard_content)
        logging.info(f"Дашборд успешно пересоздан: {dashboard_path}")
    except Exception as e:
        logging.critical(f"Критическая ошибка при записи в дашборд: {e}", exc_info=True)

    logging.info("--- ✅ AI Dashboard Injector завершил работу ---")

if __name__ == "__main__":
    run_injector() 