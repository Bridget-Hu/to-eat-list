from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.daily_record import DailyRecord


def serialize_daily_record(record: DailyRecord):
    created_at = record.created_at

    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return {
        "id": record.id,
        "createdAt": created_at.isoformat() if created_at else "",
        "budget": float(record.budget or 0),
        "goal": record.goal or "",
        "taste": record.taste or "",
        "dislike": record.dislike or "",
        "want": record.want or "",
        "hadMilkTea": bool(record.had_milk_tea),
        "totalPrice": float(record.total_price or 0),
        "remainingBudget": float(record.remaining_budget or 0),
        "summary": record.summary or "",
        "meals": record.meals or []
    }


def load_daily_records(db: Session, limit=100):
    records = (
        db.query(DailyRecord)
        .order_by(DailyRecord.created_at.desc(), DailyRecord.id.desc())
        .limit(limit)
        .all()
    )

    return [serialize_daily_record(record) for record in records]


def count_daily_records(db: Session):
    return db.query(DailyRecord).count()


def append_daily_record(db: Session, record_data):
    created_at = record_data.get("created_at") or datetime.now(timezone.utc)

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    record = DailyRecord(
        created_at=created_at,
        budget=float(record_data.get("budget") or 0),
        goal=record_data.get("goal") or "",
        taste=record_data.get("taste") or "",
        dislike=record_data.get("dislike") or "",
        want=record_data.get("want") or "",
        had_milk_tea=bool(record_data.get("hadMilkTea")),
        total_price=float(record_data.get("totalPrice") or 0),
        remaining_budget=float(record_data.get("remainingBudget") or 0),
        summary=record_data.get("summary") or "",
        meals=record_data.get("meals") or []
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return serialize_daily_record(record)


def bulk_import_daily_records(db: Session, records_data):
    imported = 0

    for record_data in records_data:
        append_daily_record(db, record_data)
        imported += 1

    return imported


def clear_daily_records(db: Session):
    db.query(DailyRecord).delete()
    db.commit()
