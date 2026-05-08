from datetime import datetime
from pathlib import Path

import pytest

from app.services.legacy_data_loader import load_legacy_foods

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def import_sample_foods(client):
    response = client.post("/foods/import-sample")

    assert response.status_code == 200

    return response.json()


def upload_fixture_foods(client, fixture_name):
    fixture_path = FIXTURES_DIR / fixture_name
    response = client.post(
        "/foods/upload",
        files={
            "file": (
                fixture_path.name,
                fixture_path.read_bytes(),
                "application/json",
            )
        },
    )

    assert response.status_code == 200

    return response.json()


def test_import_sample_json(client):
    expected_foods = load_legacy_foods()
    response_body = import_sample_foods(client)

    assert response_body["count"] == len(expected_foods)
    assert len(response_body["data"]) == len(expected_foods)
    assert [food["name"] for food in response_body["data"]] == [
        food["name"] for food in expected_foods
    ]

    foods_response = client.get("/foods")

    assert foods_response.status_code == 200
    assert foods_response.json() == {
        "count": len(expected_foods),
        "data": response_body["data"],
    }


def test_user_preferences_can_be_saved_and_latest_can_be_loaded(client):
    empty_response = client.get("/user/preferences/latest")

    assert empty_response.status_code == 404

    payload = {
        "budget": 48,
        "taste": "清淡",
        "dislike": "香菜",
        "goal": "减脂",
        "hadMilkTea": True,
        "want": "米饭",
    }

    create_response = client.post("/user/preferences", json=payload)

    assert create_response.status_code == 200

    created = create_response.json()

    assert created["budget"] == pytest.approx(payload["budget"])
    assert created["taste"] == payload["taste"]
    assert created["dislike"] == payload["dislike"]
    assert created["goal"] == payload["goal"]
    assert created["hadMilkTea"] is payload["hadMilkTea"]
    assert created["want"] == payload["want"]
    assert created["createdAt"]
    assert created["updatedAt"]

    latest_response = client.get("/user/preferences/latest")

    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == created["id"]


