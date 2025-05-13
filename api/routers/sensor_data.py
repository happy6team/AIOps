from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from config.db_config import get_db
from api.cruds import sensor_data as cruds
from sqlalchemy.orm import Session

# 예시 코드 입니다. import가 안되어 있을지도
router = APIRouter(
    prefix="/sensor-data",
    tags=["센서 데이터 관리"])

@router.get("")
async def get_sensor_data_list(limit: int = 100, db: Session = Depends(get_db)):
    return await cruds.get_all_sensor_data(db, limit)

