# src/telegram_bot_multi/states.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id, get_user_answers, get_user_problems, get_user_goals, get_user_blockers, get_user_metrics, get_user_achievements

class UserState:
    IDLE = 0
    ANSWERING_QUESTIONS = 1
    COLLECTING_PRO = 2

@dataclass
class UserSession:
    user_id: int
    state: int = UserState.IDLE
    current_sphere: int = 0
    current_question: int = 0
    current_pro_question: int = 0
    current_pro_question_data: Optional[Dict] = None
    answers: Dict[str, List[int]] = field(default_factory=dict)
    pro_data: Dict[str, Dict] = field(default_factory=dict)
    survey_start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    problems: list = field(default_factory=list)
    goals: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    metrics: list = field(default_factory=list)
    achievements: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    ai_recommendations: list = field(default_factory=list)
    user_id_internal: Optional[int] = None
    pending_user_id_internal: Optional[int] = None
    language: Optional[str] = None
    answers_history: Dict[str, List[int]] = field(default_factory=dict)

    def reset(self):
        self.state = UserState.IDLE
        self.current_sphere = 0
        self.current_question = 0
        self.current_pro_question = 0
        self.current_pro_question_data = None
        self.answers.clear()
        self.pro_data.clear()
        self.survey_start_time = None
        self.last_activity = None

    def is_complete(self) -> bool:
        return len(self.answers) == 8 and all(len(answers) == 6 for answers in self.answers.values())

class SessionManager:
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}

    async def get_session(self, user_id: int) -> UserSession:
        if user_id not in self.sessions:
            session = UserSession(user_id=user_id)
            # --- Загрузка данных из БД ---
            db_user_id = await get_user_id_by_telegram_id(user_id)
            if db_user_id:
                # Загрузка базовых ответов
                answers = await get_user_answers(db_user_id)
                answers_dict = {}
                history_dict = {}
                for row in answers:
                    if isinstance(row, dict):
                        sphere = str(row.get('sphere'))
                        answer = row.get('answer')
                    else:
                        sphere = str(row[0])
                        answer = row[2]
                    # Нормализуем ключи: только текстовые (например, 'physical', 'career', ...)
                    sphere = sphere.lower()
                    if sphere not in answers_dict:
                        answers_dict[sphere] = []
                    answers_dict[sphere].append(answer)
                # Для расчёта HPI: только последние 6 по каждой сфере (по дате)
                # answers_dict: {sphere: [ответы]}
                # Нужно отсортировать по дате, если есть created_at
                # Предполагаем, что get_user_answers возвращает либо dict с created_at, либо просто значения
                for k, v in answers_dict.items():
                    # Если элементы — dict с created_at, сортируем
                    if v and isinstance(v[0], dict) and 'created_at' in v[0]:
                        v_sorted = sorted(v, key=lambda x: x['created_at'], reverse=True)
                        answers_dict[k] = [x['answer'] for x in v_sorted[:6]]
                    else:
                        answers_dict[k] = v[-6:]
                session.answers = {k: v for k, v in answers_dict.items()}
                # Для истории: все ответы (можно использовать answers_dict)
                session.answers_history = answers_dict
                # Загрузка PRO-данных (проблемы, цели, барьеры, метрики)
                pro_data = {}
                for problem in await get_user_problems(db_user_id):
                    if isinstance(problem, dict):
                        sphere = str(problem.get('sphere')).lower()
                        text = problem.get('text')
                    else:
                        sphere = str(problem[1]).lower()
                        text = problem[2]
                    if sphere not in pro_data:
                        pro_data[sphere] = {}
                    pro_data[sphere][f"Проблема"] = text
                for goal in await get_user_goals(db_user_id):
                    if isinstance(goal, dict):
                        sphere = str(goal.get('sphere')).lower()
                        text = goal.get('text')
                    else:
                        sphere = str(goal[1]).lower()
                        text = goal[2]
                    if sphere not in pro_data:
                        pro_data[sphere] = {}
                    pro_data[sphere][f"Цель"] = text
                for blocker in await get_user_blockers(db_user_id):
                    if isinstance(blocker, dict):
                        sphere = str(blocker.get('sphere')).lower()
                        text = blocker.get('text')
                    else:
                        sphere = str(blocker[1]).lower()
                        text = blocker[2]
                    if sphere not in pro_data:
                        pro_data[sphere] = {}
                    pro_data[sphere][f"Барьеры"] = text
                for metric in await get_user_metrics(db_user_id):
                    if isinstance(metric, dict):
                        sphere = str(metric.get('sphere')).lower()
                        name = metric.get('name')
                    else:
                        sphere = str(metric[1]).lower()
                        name = metric[2]
                    if sphere not in pro_data:
                        pro_data[sphere] = {}
                    pro_data[sphere][f"Метрика"] = name
                session.pro_data = pro_data
                # Явно присваиваем списки для интерфейса
                session.problems = await get_user_problems(db_user_id)
                session.goals = await get_user_goals(db_user_id)
                session.blockers = await get_user_blockers(db_user_id)
                session.metrics = await get_user_metrics(db_user_id)
                
                # Если списки пустые, но есть pro_data, создаем записи из pro_data
                if not session.problems and pro_data:
                    for sphere, data in pro_data.items():
                        if 'Проблема' in data:
                            session.problems.append({
                                'sphere': sphere,
                                'text': data['Проблема'],
                                'severity': 7,
                                'status': 'active',
                                'created_at': datetime.now()
                            })
                
                if not session.goals and pro_data:
                    for sphere, data in pro_data.items():
                        if 'Цель' in data:
                            session.goals.append({
                                'sphere': sphere,
                                'text': data['Цель'],
                                'priority': 'high',
                                'status': 'active',
                                'deadline': datetime.now()
                            })
                
                if not session.blockers and pro_data:
                    for sphere, data in pro_data.items():
                        if 'Барьеры' in data:
                            session.blockers.append({
                                'sphere': sphere,
                                'text': data['Барьеры'],
                                'impact_level': 'high',
                                'related_goals': 'general',
                                'created_at': datetime.now()
                            })
                
                if not session.metrics and pro_data:
                    for sphere, data in pro_data.items():
                        if 'Метрика' in data:
                            session.metrics.append({
                                'sphere': sphere,
                                'name': data['Метрика'],
                                'current_value': 60.0,
                                'target_value': 80.0,
                                'unit': 'ч',
                                'type': 'number',
                                'created_at': datetime.now()
                            })
                # Загрузка достижений
                session.achievements = await get_user_achievements(db_user_id)
            self.sessions[user_id] = session
        return self.sessions[user_id]

    def reset_session(self, user_id: int):
        if user_id in self.sessions:
            self.sessions[user_id].reset() 