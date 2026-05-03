from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.types import JSON

from app.db.session import Base


class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    budget = Column(Float, nullable=False, default=0)
    goal = Column(String(50), nullable=True)
    taste = Column(String(120), nullable=True)
    dislike = Column(String(120), nullable=True)
    want = Column(String(120), nullable=True)
    had_milk_tea = Column(Boolean, nullable=False, default=False)
    total_price = Column(Float, nullable=False, default=0)
    remaining_budget = Column(Float, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    meals = Column(JSON, nullable=False, default=list)
