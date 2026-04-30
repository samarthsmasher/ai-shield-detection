from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for registering a new user (incoming request body)."""
    password: str = Field(..., min_length=6)


class UserInDB(UserBase):
    """Schema for storing a user in MongoDB (includes hashed password)."""
    id: Optional[str] = Field(default=None, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """Schema for returning user data in API responses (no password)."""
    id: Optional[str] = None
    created_at: datetime

    class Config:
        populate_by_name = True
