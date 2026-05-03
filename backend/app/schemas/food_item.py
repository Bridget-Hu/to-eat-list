from pydantic import BaseModel, ConfigDict


class FoodItemResponse(BaseModel):
    id: int
    name: str
    category: str | None = None
    price: float | None = None
    taste: str | None = None
    tags: str | None = None
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FoodListResponse(BaseModel):
    count: int
    data: list[FoodItemResponse]


class FoodImportResponse(BaseModel):
    message: str
    count: int
    data: list[FoodItemResponse]
