import csv
import json
from io import StringIO

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.food_item import FoodItem
from app.schemas.food_item import FoodItemCreate, FoodItemUpdate


def parse_price(value):
    try:
        if value is None or value == "":
            return None

        return float(str(value).replace("元", "").strip())
    except ValueError:
        return None


def parse_frequency_weight(value):
    try:
        if value is None or value == "":
            return 1.0

        weight = float(str(value).strip())
    except ValueError:
        return 1.0

    return min(3.0, max(0.5, weight))


def normalize_tag_text(value):
    if value is None:
        return ""

    normalized = str(value).replace(",", "、").replace("，", "、")
    return "、".join(item.strip() for item in normalized.split("、") if item.strip())


def normalize_food(row):
    if not isinstance(row, dict):
        return None

    name = (
        row.get("名称")
        or row.get("菜品名称")
        or row.get("name")
        or row.get("food")
        or ""
    ).strip()

    store = (
        row.get("店名")
        or row.get("店铺")
        or row.get("store")
        or row.get("shop")
        or ""
    ).strip()

    category = (
        row.get("分类")
        or row.get("类别")
        or row.get("category")
        or "其他"
    ).strip()

    price = parse_price(
        row.get("价格")
        or row.get("price")
        or row.get("金额")
    )
    frequency_weight = parse_frequency_weight(
        row.get("推荐权重")
        or row.get("出现频率")
        or row.get("frequency_weight")
        or row.get("frequencyWeight")
        or row.get("recommendation_weight")
        or row.get("recommendationWeight")
    )

    taste_tags = normalize_tag_text(
        row.get("口味")
        or row.get("taste")
        or row.get("taste_tags")
        or row.get("tasteTags")
        or ""
    )

    health_tags = normalize_tag_text(
        row.get("健康标签")
        or row.get("health_tags")
        or row.get("healthTags")
        or row.get("标签")
        or row.get("tags")
        or ""
    )

    note = (
        row.get("备注")
        or row.get("note")
        or row.get("说明")
        or ""
    ).strip()

    if not name:
        return None

    return {
        "name": name,
        "store": store,
        "category": category or "其他",
        "price": price,
        "frequency_weight": frequency_weight,
        "taste": taste_tags,
        "tags": health_tags,
        "taste_tags": taste_tags,
        "health_tags": health_tags,
        "note": note,
    }


def parse_food_text(text):
    text = text.strip()

    if not text:
        return []

    rows = []
    reader = csv.DictReader(StringIO(text))

    if reader.fieldnames and ("名称" in reader.fieldnames or "name" in reader.fieldnames):
        rows.extend(reader)
    else:
        for line in text.splitlines():
            parts = [item.strip() for item in line.split(",")]

            if not parts or not parts[0]:
                continue

            rows.append({
                "名称": parts[0] if len(parts) > 0 else "",
                "店名": parts[1] if len(parts) > 1 else "",
                "价格": parts[2] if len(parts) > 2 else "",
                "分类": parts[3] if len(parts) > 3 else "",
                "口味": parts[4] if len(parts) > 4 else "",
                "标签": parts[5] if len(parts) > 5 else "",
                "备注": parts[6] if len(parts) > 6 else "",
            })

    foods = []

    for row in rows:
        food = normalize_food(row)

        if food:
            foods.append(food)

    return foods


def parse_food_json_text(text):
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(payload, dict):
        payload = payload.get("data") or payload.get("foods") or []

    if not isinstance(payload, list):
        return []

    foods = []

    for row in payload:
        food = normalize_food(row)

        if food:
            foods.append(food)

    return foods


def import_foods_from_text(text, filename=""):
    lower_name = filename.lower()

    if lower_name.endswith(".json"):
        return parse_food_json_text(text)

    return parse_food_text(text)


def serialize_food(food):
    return {
        "id": food.id,
        "name": food.name,
        "store": food.store or "",
        "category": food.category or "",
        "price": food.price,
        "frequency_weight": float(food.frequency_weight or 1.0),
        "taste_tags": food.taste_tags or food.taste or "",
        "health_tags": food.health_tags or food.tags or "",
        "note": food.note or "",
        "created_at": food.created_at,
        "updated_at": food.updated_at,
    }


