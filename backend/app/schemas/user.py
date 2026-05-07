from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserPreferenceCreate(BaseModel):
    budget: float = Field(default=0, ge=0)
    taste: str | None = ""
    dislike: str | None = ""
    goal: str | None = ""
    had_milk_tea: bool = Field(default=False, alias="hadMilkTea")
    want: str | None = ""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class UserPreferenceResponse(BaseModel):
    id: int
    budget: float
    taste: str | None = ""
    dislike: str | None = ""
    goal: str | None = ""
    had_milk_tea: bool = Field(alias="hadMilkTea")
    want: str | None = ""
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
