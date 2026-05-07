from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.db.session import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    budget = Column(Float, nullable=False, default=0)
    taste = Column(String(120), nullable=True)
    dislike = Column(String(240), nullable=True)
    goal = Column(String(50), nullable=True)
    had_milk_tea = Column(Boolean, nullable=False, default=False)
    want = Column(String(120), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
