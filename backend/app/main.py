# main.py

from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.api.routes_user import router as user_router
from app.db.init_db import init_db

app = FastAPI(title="To-Eat-List API")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health_router)
app.include_router(user_router)