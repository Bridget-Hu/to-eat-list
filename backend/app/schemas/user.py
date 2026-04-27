# user.py

from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPreferenceCreate(BaseModel):
    nickname: Optional[str] = None
    taste_preference: Optional[str] = None
    dislike_food: Optional[str] = None
    spicy_level: Optional[str] = None
    milk_tea_limit_per_week: Optional[int] = None
    health_goal: Optional[str] = None
    email: Optional[str] = None


class UserPreferenceResponse(BaseModel):
    id: int
    nickname: Optional[str] = None
    taste_preference: Optional[str] = None
    dislike_food: Optional[str] = None
    spicy_level: Optional[str] = None
    milk_tea_limit_per_week: Optional[int] = None
    health_goal: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)