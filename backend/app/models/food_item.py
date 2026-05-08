from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.session import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    store = Column(String(120), nullable=True, index=True)
    category = Column(String(80), nullable=True, index=True)
    price = Column(Float, nullable=True)
    frequency_weight = Column(Float, nullable=False, default=1.0)
    taste = Column(String(120), nullable=True)
    tags = Column(String(240), nullable=True)
    taste_tags = Column(String(240), nullable=True)
    health_tags = Column(String(240), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
