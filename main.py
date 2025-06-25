import os
import sys
import logging
from datetime import datetime

# --- Информация о приложении ---
APP_VERSION = "0.7.0"

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

        # Импортируем функцию проверки OpenAI
        from src.dashboard.ai.test_openai import check_openai_available
        logging.info("Вызов check_openai_available...")
        openai_error = check_openai_available()
        logging.info(f"check_openai_available завершен. Результат: {openai_error}")

        if openai_error:
            logging.warning(f"OpenAI API недоступен: {openai_error}")
        else:
            logging.info("OpenAI API доступен и работает корректно.")

        # Импортируем модули прямо здесь, чтобы быть уверенными, что sys.path уже обновлен
        logging.info("Импорт run_calculator...")
        from src.calculator import run_calculator
        logging.info("Импорт run_calculator завершен.")
        logging.info("Импорт DashboardInjector...")
        from src.dashboard.injector import DashboardInjector
        logging.info("Импорт DashboardInjector завершен.")
        
        logging.info("Шаг 1: Запуск калькулятора для расчета метрик...")
        run_calculator()
        logging.info("Калькулятор успешно завершил работу.")

        logging.info("Шаг 2: Запуск инжектора для обновления PRO-дашборда...")
        injector = DashboardInjector(version=APP_VERSION)
        
        # Обновляем основной дашборд, передаём openai_error
        dashboard_path = injector.inject(save_draft=False, openai_error=openai_error)
        logging.info(f"Дашборд обновлен: {dashboard_path}")

    except ImportError as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА. Убедитесь, что все скрипты находятся в папке 'src' и все зависимости установлены. Ошибка: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ НЕПРЕДВИДЕННАЯ ОШИБКА в главном процессе: {e}", exc_info=True)

    logging.info("--- ✅ Система HPI завершила работу ---")

if __name__ == "__main__":
    main() 