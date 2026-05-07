from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.food_item import (
    FoodImportResponse,
    FoodItemCreate,
    FoodItemResponse,
    FoodItemUpdate,
    FoodListResponse,
)
from app.services.food_store import (
    clear_foods,
    create_food,
    delete_food,
    import_foods_from_text,
    load_foods,
    replace_foods,
    update_food,
)
from app.services.legacy_data_loader import load_legacy_foods

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("", response_model=FoodListResponse)
def get_foods(db: Session = Depends(get_db)):
    foods = load_foods(db)

    return {
        "count": len(foods),
        "data": foods,
    }


@router.post("", response_model=FoodItemResponse)
def create_food_item(data: FoodItemCreate, db: Session = Depends(get_db)):
    return create_food(db, data)


@router.put("/{food_id}", response_model=FoodItemResponse)
def update_food_item(food_id: int, data: FoodItemUpdate, db: Session = Depends(get_db)):
    return update_food(db, food_id, data)


@router.delete("/{food_id}")
def delete_food_item(food_id: int, db: Session = Depends(get_db)):
    delete_food(db, food_id)
    return {"message": "菜品已删除"}


@router.delete("")
def delete_foods(db: Session = Depends(get_db)):
    clear_foods(db)

    return {
        "message": "菜品数据已清空"
    }


@router.post("/import-sample", response_model=FoodImportResponse)
def import_sample_foods(db: Session = Depends(get_db)):
    foods = load_legacy_foods()

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="没有可导入的示例 JSON 菜品数据。"
        )

    saved_foods = replace_foods(db, foods)

    return {
        "message": "示例 JSON 菜品已导入到 SQLite",
        "count": len(saved_foods),
        "data": saved_foods
    }


@router.post("/upload", response_model=FoodImportResponse)
async def upload_food_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or ""

    if not filename.endswith((".txt", ".csv", ".json")):
        raise HTTPException(
            status_code=400,
            detail="暂时只支持 txt / csv / json 文件。"
        )

    content = await file.read()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("gbk", errors="ignore")

    foods = import_foods_from_text(text, filename=filename)

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="没有解析到有效菜品，请检查文件格式。"
        )

    saved_foods = replace_foods(db, foods)

    return {
        "message": "菜品已导入 SQLite",
        "count": len(saved_foods),
        "data": saved_foods
    }
