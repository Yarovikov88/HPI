import os
import sys
import subprocess
import logging
import locale
from datetime import datetime

# --- Информация о приложении ---
APP_VERSION = "0.4.0-dev"

# --- Настройка логирования ---
# Определяем пути до того, как настроить логгер
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'src')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'app.log')

# Настраиваем логгер для вывода в файл и в консоль
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Удаляем все предыдущие обработчики, чтобы избежать дублирования
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Обработчик для записи в файл
file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Обработчик для вывода в консоль
# Принудительно настраиваем кодировку stdout для корректного отображения в Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError: # В некоторых средах (например, в VSCode) это может вызвать ошибку
        pass
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# --- Конец настройки логирования ---

# Добавляем папку бэкенда в системный путь, чтобы Python мог найти модули
sys.path.append(BACKEND_DIR)

def run_script(script_name: str):
    """Запускает указанный Python-скрипт из папки бэкенда."""
    script_path = os.path.join(BACKEND_DIR, script_name)
    logging.info(f"Запуск скрипта: {script_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,  # Не выбрасывать исключение при ошибке, а анализировать вручную
            encoding='utf-8', # Принудительно используем UTF-8
            errors='replace', # Заменять некорректные символы
            cwd=PROJECT_ROOT  # Запускаем из корня проекта
        )

        # Логируем stdout
        if result.stdout:
            logging.info(f"Вывод скрипта '{script_name}':\n{result.stdout}")

        # Логируем stderr
        if result.stderr:
            logging.warning(f"Ошибки скрипта '{script_name}':\n{result.stderr}")
        
        if result.returncode == 0:
            logging.info(f"Скрипт {script_name} успешно завершен.")
        else:
            logging.error(f"Скрипт {script_name} завершился с кодом ошибки: {result.returncode}")

    except FileNotFoundError:
        logging.error(f"Ошибка: Скрипт не найден по пути {script_path}")
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка при запуске {script_name}: {e}")

def main():
    logging.info("--- 🚀 Начало работы системы HPI ---")
    
    # Шаг 1: Запускаем основной калькулятор для расчета метрик и генерации отчета
    run_script('calculator.py')
    
    # Шаг 2: Запускаем инжектор для обновления PRO-дашборда
    # Этот скрипт может использовать артефакты, созданные калькулятором
    run_script('ai_dashboard_injector.py')

    logging.info("--- ✅ Система HPI завершила работу ---")

if __name__ == "__main__":
    main() 