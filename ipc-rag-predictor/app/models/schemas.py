from pydantic import BaseModel, Field
from typing import List, Optional

class PredictRequest(BaseModel):
    crime_description: str = Field(..., min_length=10, max_length=2000)
    top_k: Optional[int] = Field(default=10, ge=1, le=20)
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class IPCSection(BaseModel):
    section: str
    title: str
    excerpt: str
    score: float
    confidence: float

class PredictResponse(BaseModel):
    predictions: List[IPCSection]
    query: str
    total_retrieved: int
    processing_time_ms: float