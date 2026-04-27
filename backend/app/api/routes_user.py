# routes_user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPreferenceCreate, UserPreferenceResponse

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/preferences", response_model=UserPreferenceResponse)
def create_user_preferences(
    data: UserPreferenceCreate,
    db: Session = Depends(get_db),
):
    user = User(
        nickname=data.nickname,
        taste_preference=data.taste_preference,
        dislike_food=data.dislike_food,
        spicy_level=data.spicy_level,
        milk_tea_limit_per_week=data.milk_tea_limit_per_week,
        health_goal=data.health_goal,
        email=data.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/preferences/{user_id}", response_model=UserPreferenceResponse)
def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User preference not found")
    return user