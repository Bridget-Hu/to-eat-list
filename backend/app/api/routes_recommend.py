from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import RecommendRequest, RecommendResponse
from app.services.daily_record_store import append_daily_record
from app.services.food_store import load_foods
from app.services.recommendation_service import generate_recommendations

router = APIRouter(prefix="/recommend", tags=["recommend"])
generate_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _plain_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return "、".join(str(item).strip() for item in value if str(item).strip())

    return str(value).strip()


def _generate_and_save_recommendation(data: RecommendRequest, db: Session):
    foods = load_foods(db)

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="还没有正式菜品数据，请先上传菜品文件或导入示例 JSON 数据。",
        )

    recommendation = generate_recommendations(data, foods)

    saved_record = append_daily_record(db, {
        "budget": recommendation["budget"],
        "goal": _plain_text(data.goal),
        "taste": _plain_text(data.taste),
        "dislike": _plain_text(data.dislike),
        "want": _plain_text(data.want),
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
        "meals": meals,
        "recommendations": recommendation["recommendations"],
        "total_estimated_price": recommendation["total_estimated_price"],
        "generated_at": recommendation["generated_at"],
    }


@router.post("/daily", response_model=RecommendResponse)
def recommend_daily(
    data: RecommendRequest,
    db: Session = Depends(get_db),
):
    return _generate_and_save_recommendation(data, db)


@generate_router.post("/generate", response_model=RecommendResponse)
def generate_recommendation(
    data: RecommendRequest,
    db: Session = Depends(get_db),
):
    return _generate_and_save_recommendation(data, db)
