from pydantic import BaseModel
from typing import Optional, List, Any

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