def test_upload_food_file_imports_rows(client):
    csv_text = "\n".join(
        [
            "name,category,price,taste,tags,note",
            "Protein Oats,Breakfast,8.5,light,high-protein,quick breakfast",
            "Chicken Bowl,Lunch,18.0,savory,lean,post-workout lunch",
            "Salmon Salad,Dinner,22.0,fresh,light,balanced dinner",
        ]
    )

    response = client.post(
        "/foods/upload",
        files={"file": ("foods.csv", csv_text.encode("utf-8"), "text/csv")},
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["count"] == 3
    assert [food["name"] for food in response_body["data"]] == [
        "Protein Oats",
        "Chicken Bowl",
        "Salmon Salad",
    ]
    assert [food["category"] for food in response_body["data"]] == [
        "Breakfast",
        "Lunch",
        "Dinner",
    ]

    foods_response = client.get("/foods")

    assert foods_response.status_code == 200
    assert foods_response.json() == {
        "count": 3,
        "data": response_body["data"],
    }


def test_food_crud_supports_validation_update_and_delete(client):
    create_payload = {
        "name": "鸡胸能量碗",
        "store": "轻食窗口",
        "price": 19.5,
        "category": "主食",
        "taste_tags": "清淡,咸香",
        "health_tags": ["高蛋白", "低脂"],
        "note": "午餐常点",
    }

    create_response = client.post("/foods", json=create_payload)

    assert create_response.status_code == 200

    created_food = create_response.json()

    assert created_food["name"] == create_payload["name"]
    assert created_food["store"] == create_payload["store"]
    assert created_food["price"] == pytest.approx(create_payload["price"])
    assert created_food["taste_tags"] == "清淡、咸香"
    assert created_food["health_tags"] == "高蛋白、低脂"

    duplicate_response = client.post("/foods", json=create_payload)

    assert duplicate_response.status_code == 400
    assert "同名菜品" in duplicate_response.json()["detail"]

    invalid_price_response = client.post(
        "/foods",
        json={
            "name": "无效价格菜品",
            "price": 0,
            "category": "其他",
        },
    )

    assert invalid_price_response.status_code == 422

    update_response = client.put(
        f"/foods/{created_food['id']}",
        json={
            "price": 21.0,
            "store": "轻食二窗口",
            "health_tags": "高蛋白,蔬菜多",
        },
    )

    assert update_response.status_code == 200

    updated_food = update_response.json()

    assert updated_food["price"] == pytest.approx(21.0)
    assert updated_food["store"] == "轻食二窗口"
    assert updated_food["health_tags"] == "高蛋白、蔬菜多"

    list_response = client.get("/foods")

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    delete_response = client.delete(f"/foods/{created_food['id']}")

    assert delete_response.status_code == 200

    cleared_list_response = client.get("/foods")

    assert cleared_list_response.status_code == 200
    assert cleared_list_response.json() == {
        "count": 0,
        "data": [],
    }


def test_foods_can_be_batch_deleted(client):
    created_ids = []

    for name in ["豆浆", "包子", "肉肠"]:
        response = client.post(
            "/foods",
            json={
                "name": name,
                "price": 2,
                "category": "早餐",
            },
        )

        assert response.status_code == 200
        created_ids.append(response.json()["id"])

    response = client.post(
        "/foods/batch-delete",
        json={"ids": created_ids[:2]},
    )

    assert response.status_code == 200
    assert response.json()["deleted_count"] == 2

    list_response = client.get("/foods")

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["data"][0]["name"] == "肉肠"


def test_recommendation_persists_history_and_history_can_be_cleared(client):
    upload_response = upload_fixture_foods(client, "recommendation_foods.json")

    assert upload_response["count"] == 3
    assert [food["name"] for food in upload_response["data"]] == [
        "麦片鸡蛋杯",
        "香煎鸡胸饭",
        "清炒时蔬饭",
    ]

    payload = {
        "budget": 60,
        "taste": "清淡",
        "dislike": "辣",
        "want": "鸡",
        "goal": "减脂",
        "hadMilkTea": True,
    }

    response = client.post("/recommend/daily", json=payload)

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["recordId"] > 0
    assert response_body["createdAt"]
    assert len(response_body["meals"]) == 3
    assert response_body["breakfast"] == "麦片鸡蛋杯"
    assert response_body["lunch"] == "香煎鸡胸饭"
    assert response_body["dinner"] == "清炒时蔬饭"
    assert [meal["name"] for meal in response_body["meals"]] == [
        response_body["breakfast"],
        response_body["lunch"],
        response_body["dinner"],
    ]
    assert response_body["remainingBudget"] == pytest.approx(
        payload["budget"] - response_body["totalPrice"]
    )

    history_response = client.get("/daily-records")

    assert history_response.status_code == 200

    history_body = history_response.json()

    assert history_body["count"] == 1
    assert len(history_body["data"]) == 1

    record = history_body["data"][0]

    assert record["id"] == response_body["recordId"]
    assert record["createdAt"] == response_body["createdAt"]
    assert record["budget"] == pytest.approx(payload["budget"])
    assert record["goal"] == payload["goal"]
    assert record["taste"] == payload["taste"]
    assert record["dislike"] == payload["dislike"]
    assert record["want"] == payload["want"]
    assert record["hadMilkTea"] is payload["hadMilkTea"]
    assert record["summary"] == response_body["summary"]
    assert record["totalPrice"] == pytest.approx(response_body["totalPrice"])
    assert record["remainingBudget"] == pytest.approx(response_body["remainingBudget"])
    assert record["actualChoice"] == ""
    assert record["meals"] == response_body["meals"]

    record_date = datetime.fromisoformat(record["createdAt"]).date().isoformat()
    filtered_history_response = client.get(
        "/daily-records",
        params={
            "start_date": record_date,
            "end_date": record_date,
        },
    )

    assert filtered_history_response.status_code == 200
    assert filtered_history_response.json()["count"] == 1
    assert filtered_history_response.json()["data"][0]["id"] == record["id"]

    empty_filtered_history_response = client.get(
        "/daily-records",
        params={
            "start_date": "2999-01-01",
            "end_date": "2999-01-02",
        },
    )

    assert empty_filtered_history_response.status_code == 200
    assert empty_filtered_history_response.json() == {
        "count": 0,
        "data": [],
    }

    actual_choice_response = client.patch(
        f"/daily-records/{record['id']}/actual-choice",
        json={"actualChoice": "香煎鸡胸饭"},
    )

    assert actual_choice_response.status_code == 200
    assert actual_choice_response.json()["actualChoice"] == "香煎鸡胸饭"

    overview_response = client.get("/stats/overview")

    assert overview_response.status_code == 200
    assert overview_response.json() == {
        "food_count": 3,
        "history_count": 1,
    }

    clear_response = client.delete("/daily-records")

    assert clear_response.status_code == 200

    cleared_history_response = client.get("/daily-records")

    assert cleared_history_response.status_code == 200
    assert cleared_history_response.json() == {
        "count": 0,
        "data": [],
    }
