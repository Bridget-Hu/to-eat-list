from pydantic import BaseModel, Field


class MealRecordResponse(BaseModel):
    type: str
    name: str
    reason: str
    price: float | None = None
    food_id: int | None = None
    store: str | None = ""
    category: str | None = ""
    score: float | None = None
    reasons: list[str] = Field(default_factory=list)


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
