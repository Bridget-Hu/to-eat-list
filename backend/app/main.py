from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_daily import router as daily_record_router
from app.api.routes_food import router as food_router
from app.api.routes_recommend import generate_router, router as recommend_router
from app.api.routes_stats import router as stats_router
from app.api.routes_user import router as user_router
from app.db.init_db import init_db
from app.services.bootstrap_service import bootstrap_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    bootstrap_database()
    yield


app = FastAPI(title="To-Eat-List API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["health"])
def ping():
    return {"message": "pong"}


app.include_router(food_router)
app.include_router(recommend_router)
app.include_router(generate_router)
app.include_router(daily_record_router)
app.include_router(stats_router)
app.include_router(user_router)
