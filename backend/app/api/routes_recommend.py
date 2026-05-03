from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.services.daily_record_store import append_daily_record
from app.services.food_store import load_foods
from app.services.recommendation_service import build_recommendation

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post("/daily", response_model=RecommendResponse)
def recommend_daily(
    data: RecommendRequest,
    db: Session = Depends(get_db)
):
    foods = load_foods(db)

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="还没有正式菜品数据，请先上传菜品文件或导入示例 JSON 数据。"
        )

    recommendation = build_recommendation(data, foods)

    saved_record = append_daily_record(db, {
        "budget": recommendation["budget"],
        "goal": data.goal or "",
        "taste": data.taste or "",
        "dislike": data.dislike or "",
        "want": data.want or "",
        "hadMilkTea": bool(data.hadMilkTea),
        "totalPrice": recommendation["totalPrice"],
        "remainingBudget": recommendation["remainingBudget"],
        "summary": recommendation["summary"],
        "meals": recommendation["meals"]
    })

    meals = recommendation["meals"]

    return {
        "breakfast": meals[0]["name"],
        "breakfastReason": meals[0]["reason"],
        "lunch": meals[1]["name"],
        "lunchReason": meals[1]["reason"],
        "dinner": meals[2]["name"],
        "dinnerReason": meals[2]["reason"],
        "summary": recommendation["summary"],
        "totalPrice": recommendation["totalPrice"],
        "remainingBudget": recommendation["remainingBudget"],
        "recordId": saved_record["id"],
        "createdAt": saved_record["createdAt"],
        "meals": meals
    }
