from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.app_setting import AppSetting
from app.models.daily_record import DailyRecord
from app.models.food_item import FoodItem
from app.services.daily_record_store import bulk_import_daily_records
from app.services.food_store import replace_foods
from app.services.legacy_data_loader import load_legacy_daily_records, load_legacy_foods

LEGACY_JSON_MIGRATION_KEY = "legacy_json_to_sqlite_migrated_v1"


def get_setting(db: Session, key: str):
    return db.query(AppSetting).filter(AppSetting.key == key).first()


def set_setting(db: Session, key: str, value: str):
    setting = get_setting(db, key)

    if setting is None:
        setting = AppSetting(key=key, value=value)
        db.add(setting)
    else:
        setting.value = value

    db.commit()


def bootstrap_database():
    db = SessionLocal()

    try:
        if get_setting(db, LEGACY_JSON_MIGRATION_KEY):
            return

        if db.query(FoodItem).count() == 0:
            legacy_foods = load_legacy_foods()

            if legacy_foods:
                replace_foods(db, legacy_foods)

        if db.query(DailyRecord).count() == 0:
            legacy_records = load_legacy_daily_records()

            if legacy_records:
                bulk_import_daily_records(db, legacy_records)

        set_setting(
            db,
            LEGACY_JSON_MIGRATION_KEY,
            datetime.now(timezone.utc).isoformat()
        )
    finally:
        db.close()
