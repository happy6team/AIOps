from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

# 예시 코드 입니다. import가 안되어 있을지도
router = APIRouter(
    prefix="/file",
    tags=["데이터 파일 관리"])

@router.get("/download")
async def download():
    try:
        img_name = os.path.join(IMAGE_DIR, weight_used_model.get_stock_png())
        return FileResponse(path=img_name, media_type='application/octet-stream', filename="stock.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

