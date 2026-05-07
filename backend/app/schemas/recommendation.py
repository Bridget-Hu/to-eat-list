from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.daily_record import MealRecordResponse


def _has_value(value):
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, list):
        return bool(value)

    return True


class RecommendRequest(BaseModel):
    budget: float | None = Field(default=60, ge=0)
    taste: str | list[str] | None = ""
    dislike: str | list[str] | None = ""
    want: str | list[str] | None = ""
    goal: str | None = ""
    hadMilkTea: bool | None = False
    taste_preferences: str | list[str] | None = None
    avoid_keywords: str | list[str] | None = None
    health_goal: str | None = None
    craving: str | list[str] | None = None
    has_milk_tea: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def merge_new_and_legacy_fields(self):
        if not _has_value(self.taste) and _has_value(self.taste_preferences):
            self.taste = self.taste_preferences

        if not _has_value(self.dislike) and _has_value(self.avoid_keywords):
            self.dislike = self.avoid_keywords

        if not _has_value(self.want) and _has_value(self.craving):
            self.want = self.craving

        if not _has_value(self.goal) and _has_value(self.health_goal):
            self.goal = self.health_goal

        if self.has_milk_tea is not None:
            self.hadMilkTea = self.has_milk_tea

        return self


class RecommendationItem(BaseModel):
    food_id: int | None = None
    name: str
    store: str | None = ""
    price: float | None = None
    category: str | None = ""
    score: float
    reasons: list[str] = Field(default_factory=list)


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
    recordId: int | None = None
    createdAt: str | None = None
    meals: list[MealRecordResponse]
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    total_estimated_price: float = 0
    generated_at: str = ""
