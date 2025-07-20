from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# --- Базовые схемы, используемые в разных местах ---

class AnswerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    question_id: str
    answer: int
    created_at: datetime

# --- Схемы для Pro-ответов (ОТВЕТ API) ---

class ProProblemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    sphere_id: str
    text: str # Используем 'text' из модели SQLAlchemy
    created_at: datetime

class ProGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    sphere_id: str
    text: str # Используем 'text' из модели SQLAlchemy
    created_at: datetime
    
class ProBlockerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    sphere_id: str
    text: str # Используем 'text' из модели SQLAlchemy
    created_at: datetime

class ProAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    sphere_id: str
    description: str # В модели Achievement поле называется description
    created_at: datetime

class ProMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    sphere_id: str
    name: str
    current_value: int
    created_at: datetime


# --- Схема-объединение для всех видов Pro-ответов (старая, может понадобиться где-то еще) ---
AnyProAnswer = Union[ProAchievementResponse, ProProblemResponse, ProGoalResponse, ProBlockerResponse, ProMetricResponse]

# --- Новая схема для сгруппированных Pro-ответов за сегодня ---
class ProAnswersTodayResponse(BaseModel):
    problems: List[ProProblemResponse] = []
    goals: List[ProGoalResponse] = []
    blockers: List[ProBlockerResponse] = []
    achievements: List[ProAchievementResponse] = []
    metrics: List[ProMetricResponse] = []

# --- Схема для ответа от data_factory ---
class GeneratedData(BaseModel):
    answers: List[AnswerSchema]
    pro_answers: List[Any] # Оставляем Any, т.к. тут могут быть разные типы

# --- Существующие схемы ---

class Sphere(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class Question(BaseModel):
    id: str
    sphere_id: str
    category: Optional[str] = None
    text: Optional[str] = None
    options: Optional[List[str]] = None
    scores: Optional[List[int]] = None
    fields: Optional[Any] = None # JSONB
    metrics: Optional[Any] = None # JSONB

    class Config:
        from_attributes = True 

class SphereScore(BaseModel):
    sphere_id: str
    sphere_name: str
    score: float

class TrendDataPoint(BaseModel):
    date: datetime
    hpi: float

class SphereTrendData(BaseModel):
    sphere_id: str
    sphere_name: str
    trend: List[TrendDataPoint]

class BasicDashboardData(BaseModel):
    hpi: float
    hpi_change: Optional[float] = None
    trend: List[TrendDataPoint]
    radar: List[SphereScore]
    sphere_trends: List[SphereTrendData]
    last_updated: datetime

# --- Схемы для Pro-дашборда (в соответствии с ProDashboardPage.tsx) ---

class ProSectionItem(BaseModel):
    sphere: str
    value: str

class ProMetricsItem(BaseModel):
    sphere: str
    metric: str
    value: int
    target: int
    change_value: Optional[float] = None
    change_percent: Optional[float] = None

class RecommendationItem(BaseModel):
    sphere: str
    recommendation: str

class AiRecommendationItem(BaseModel):
    sphere: str
    ai_recommendation: str
    description: str
    steps: str
    justification: str

class ProDashboardData(BaseModel):
    problems: List[ProSectionItem]
    goals: List[ProSectionItem]
    blockers: List[ProSectionItem]
    metrics: List[ProMetricsItem]
    basic_recommendations: List[RecommendationItem]
    ai_recommendations: List[AiRecommendationItem]


class DashboardResponse(BaseModel):
    basic: Optional[BasicDashboardData] = None
    pro: Optional[ProDashboardData] = None


# --- Схемы для ответов (старые, могут быть использованы в других местах, пока не трогаем) ---

class AnswerBase(BaseModel):
    question_id: str
    answer: int

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# --- Схемы для Pro-ответов (входные данные) ---

class ProAchievementBase(BaseModel):
    sphere_id: str
    description: str
    date_achieved: Optional[datetime] = None
    impact_areas: Optional[str] = None

class ProAchievementCreate(ProAchievementBase):
    pass

class ProAchievement(ProAchievementBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime

class ProProblemBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    sphere_id: str
    text: str = Field(alias='description')
    severity: Optional[int] = None
    status: Optional[str] = None

class ProProblemCreate(ProProblemBase):
    pass

class ProProblem(ProProblemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime

class ProGoalBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    sphere_id: str
    text: str = Field(alias='description')
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None

class ProGoalCreate(ProGoalBase):
    pass

class ProGoal(ProGoalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime

class ProBlockerBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    sphere_id: str
    text: str = Field(alias='description')
    impact_level: Optional[int] = None
    related_goals: Optional[str] = None

class ProBlockerCreate(ProBlockerBase):
    pass

class ProBlocker(ProBlockerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime

class ProMetricBase(BaseModel):
    sphere_id: str
    name: str
    current_value: int
    target_value: Optional[int] = None
    unit: Optional[str] = None
    type: Optional[str] = None

class ProMetricCreate(ProMetricBase):
    pass

class ProMetric(ProMetricBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True 