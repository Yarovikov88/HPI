import logging
import sys

def setup_logging():
    """Упрощенная настройка логирования без файлов"""
    logger = logging.getLogger("hpi_api")
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие хендлеры
    logger.handlers.clear()
    
    # Создаем консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Добавляем хендлер
    logger.addHandler(console_handler)
    
    return logger

# Создаем логгер
logger = setup_logging() 