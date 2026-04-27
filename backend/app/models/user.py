# user.py

from sqlalchemy import Column, Integer, String

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), nullable=True)
    taste_preference = Column(String(100), nullable=True)
    dislike_food = Column(String(200), nullable=True)
    spicy_level = Column(String(20), nullable=True)
    milk_tea_limit_per_week = Column(Integer, nullable=True)
    health_goal = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)