def load_foods(db: Session):
    foods = db.query(FoodItem).order_by(FoodItem.id.asc()).all()
    return [serialize_food(food) for food in foods]


def count_foods(db: Session):
    return db.query(FoodItem).count()


def normalize_food_payload(data: FoodItemCreate | FoodItemUpdate):
    category = getattr(data, "category", None)
    taste_tags = getattr(data, "taste_tags", None)
    health_tags = getattr(data, "health_tags", None)
    frequency_weight = getattr(data, "frequency_weight", None)

    normalized_category = (category or "").strip() or "其他"
    normalized_taste_tags = normalize_tag_text(taste_tags)
    normalized_health_tags = normalize_tag_text(health_tags)

    return {
        "name": getattr(data, "name", None),
        "store": (getattr(data, "store", None) or "").strip(),
        "category": normalized_category,
        "price": getattr(data, "price", None),
        "frequency_weight": parse_frequency_weight(frequency_weight),
        "taste": normalized_taste_tags,
        "tags": normalized_health_tags,
        "taste_tags": normalized_taste_tags,
        "health_tags": normalized_health_tags,
        "note": (getattr(data, "note", None) or "").strip(),
    }


def ensure_unique_food(db: Session, name: str, store: str = "", exclude_id: int | None = None):
    query = db.query(FoodItem).filter(
        func.lower(FoodItem.name) == (name or "").lower(),
        func.lower(func.coalesce(FoodItem.store, "")) == (store or "").lower(),
    )

    if exclude_id is not None:
        query = query.filter(FoodItem.id != exclude_id)

    if query.first():
        store_label = store or "未填写店名"
        raise HTTPException(
            status_code=400,
            detail=f"店铺“{store_label}”下已存在同名菜品，请勿重复添加。",
        )


def get_food_or_404(db: Session, food_id: int):
    food = db.query(FoodItem).filter(FoodItem.id == food_id).first()

    if food is None:
        raise HTTPException(status_code=404, detail="菜品不存在。")

    return food


def create_food(db: Session, data: FoodItemCreate):
    payload = normalize_food_payload(data)
    ensure_unique_food(db, payload["name"], payload["store"])
    food = FoodItem(**payload)
    db.add(food)
    db.commit()
    db.refresh(food)
    return serialize_food(food)


def update_food(db: Session, food_id: int, data: FoodItemUpdate):
    food = get_food_or_404(db, food_id)

    updates = data.model_dump(exclude_unset=True)
    merged_payload = {
        "name": updates.get("name", food.name),
        "store": updates.get("store", food.store or ""),
        "price": updates.get("price", food.price),
        "category": updates.get("category", food.category or "其他"),
        "frequency_weight": updates.get("frequency_weight", food.frequency_weight or 1.0),
        "taste_tags": updates.get("taste_tags", food.taste_tags or food.taste or ""),
        "health_tags": updates.get("health_tags", food.health_tags or food.tags or ""),
        "note": updates.get("note", food.note or ""),
    }

    normalized_payload = normalize_food_payload(FoodItemCreate(**merged_payload))
    ensure_unique_food(db, normalized_payload["name"], normalized_payload["store"], exclude_id=food_id)

    for key, value in normalized_payload.items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)
    return serialize_food(food)


def delete_food(db: Session, food_id: int):
    food = get_food_or_404(db, food_id)
    db.delete(food)
    db.commit()


def delete_foods_by_ids(db: Session, food_ids):
    unique_ids = sorted({food_id for food_id in food_ids if food_id > 0})

    if not unique_ids:
        return 0

    deleted_count = (
        db.query(FoodItem)
        .filter(FoodItem.id.in_(unique_ids))
        .delete(synchronize_session=False)
    )
    db.commit()

    return deleted_count


def replace_foods(db: Session, foods_data):
    db.query(FoodItem).delete()

    for food in foods_data:
        db.add(FoodItem(**food))

    db.commit()

    return load_foods(db)


def clear_foods(db: Session):
    db.query(FoodItem).delete()
    db.commit()
