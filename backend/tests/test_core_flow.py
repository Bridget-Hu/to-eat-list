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
    assert record["meals"] == response_body["meals"]

    clear_response = client.delete("/daily-records")

    assert clear_response.status_code == 200

    cleared_history_response = client.get("/daily-records")

    assert cleared_history_response.status_code == 200
    assert cleared_history_response.json() == {
        "count": 0,
        "data": [],
    }
