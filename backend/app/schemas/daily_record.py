from pydantic import BaseModel


class MealRecordResponse(BaseModel):
    type: str
    name: str
    reason: str
    price: float | None = None


class DailyRecordResponse(BaseModel):
    id: int
    createdAt: str
    budget: float
    goal: str
    taste: str
    dislike: str
    want: str
    hadMilkTea: bool
    totalPrice: float
    remainingBudget: float
    summary: str
    meals: list[MealRecordResponse]


class DailyRecordListResponse(BaseModel):
    count: int
    data: list[DailyRecordResponse]
