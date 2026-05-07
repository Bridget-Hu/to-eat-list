from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_optional_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_tag_value(value):
    if value is None:
        return ""

    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
    else:
        normalized = str(value).replace("，", ",").replace("、", ",")
        parts = [item.strip() for item in normalized.split(",") if item.strip()]

    return "、".join(parts)


class FoodItemBase(BaseModel):
    name: str
    store: str | None = ""
    price: float = Field(gt=0)
    category: str | None = "其他"
    taste_tags: str | list[str] | None = ""
    health_tags: str | list[str] | None = ""
    note: str | None = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        cleaned = normalize_optional_text(value)

        if not cleaned:
            raise ValueError("菜名不能为空")

        return cleaned

    @field_validator("store", "category", "note")
    @classmethod
    def validate_optional_text(cls, value):
        return normalize_optional_text(value)

    @field_validator("taste_tags", "health_tags")
    @classmethod
    def validate_tags(cls, value):
        return normalize_tag_value(value)


class FoodItemCreate(FoodItemBase):
    pass


class FoodItemUpdate(BaseModel):
    name: str | None = None
    store: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    taste_tags: str | list[str] | None = None
    health_tags: str | list[str] | None = None
    note: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        cleaned = normalize_optional_text(value)

        if not cleaned:
            raise ValueError("菜名不能为空")

        return cleaned

    @field_validator("store", "category", "note")
    @classmethod
    def validate_optional_text(cls, value):
        if value is None:
            return value

        return normalize_optional_text(value)

    @field_validator("taste_tags", "health_tags")
    @classmethod
    def validate_tags(cls, value):
        if value is None:
            return value

        return normalize_tag_value(value)


class FoodItemResponse(BaseModel):
    id: int
    name: str
    store: str | None = ""
    category: str | None = ""
    price: float | None = None
    taste_tags: str | None = ""
    health_tags: str | None = ""
    note: str | None = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FoodListResponse(BaseModel):
    count: int
    data: list[FoodItemResponse]


class FoodImportResponse(BaseModel):
    message: str
    count: int
    data: list[FoodItemResponse]
