from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class DetectionResult(BaseModel):
    """Schema for storing a detection result in MongoDB."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None          # None if unauthenticated
    input_type: Literal["text", "image", "video"]
    result: str                             # e.g. "spam", "ham", "real", "fake"
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DetectionResponse(BaseModel):
    """Schema returned to the client after a detection request."""
    result: str
    confidence: float
    input_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
