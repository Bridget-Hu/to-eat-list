# init_db.py

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine


def ensure_food_item_columns():
    inspector = inspect(engine)

    if "food_items" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("food_items")}
    statements = []

    if "store" not in columns:
        statements.append("ALTER TABLE food_items ADD COLUMN store VARCHAR(120)")

    if "taste_tags" not in columns:
        statements.append("ALTER TABLE food_items ADD COLUMN taste_tags VARCHAR(240)")

    if "health_tags" not in columns:
        statements.append("ALTER TABLE food_items ADD COLUMN health_tags VARCHAR(240)")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_food_item_columns()
