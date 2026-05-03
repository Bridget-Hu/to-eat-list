from fastapi import APIRouter, Query

from app.services.daily_record_store import (
    clear_daily_records,
    load_daily_records,
)

router = APIRouter(prefix="/daily-records", tags=["daily-records"])


@router.get("")
def get_daily_records(limit: int = Query(default=100, ge=1, le=500)):
    records = load_daily_records()

    return {
        "count": len(records),
        "data": records[:limit]
    }


@router.delete("")
def delete_daily_records():
    clear_daily_records()

    return {
      "message": "历史记录已清空"
    }
