"""
Генерация линейного графика изменений HPI
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import re
import os
import sys

# Определяем корень проекта
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERFACES_FOLDER = os.path.join(PROJECT_ROOT, "interfaces")
REPORTS_FOLDER = os.path.join(PROJECT_ROOT, "reports_final")
IMAGES_FOLDER = os.path.join(REPORTS_FOLDER, "images")

def extract_hpi_history(dashboard_path):
    """Извлекает историю значений HPI из дашборда."""
    if not os.path.exists(dashboard_path):
        print(f"Файл дашборда не найден: {dashboard_path}")
        return [], []

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем все записи в формате даты и значения HPI
    pattern = r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+\.\d+)\s*\|'
    matches = re.findall(pattern, content)
    
    dates = []
    values = []
    for date_str, value_str in matches:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            value = float(value_str)
            dates.append(date)
            values.append(value)
        except (ValueError, TypeError):
            continue
    
    return dates, values

def create_trend_chart(dates, values, output_path):
    """Создает линейный график изменений HPI."""
    if not dates or not values:
        print("Нет данных для построения графика.")
        return

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

    ax.plot(dates, values, marker='o', markersize=6, linewidth=1.5, color='#FF1493', linestyle='-')

    # Настройка сетки и фона
    ax.grid(True, linestyle=':', alpha=0.2, color='gray')
    ax.set_facecolor('#1E2D2F')
    fig.patch.set_facecolor('#1E2D2F')

    # Форматирование подписей на оси X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=45)

    # Установка диапазона оси Y
    ax.set_ylim(0, 100)
    ax.set_ylabel('Значение HPI', fontsize=10, color='white')

    # Добавление значений на график
    for date, value in zip(dates, values):
        ax.annotate(f'{value:.1f}', (date, value), textcoords="offset points", xytext=(0, 7), ha='center', color='white')

    ax.set_title('График изменения индекса HPI', fontsize=12, pad=15, color='white')
    
    # Настройка рамок
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('white')

    plt.tick_params(axis='both', labelsize=8, colors='white')
    
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', facecolor='#1E2D2F')
    plt.close()
    print(f"График тренда сохранен: {output_path}")

def main():
    """Основная функция для создания графика тренда HPI."""
    try:
        dashboard_path = os.path.join(INTERFACES_FOLDER, "dashboard.md")
        output_path = os.path.join(IMAGES_FOLDER, "latest_trend.png")
        
        os.makedirs(IMAGES_FOLDER, exist_ok=True)

        dates, values = extract_hpi_history(dashboard_path)
        
        if dates and values:
            sorted_data = sorted(zip(dates, values))
            sorted_dates, sorted_values = zip(*sorted_data)
            create_trend_chart(list(sorted_dates), list(sorted_values), output_path)
        else:
            print("Не удалось найти данные для построения графика тренда.")

    except Exception as e:
        print(f"Ошибка при создании графика тренда: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 