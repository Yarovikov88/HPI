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

class DashboardResponse(BaseModel):
    basic: Optional[BasicDashboardData] = None
    pro: Optional[Any] = None # Заглушка для будущего Pro-дашборда 