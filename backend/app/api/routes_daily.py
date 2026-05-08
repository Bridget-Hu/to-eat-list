from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.daily_record import (
    DailyRecordActualChoiceUpdate,
    DailyRecordListResponse,
    DailyRecordResponse,
)
from app.services.daily_record_store import (
    clear_daily_records,
    count_daily_records,
    load_daily_records,
    update_daily_record_actual_choice,
)

router = APIRouter(prefix="/daily-records", tags=["daily-records"])


@router.get("", response_model=DailyRecordListResponse)
def get_daily_records(
    limit: int = Query(default=100, ge=1, le=500),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期。")

    records = load_daily_records(
        db,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "count": count_daily_records(db, start_date=start_date, end_date=end_date),
        "data": records
    }


@router.patch("/{record_id}/actual-choice", response_model=DailyRecordResponse)
def update_actual_choice(
    record_id: int,
    data: DailyRecordActualChoiceUpdate,
    db: Session = Depends(get_db),
):
    return update_daily_record_actual_choice(db, record_id, data.actualChoice)


@router.delete("")
def delete_daily_records(db: Session = Depends(get_db)):
    clear_daily_records(db)

    return {
        "message": "历史记录已清空"
    }
