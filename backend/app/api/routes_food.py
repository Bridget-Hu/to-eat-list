from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.food_store import load_foods, import_foods_from_text, clear_foods

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("")
def get_foods():
    foods = load_foods()

    return {
        "count": len(foods),
        "data": foods
    }


@router.delete("")
def delete_foods():
    clear_foods()

    return {
        "message": "菜品数据已清空"
    }


@router.post("/upload")
async def upload_food_file(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not filename.endswith((".txt", ".csv", ".doc", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="暂时只支持 txt / csv / doc / docx 文件"
        )

    content = await file.read()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("gbk", errors="ignore")

    foods = import_foods_from_text(text)

    if not foods:
        raise HTTPException(
            status_code=400,
            detail="没有解析到有效菜品，请检查文件格式"
        )

    return {
        "message": "菜品导入成功",
        "count": len(foods),
        "data": foods
    }
