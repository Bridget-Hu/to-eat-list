from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.daily_record_store import append_daily_record
from app.services.food_store import load_foods

router = APIRouter(prefix="/recommend", tags=["recommend"])


class RecommendRequest(BaseModel):
    budget: int | None = 60
    taste: str | None = ""
    dislike: str | None = ""
    want: str | None = ""
    goal: str | None = ""
    hadMilkTea: bool | None = False


def food_text(food):
    return (
        f"{food.get('name', '')} "
        f"{food.get('category', '')} "
        f"{food.get('taste', '')} "
        f"{food.get('tags', '')} "
        f"{food.get('note', '')}"
    )


def contains_any(text, keywords):
    return any(keyword and keyword in text for keyword in keywords)


def split_words(value):
    if not value:
        return []

    result = []

    for item in value.replace(",", "、").replace("，", "、").replace(" ", "、").split("、"):
        cleaned = item.strip()

        if cleaned:
            result.append(cleaned)

    return result


def score_food(food, meal_type, data):
    text = food_text(food)
    score = 0

    dislike_words = split_words(data.dislike)
    want_words = split_words(data.want)
    taste_words = split_words(data.taste)

    if contains_any(text, dislike_words):
        return -9999

    if data.hadMilkTea and ("奶茶" in text or "高糖" in text):
        return -9999

    category = food.get("category", "")

    if meal_type in category:
        score += 8

    if meal_type == "早餐" and contains_any(text, ["早餐", "豆浆", "粥", "鸡蛋", "三明治", "燕麦"]):
        score += 4

    if meal_type == "午餐" and contains_any(text, ["午餐", "盖饭", "米饭", "面", "饭"]):
        score += 4

    if meal_type == "晚餐" and contains_any(text, ["晚餐", "轻食", "时蔬", "拌饭", "汤"]):
        score += 4

    for word in want_words:
        if word in text:
            score += 10

    for word in taste_words:
        if word in text:
            score += 5

    if data.goal == "减脂":
        if contains_any(text, ["减脂", "低脂", "低油", "清淡", "轻食", "高蛋白"]):
            score += 8

        if contains_any(text, ["油炸", "高糖", "奶茶", "重口", "热量较高"]):
            score -= 6

    if data.goal == "增肌" and contains_any(text, ["增肌", "高蛋白", "鸡胸", "牛肉", "鸡蛋", "肉"]):
        score += 8

    price = food.get("price")
    budget = data.budget or 60

    if price is not None:
        if price <= budget / 3:
            score += 3
        elif price <= budget / 2:
            score += 1
        else:
            score -= 3

    return score


def choose_food(foods, meal_type, data, used_ids):
    available_foods = [
        food for food in foods
        if food.get("id") not in used_ids
    ]

    if not available_foods:
        return None

    ranked = sorted(
        available_foods,
        key=lambda food: score_food(food, meal_type, data),
        reverse=True
    )

    best_food = ranked[0]

    if score_food(best_food, meal_type, data) <= -9999:
        return None

    used_ids.add(best_food.get("id"))

    return best_food


def reason_for(food, meal_type, data):
    if not food:
        return f"没有找到适合{meal_type}的菜品，请重新导入更多菜品数据。"

    reasons = []
    text = food_text(food)

    if data.want and contains_any(text, split_words(data.want)):
        reasons.append("匹配了你今天突然很想吃的内容")

    if data.taste and contains_any(text, split_words(data.taste)):
        reasons.append("符合你的口味偏好")

    if data.goal == "减脂":
        reasons.append("尽量优先了清淡、低油或高蛋白方向")

    if data.goal == "增肌":
        reasons.append("优先考虑了蛋白质更充足的选择")

    if data.dislike:
        reasons.append("已避开你的忌口关键词")

    if not reasons:
        reasons.append("根据已导入菜品做了基础规则匹配")

    price = food.get("price")

    if price is not None:
        reasons.append(f"价格约 {price} 元")

    return "，".join(reasons) + "。"


def meal_payload(food, meal_type, data):
    return {
        "type": meal_type,
        "name": food["name"] if food else f"暂无合适{meal_type}",
        "reason": reason_for(food, meal_type, data),
        "price": food.get("price") if food else None
    }


@router.post("/daily")
def recommend_daily(data: RecommendRequest):
    foods = load_foods()

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="还没有导入菜品数据，请先去上传页导入菜品文件。"
        )

    used_ids = set()

    breakfast = choose_food(foods, "早餐", data, used_ids)
    lunch = choose_food(foods, "午餐", data, used_ids)
    dinner = choose_food(foods, "晚餐", data, used_ids)

    meals = [
        meal_payload(breakfast, "早餐", data),
        meal_payload(lunch, "午餐", data),
        meal_payload(dinner, "晚餐", data)
    ]

    total_price = round(
        sum(meal["price"] or 0 for meal in meals),
        2
    )
    budget = data.budget or 0
    remaining_budget = round(budget - total_price, 2)

    summary = (
        f"本次推荐基于已导入的 {len(foods)} 个菜品生成，"
        f"预计总价约 {total_price} 元，"
        f"预算为 {budget} 元，"
        f"结余约 {remaining_budget} 元。"
    )

    saved_record = append_daily_record({
        "budget": budget,
        "goal": data.goal or "",
        "taste": data.taste or "",
        "dislike": data.dislike or "",
        "want": data.want or "",
        "hadMilkTea": bool(data.hadMilkTea),
        "totalPrice": total_price,
        "remainingBudget": remaining_budget,
        "summary": summary,
        "meals": meals
    })

    return {
        "breakfast": meals[0]["name"],
        "breakfastReason": meals[0]["reason"],
        "lunch": meals[1]["name"],
        "lunchReason": meals[1]["reason"],
        "dinner": meals[2]["name"],
        "dinnerReason": meals[2]["reason"],
        "summary": summary,
        "totalPrice": total_price,
        "remainingBudget": remaining_budget,
        "recordId": saved_record["id"],
        "createdAt": saved_record["createdAt"]
    }
