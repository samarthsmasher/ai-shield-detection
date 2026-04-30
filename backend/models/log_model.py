from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SystemLog(BaseModel):
    """Schema for logging every API request in MongoDB."""
    id: Optional[str] = Field(default=None, alias="_id")
    endpoint: str                           # e.g. "/api/detect/text"
    method: str                             # e.g. "POST"
    status_code: int                        # e.g. 200, 422, 500
    processing_time_ms: float               # time taken to handle request
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
