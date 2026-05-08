from datetime import date, datetime, time, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.daily_record import DailyRecord


def _date_start(value: date | None):
    if value is None:
        return None

    return datetime.combine(value, time.min).replace(tzinfo=timezone.utc)


def _date_end(value: date | None):
    if value is None:
        return None

    return datetime.combine(value, time.max).replace(tzinfo=timezone.utc)


def _extract_actual_choice(record_data):
    return (
        record_data.get("actualChoice")
        or record_data.get("actual_choice")
        or record_data.get("finalChoice")
        or record_data.get("final_choice")
        or record_data.get("selectedFood")
        or record_data.get("selected_food")
        or record_data.get("chosenFood")
        or record_data.get("chosen_food")
        or ""
    )


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
        "actualChoice": record.actual_choice or "",
        "meals": record.meals or []
    }


def _daily_record_query(db: Session, start_date: date | None = None, end_date: date | None = None):
    query = db.query(DailyRecord)
    start_at = _date_start(start_date)
    end_at = _date_end(end_date)

    if start_at is not None:
        query = query.filter(DailyRecord.created_at >= start_at)

    if end_at is not None:
        query = query.filter(DailyRecord.created_at <= end_at)

    return query


def load_daily_records(
    db: Session,
    limit=100,
    start_date: date | None = None,
    end_date: date | None = None,
):
    records = (
        _daily_record_query(db, start_date=start_date, end_date=end_date)
        .order_by(DailyRecord.created_at.desc(), DailyRecord.id.desc())
        .limit(limit)
        .all()
    )

    return [serialize_daily_record(record) for record in records]


def count_daily_records(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
):
    return _daily_record_query(db, start_date=start_date, end_date=end_date).count()


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
        actual_choice=_extract_actual_choice(record_data),
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


def update_daily_record_actual_choice(db: Session, record_id: int, actual_choice: str | None):
    record = db.query(DailyRecord).filter(DailyRecord.id == record_id).first()

    if record is None:
        raise HTTPException(status_code=404, detail="历史记录不存在。")

    record.actual_choice = (actual_choice or "").strip()
    db.commit()
    db.refresh(record)

    return serialize_daily_record(record)
