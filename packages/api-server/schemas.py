from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

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


# --- Схемы для ответов ---

class AnswerBase(BaseModel):
    question_id: str
    score: int

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
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProProblemBase(BaseModel):
    sphere_id: str
    text: str
    severity: Optional[int] = None
    status: Optional[str] = None

class ProProblemCreate(ProProblemBase):
    pass

class ProProblem(ProProblemBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProGoalBase(BaseModel):
    sphere_id: str
    text: str
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None

class ProGoalCreate(ProGoalBase):
    pass

class ProGoal(ProGoalBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProBlockerBase(BaseModel):
    sphere_id: str
    text: str
    impact_level: Optional[int] = None
    related_goals: Optional[str] = None

class ProBlockerCreate(ProBlockerBase):
    pass

class ProBlocker(ProBlockerBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

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