from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference
from app.schemas.user import UserPreferenceCreate


def save_user_preference(db: Session, data: UserPreferenceCreate):
    preference = UserPreference(
        budget=data.budget,
        taste=data.taste or "",
        dislike=data.dislike or "",
        goal=data.goal or "",
        had_milk_tea=bool(data.had_milk_tea),
        want=data.want or "",
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


def get_latest_user_preference(db: Session):
    return (
        db.query(UserPreference)
        .order_by(UserPreference.created_at.desc(), UserPreference.id.desc())
        .first()
    )
