from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_daily import router as daily_record_router
from app.api.routes_food import router as food_router
from app.api.routes_recommend import router as recommend_router

app = FastAPI(title="To-Eat-List API")

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
app.include_router(daily_record_router)
