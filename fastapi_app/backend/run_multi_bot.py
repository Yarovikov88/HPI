import sys
import os
import importlib
from dotenv import load_dotenv
load_dotenv()

# Добавляем src в sys.path для корректных абсолютных импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Динамический импорт main из telegram_bot_multi.bot
bot_module = importlib.import_module("telegram_bot_multi.bot")
main = getattr(bot_module, "main")

if __name__ == "__main__":
    main()