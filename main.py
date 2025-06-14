import os
import sys
import logging
from datetime import datetime

# --- Информация о приложении ---
APP_VERSION = "0.4.0"

# --- Настройка логирования ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'app.log')
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'src')

# Добавляем папку с модулями в sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Настраиваем логгер
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Файловый обработчик
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Консольный обработчик
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# --- Конец настройки логирования ---

# --- Основная логика ---
def main():
    """
    Основной воркфлоу системы HPI.
    Последовательно вызывает калькулятор и инжектор в одном процессе.
    """
    logging.info("--- 🚀 Начало работы системы HPI (единый процесс) ---")
    
    try:
        # Проверяем наличие API ключа
        if not os.getenv("OPENAI_API_KEY"):
            logging.warning("OPENAI_API_KEY не найден в переменных окружения. AI-рекомендации будут недоступны.")
        
        # Импортируем модули прямо здесь, чтобы быть уверенными, что sys.path уже обновлен
        from src.calculator import run_calculator
        from src.dashboard.injector import DashboardInjector
        
        logging.info("Шаг 1: Запуск калькулятора для расчета метрик...")
        run_calculator()
        logging.info("Калькулятор успешно завершил работу.")

        logging.info("Шаг 2: Запуск инжектора для обновления PRO-дашборда...")
        injector = DashboardInjector(version=APP_VERSION)
        
        # Обновляем основной дашборд
        dashboard_path = injector.inject(save_draft=False)
        logging.info(f"Дашборд обновлен: {dashboard_path}")

    except ImportError as e:
        logging.error(f"Ошибка импорта. Убедитесь, что все скрипты находятся в папке 'src'. Ошибка: {e}")
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка в главном процессе: {e}", exc_info=True)

    logging.info("--- ✅ Система HPI завершила работу ---")

if __name__ == "__main__":
    main() 