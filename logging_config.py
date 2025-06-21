import logging
import sys
from pathlib import Path
from typing import Optional

import yaml
from typing_extensions import TypedDict


class LoggingConfig(TypedDict):
    """Type definition for logging configuration."""

    log_dir: str
    log_file: str
    log_format: str
    log_datefmt: str


def setup_logging(config_path: Optional[str | Path] = None) -> logging.Logger:
    """
    Централизованная настройка логирования для HPI.

    Args:
        config_path: Путь к файлу конфигурации. Если не указан,
                    ищет config.yaml в текущей директории.

    Returns:
        logging.Logger: Настроенный логгер

    Raises:
        FileNotFoundError: Если файл конфигурации не найден
        yaml.YAMLError: Если файл конфигурации некорректен
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    else:
        config_path = Path(config_path)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    project_root = Path(__file__).parent
    log_config: LoggingConfig = config["logging"]
    log_dir = project_root / log_config["log_dir"]
    log_path = log_dir / log_config["log_file"]

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        log_config["log_format"], datefmt=log_config["log_datefmt"]
    )

    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
