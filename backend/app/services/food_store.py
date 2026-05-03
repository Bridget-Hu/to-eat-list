import csv
import json
from io import StringIO

from sqlalchemy.orm import Session

from app.models.food_item import FoodItem


def parse_price(value):
    try:
        if value is None or value == "":
            return None

        return float(str(value).replace("元", "").strip())
    except ValueError:
        return None


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

    category = (
        row.get("分类")
        or row.get("类别")
        or row.get("category")
        or ""
    ).strip()

    price = parse_price(
        row.get("价格")
        or row.get("price")
        or row.get("金额")
    )

    taste = (
        row.get("口味")
        or row.get("taste")
        or ""
    ).strip()

    tags = (
        row.get("标签")
        or row.get("tags")
        or ""
    ).strip()

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
        "category": category,
        "price": price,
        "taste": taste,
        "tags": tags,
        "note": note
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
                "分类": parts[1] if len(parts) > 1 else "",
                "价格": parts[2] if len(parts) > 2 else "",
                "口味": parts[3] if len(parts) > 3 else "",
                "标签": parts[4] if len(parts) > 4 else "",
                "备注": parts[5] if len(parts) > 5 else ""
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
        "category": food.category or "",
        "price": food.price,
        "taste": food.taste or "",
        "tags": food.tags or "",
        "note": food.note or ""
    }


def load_foods(db: Session):
    foods = db.query(FoodItem).order_by(FoodItem.id.asc()).all()
    return [serialize_food(food) for food in foods]


def replace_foods(db: Session, foods_data):
    db.query(FoodItem).delete()

    for food in foods_data:
        db.add(FoodItem(**food))

    db.commit()

    return load_foods(db)


def clear_foods(db: Session):
    db.query(FoodItem).delete()
    db.commit()
