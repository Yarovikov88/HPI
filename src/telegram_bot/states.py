"""
Состояния пользователя для Telegram-бота HPI
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class UserState(Enum):
    """Состояния пользователя в боте."""
    IDLE = "idle"
    STARTING_SURVEY = "starting_survey"
    ANSWERING_QUESTIONS = "answering_questions"
    COLLECTING_PRO_DATA = "collecting_pro_data"
    SHOWING_RESULTS = "showing_results"


@dataclass
class UserSession:
    """Сессия пользователя в боте."""
    user_id: int
    state: UserState = UserState.IDLE
    current_sphere: int = 0
    current_question: int = 0
    answers: Dict[str, List[int]] = field(default_factory=dict)
    pro_data: Dict[str, Dict] = field(default_factory=dict)
    survey_start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def reset(self):
        """Сброс сессии."""
        self.state = UserState.IDLE
        self.current_sphere = 0
        self.current_question = 0
        self.answers.clear()
        self.pro_data.clear()
        self.survey_start_time = None
        self.last_activity = None
    
    def is_complete(self) -> bool:
        """Проверяет, завершена ли сессия."""
        return len(self.answers) == 8 and all(len(answers) == 6 for answers in self.answers.values())


class SessionManager:
    """Менеджер сессий пользователей."""
    
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Получает или создает сессию пользователя."""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
        return self.sessions[user_id]
    
    def reset_session(self, user_id: int):
        """Сбрасывает сессию пользователя."""
        if user_id in self.sessions:
            self.sessions[user_id].reset()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Очищает старые сессии."""
        now = datetime.now()
        to_remove = []
        
        for user_id, session in self.sessions.items():
            if session.last_activity:
                age = (now - session.last_activity).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.sessions[user_id] 