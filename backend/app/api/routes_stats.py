from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stats import OverviewStatsResponse
from app.services.daily_record_store import count_daily_records
from app.services.food_store import count_foods

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=OverviewStatsResponse)
def get_overview_stats(db: Session = Depends(get_db)):
    return {
        "food_count": count_foods(db),
        "history_count": count_daily_records(db),
    }
