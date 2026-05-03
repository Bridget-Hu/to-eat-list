from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.daily_record import DailyRecordListResponse
from app.services.daily_record_store import clear_daily_records, count_daily_records, load_daily_records

router = APIRouter(prefix="/daily-records", tags=["daily-records"])


@router.get("", response_model=DailyRecordListResponse)
def get_daily_records(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    records = load_daily_records(db, limit=limit)

    return {
        "count": count_daily_records(db),
        "data": records
    }


@router.delete("")
def delete_daily_records(db: Session = Depends(get_db)):
    clear_daily_records(db)

    return {
        "message": "历史记录已清空"
    }
