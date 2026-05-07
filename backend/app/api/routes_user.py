from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserPreferenceCreate, UserPreferenceResponse
from app.services.user_preference_service import (
    get_latest_user_preference,
    save_user_preference,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/preferences", response_model=UserPreferenceResponse)
def create_user_preferences(
    data: UserPreferenceCreate,
    db: Session = Depends(get_db),
):
    return save_user_preference(db, data)


@router.get("/preferences/latest", response_model=UserPreferenceResponse)
def get_latest_preferences(db: Session = Depends(get_db)):
    preference = get_latest_user_preference(db)

    if preference is None:
        raise HTTPException(status_code=404, detail="还没有保存过用户偏好。")

    return preference
