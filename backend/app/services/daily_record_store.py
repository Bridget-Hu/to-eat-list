import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "daily_records.json"


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_daily_records():
    ensure_data_file()

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return data


def save_daily_records(records):
    ensure_data_file()
    DATA_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def append_daily_record(record_data):
    records = load_daily_records()
    next_id = max((record.get("id", 0) for record in records), default=0) + 1

    record = {
        "id": next_id,
        "createdAt": datetime.now().astimezone().isoformat(),
        **record_data
    }

    records.insert(0, record)
    save_daily_records(records)

    return record


def clear_daily_records():
    save_daily_records([])
