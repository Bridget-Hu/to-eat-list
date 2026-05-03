import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.food_store import parse_food_json_text

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
LEGACY_FOODS_FILE = DATA_DIR / "foods.json"
LEGACY_DAILY_RECORDS_FILE = DATA_DIR / "daily_records.json"


def read_json_text(path: Path):
    if not path.exists():
        return None

    return path.read_text(encoding="utf-8")


def load_legacy_foods():
    text = read_json_text(LEGACY_FOODS_FILE)

    if not text:
        return []

    return parse_food_json_text(text)


def normalize_legacy_daily_record(payload):
    if not isinstance(payload, dict):
        return None

    meals = payload.get("meals")

    if not isinstance(meals, list):
        meals = []

    created_at = payload.get("createdAt")

    try:
        parsed_created_at = datetime.fromisoformat(created_at) if created_at else None
    except ValueError:
        parsed_created_at = None

    if parsed_created_at and parsed_created_at.tzinfo is None:
        parsed_created_at = parsed_created_at.replace(tzinfo=timezone.utc)

    return {
        "created_at": parsed_created_at,
        "budget": payload.get("budget") or 0,
        "goal": payload.get("goal") or "",
        "taste": payload.get("taste") or "",
        "dislike": payload.get("dislike") or "",
        "want": payload.get("want") or "",
        "hadMilkTea": bool(payload.get("hadMilkTea")),
        "totalPrice": payload.get("totalPrice") or 0,
        "remainingBudget": payload.get("remainingBudget") or 0,
        "summary": payload.get("summary") or "",
        "meals": meals
    }


def load_legacy_daily_records():
    text = read_json_text(LEGACY_DAILY_RECORDS_FILE)

    if not text:
        return []

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(payload, list):
        return []

    records = []

    for item in payload:
        record = normalize_legacy_daily_record(item)

        if record:
            records.append(record)

    records.sort(
        key=lambda item: item.get("created_at") or datetime.min.replace(tzinfo=timezone.utc)
    )

    return records
