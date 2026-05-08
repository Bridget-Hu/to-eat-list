from types import SimpleNamespace

from app.services.recommendation_service import generate_recommendations
from app.utils.keyword_normalizer import normalize_keywords


def test_normalize_keywords_supports_common_separators_and_synonyms():
    assert normalize_keywords("清淡,微辣") == ["清淡", "辣"]
    assert normalize_keywords("清淡、微辣") == ["清淡", "辣"]
    assert normalize_keywords("清淡 微辣") == ["清淡", "辣"]
    assert normalize_keywords("奶茶；米饭；拉面") == ["饮品", "主食", "面食"]


def test_generate_recommendations_returns_scores_reasons_and_avoids_severe_keywords(client):
    foods = [
        {
            "name": "牛肉鸡蛋蛋白饭",
            "store": "一楼轻食",
            "price": 22,
            "category": "午餐",
            "taste_tags": "咸香",
            "health_tags": "高蛋白、低脂",
            "note": "牛肉、鸡蛋、主食充足",
        },
        {
            "name": "珍珠奶茶",
            "store": "饮品档口",
            "price": 13,
            "category": "饮品",
            "taste_tags": "甜",
            "health_tags": "高糖",
            "note": "奶茶饮品",
        },
        {
            "name": "香菜海鲜面",
            "store": "二楼面档",
            "price": 19,
            "category": "午餐",
            "taste_tags": "鲜香",
            "health_tags": "海鲜",
            "note": "含香菜和虾",
        },
    ]

    for food in foods:
        response = client.post("/foods", json=food)
        assert response.status_code == 200

    response = client.post(
        "/recommendations/generate",
        json={
            "budget": 60,
            "taste_preferences": "咸香",
            "avoid_keywords": "香菜, 海鲜",
            "health_goal": "高蛋白",
            "craving": "牛肉",
            "has_milk_tea": True,
        },
    )

    assert response.status_code == 200

    body = response.json()
    names = [item["name"] for item in body["recommendations"]]

    assert body["recommendations"][0]["name"] == "牛肉鸡蛋蛋白饭"
    assert body["recommendations"][0]["score"] > 0
    assert any("高蛋白" in reason for reason in body["recommendations"][0]["reasons"])
    assert any("牛肉" in reason for reason in body["recommendations"][0]["reasons"])
    assert "香菜海鲜面" not in names
    assert body["total_estimated_price"] == body["totalPrice"]


def test_frequency_weight_can_raise_similar_food_ranking():
    foods = [
        {
            "id": 1,
            "name": "普通肥牛饭",
            "store": "一楼",
            "price": 25,
            "category": "午餐",
            "taste_tags": "咸香",
            "health_tags": "米饭",
            "note": "常规选择",
            "frequency_weight": 1.0,
        },
        {
            "id": 2,
            "name": "偏爱肥牛饭",
            "store": "一楼",
            "price": 25,
            "category": "午餐",
            "taste_tags": "咸香",
            "health_tags": "米饭",
            "note": "常规选择",
            "frequency_weight": 2.5,
        },
    ]
    data = SimpleNamespace(
        budget=60,
        taste="咸香",
        dislike="",
        want="肥牛",
        goal="",
        hadMilkTea=False,
    )

    recommendation = generate_recommendations(data, foods)

    assert recommendation["recommendations"][0]["name"] == "偏爱肥牛饭"
    assert any(
        "推荐权重" in reason
        for reason in recommendation["recommendations"][0]["reasons"]
    )


def test_generate_recommendations_returns_multiple_options_per_meal_type():
    foods = [
        {
            "id": index,
            "name": f"早餐候选{index}",
            "price": 3 + index,
            "category": "早餐",
            "taste_tags": "清淡",
            "health_tags": "早餐",
            "note": "早餐",
            "frequency_weight": 1.0,
        }
        for index in range(1, 5)
    ]
    data = SimpleNamespace(
        budget=60,
        taste="清淡",
        dislike="",
        want="早餐",
        goal="",
        hadMilkTea=False,
    )

    recommendation = generate_recommendations(data, foods)
    breakfast_options = [
        meal for meal in recommendation["meals"] if meal["type"] == "早餐"
    ]

    assert len(breakfast_options) == 3
    assert [meal["rank"] for meal in breakfast_options] == [1, 2, 3]
