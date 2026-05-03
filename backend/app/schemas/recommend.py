from pydantic import BaseModel

from app.schemas.daily_record import MealRecordResponse


class RecommendRequest(BaseModel):
    budget: int | None = 60
    taste: str | None = ""
    dislike: str | None = ""
    want: str | None = ""
    goal: str | None = ""
    hadMilkTea: bool | None = False


class RecommendResponse(BaseModel):
    breakfast: str
    breakfastReason: str
    lunch: str
    lunchReason: str
    dinner: str
    dinnerReason: str
    summary: str
    totalPrice: float
    remainingBudget: float
    recordId: int
    createdAt: str
    meals: list[MealRecordResponse]
