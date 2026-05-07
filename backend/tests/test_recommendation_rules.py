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
