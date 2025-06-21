import logging
import os

import yaml

from logging_config import setup_logging

# --- Загрузка конфигурации ---
CONFIG_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "config.yaml"
)
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config: dict = yaml.safe_load(f)

APP_VERSION: str = config["app_version"]

# --- Настройка логирования ---
logger: logging.Logger = setup_logging(CONFIG_PATH)


def main() -> None:
    """
    Основной воркфлоу системы HPI.
    Последовательно вызывает калькулятор и инжектор в одном процессе.
    """
    logging.info("--- 🚀 Начало работы системы HPI (единый процесс) ---")

    try:
        # Проверяем наличие API ключа
        if not os.getenv("OPENAI_API_KEY"):
            logging.warning(
                "OPENAI_API_KEY не найден в переменных окружения. "
                "AI-рекомендации будут недоступны."
            )

        # Импортируем модули прямо здесь, чтобы быть уверенными в sys.path
        from src.calculator import run_calculator
        from src.dashboard.injector import DashboardInjector

        logging.info("Шаг 1: Запуск калькулятора для расчета метрик...")
        run_calculator()
        logging.info("Калькулятор успешно завершил работу.")

        logging.info("Шаг 2: Запуск инжектора для обновления PRO-дашборда...")
        injector = DashboardInjector(version=APP_VERSION)

        # Обновляем основной дашборд
        dashboard_path: str = injector.inject(save_draft=False)
        logging.info(f"Дашборд обновлен: {dashboard_path}")

    except ImportError as e:
        error_msg = (
            "Ошибка импорта. Убедитесь, что все скрипты находятся "
            f"в папке 'src'. Ошибка: {e}"
        )
        logging.error(error_msg)
    except Exception as e:
        logging.error(
            "Произошла непредвиденная ошибка в главном процессе: " f"{e}",
            exc_info=True,
        )

    logging.info("--- ✅ Система HPI завершила работу ---")


if __name__ == "__main__":
    main()
