"""
Генерация линейного графика изменений HPI
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re
import os
import sys
import logging
from typing import List, Dict, Optional, Tuple
import io
from src.telegram_bot_multi.db_async import get_hpi_history

# Определяем корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_FOLDER = os.path.join(PROJECT_ROOT, "reports_final")
IMAGES_FOLDER = os.path.join(REPORTS_FOLDER, "images")

def find_reports() -> List[str]:
    """Находит все файлы финальных отчетов."""
    if not os.path.exists(REPORTS_FOLDER):
        logging.error(f"Папка с финальными отчетами не найдена: {REPORTS_FOLDER}")
        return []
    
    report_files = [os.path.join(REPORTS_FOLDER, f) for f in os.listdir(REPORTS_FOLDER) if f.endswith("_report.md")]
    logging.info(f"Найдено {len(report_files)} финальных отчетов.")
    return report_files

def extract_hpi_from_report(file_path: str) -> Optional[Tuple[datetime, float]]:
    """Извлекает дату и значение HPI из одного файла отчета."""
    filename = os.path.basename(file_path)
    date_str = filename.split('_')[0]
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        logging.warning(f"Не удалось извлечь дату из имени файла: {filename}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем в формате таблицы
        match = re.search(r'\|\s*\*\*Итоговый HPI\*\*\s*\|\s*\*\*(\d+\.\d+)\*\*\s*\|\s*[🟡🔵🔴🟢]\s*\|', content)
        if match:
            hpi_value = float(match.group(1))
            logging.info(f"Найдено значение HPI {hpi_value} в отчете: {filename}")
            return report_date, hpi_value
        
        logging.warning(f"Значение HPI не найдено в отчете: {filename}")
        return None
        
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filename}: {e}")
        return None

def create_trend_chart(dates: List[datetime], values: List[float], output_path: str) -> bool:
    """Создает линейный график изменений HPI."""
    if not dates or not values or len(dates) < 2:
        logging.warning(f"Недостаточно данных для построения графика тренда (нужно минимум 2 точки). Найдено: {len(dates)}")
        return False

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

    # Преобразуем даты в числовой формат для matplotlib
    date_nums = mdates.date2num(dates)
    ax.plot(date_nums, values, marker='o', markersize=6, linewidth=1.5, color='#FF1493', linestyle='-')

    # Настройка сетки и фона
    ax.grid(True, linestyle=':', alpha=0.2, color='gray')
    ax.set_facecolor('#1E2D2F')
    fig.patch.set_facecolor('#1E2D2F')

    # Форматирование подписей на оси X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=45)

    # Установка диапазона оси Y
    ax.set_ylim(0, 100)
    ax.set_ylabel('HPI Value', fontsize=10, color='white')

    # Добавление значений на график
    for date, value in zip(date_nums, values):
        ax.annotate(f'{value:.1f}', (date, value), textcoords="offset points", xytext=(0, 7), ha='center', color='white')

    ax.set_title('HPI Index Trend', fontsize=12, pad=15, color='white')
    
    # Настройка рамок
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('white')

    plt.tick_params(axis='both', labelsize=8, colors='white')
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', facecolor='#1E2D2F')
    plt.close()
    logging.info(f"График тренда успешно сохранен: {output_path}")
    return True

def generate_trend_chart(history_data: List[Dict]) -> Optional[str]:
    """
    Основная функция для создания графика тренда HPI на основе переданных данных.
    Сохраняет график с датой последнего отчета в имени файла.
    Возвращает относительный путь к созданному файлу или None в случае ошибки.
    """
    try:
        logging.info("--- 📈 Генерация графика тренда HPI ---")
        
        if not history_data or len(history_data) < 2:
            logging.warning("Недостаточно исторических данных для построения графика.")
            return None

        # Преобразуем строки дат в datetime
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in history_data]
        values = [item['hpi'] for item in history_data]

        # Определяем имя файла на основе последней даты
        latest_date_str = dates[-1].strftime("%Y-%m-%d")
        output_filename = f"{latest_date_str}_trend.png"
        
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        output_path = os.path.join(IMAGES_FOLDER, output_filename)
        
        if create_trend_chart(dates, values, output_path):
            # Возвращаем относительный путь от корня проекта для использования в Markdown
            relative_path = os.path.join(os.path.basename(REPORTS_FOLDER), os.path.basename(IMAGES_FOLDER), output_filename)
            # Заменяем разделители пути для совместимости с Markdown/URL
            return relative_path.replace(os.path.sep, '/')
        else:
            return None

    except Exception as e:
        logging.error(f"Критическая ошибка при создании графика тренда: {e}", exc_info=True)
        return None

async def plot_hpi_trend_for_telegram(user_id, lang='en'):
    """
    Строит график динамики HPI для Telegram-бота и возвращает BytesIO.
    """
    history = await get_hpi_history(user_id)
    if not history or len(history) < 2:
        return None
    dates = []
    values = []
    for row in history:
        if isinstance(row, dict):
            created_at = row.get('created_at')
            hpi_value = row.get('hpi_value')
        else:
            hpi_value, created_at = row[0], row[1]
        if created_at is not None and hasattr(created_at, 'strftime'):
            date_str = created_at.strftime('%Y-%m-%d')
        elif created_at is not None:
            date_str = str(created_at)[:10]
        else:
            date_str = ''
        dates.append(date_str)
        values.append(hpi_value)
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    ax.plot(dates, values, marker='o', markersize=7, linewidth=2, color='#e75480', linestyle='-')
    ax.grid(True, linestyle=':', alpha=0.2, color='gray')
    ax.set_facecolor('#1E2D2F')
    fig.patch.set_facecolor('#1E2D2F')
    ax.set_ylim(0, 100)
    # --- Языковые подписи ---
    if lang == 'ru':
        ylabel = 'Значение HPI'
        title = 'Динамика HPI'
    else:
        ylabel = 'HPI Value'
        title = 'HPI Index Trend'
    ax.set_ylabel(ylabel, fontsize=10, color='white')
    for x, y in zip(dates, values):
        ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0, 7), ha='center', color='white', fontsize=9)
    ax.set_title(title, fontsize=13, pad=15, color='white')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('white')
    plt.tick_params(axis='both', labelsize=8, colors='white')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#1E2D2F')
    buf.seek(0)
    plt.close()
    return buf

if __name__ == "__main__":
    # Для автономного тестирования этого модуля напрямую
    # Создадим фиктивные данные
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    mock_history = [
        {'date': datetime(2024, 1, 1), 'hpi': 65.2, 'scores': {}},
        {'date': datetime(2024, 1, 15), 'hpi': 68.0, 'scores': {}},
        {'date': datetime(2024, 2, 1), 'hpi': 72.5, 'scores': {}},
        {'date': datetime(2024, 2, 20), 'hpi': 71.8, 'scores': {}},
    ]
    generated_path = generate_trend_chart(mock_history)
    if generated_path:
        print(f"Тестовый график тренда создан: {generated_path}")
    else:
        print("Не удалось создать тестовый график.") 