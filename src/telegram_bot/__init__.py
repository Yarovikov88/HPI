"""
Telegram Bot для системы HPI
Версия: 1.0.0
"""

from .bot import HPIBot
from .handlers import setup_handlers
from .states import UserState

__all__ = ['HPIBot', 'setup_handlers', 'UserState'] 