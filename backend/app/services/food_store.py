import csv
import json
from io import StringIO
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "foods.json"


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_foods():
    ensure_data_file()

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_foods(foods):
    ensure_data_file()
    DATA_FILE.write_text(
        json.dumps(foods, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def clear_foods():
    save_foods([])


def parse_price(value):
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace("元", "").strip())
    except ValueError:
        return None


def normalize_food(row, food_id):
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
        "id": food_id,
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
        for row in reader:
            rows.append(row)
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

    for index, row in enumerate(rows, start=1):
        food = normalize_food(row, index)

        if food:
            foods.append(food)

    return foods


def import_foods_from_text(text):
    foods = parse_food_text(text)
    save_foods(foods)
    return foods