from pydantic import BaseModel, Field


class MealRecordResponse(BaseModel):
    type: str
    name: str
    reason: str
    rank: int = 1
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
    actualChoice: str = ""
    meals: list[MealRecordResponse]


class DailyRecordListResponse(BaseModel):
    count: int
    data: list[DailyRecordResponse]


class DailyRecordActualChoiceUpdate(BaseModel):
    actualChoice: str | None = Field(default="", max_length=240)
