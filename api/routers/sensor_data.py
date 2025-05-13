from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from config.db_config import get_db
from api.cruds import sensor_data as cruds
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.sensor_data import SensorDataCreate
from crud.sensor_data import create_sensor_data

# 예시 코드 입니다. import가 안되어 있을지도
router = APIRouter(
    prefix="/sensor-data",
    tags=["센서 데이터 관리"])

@router.get("")
async def get_sensor_data_list(limit: int = 100, db: Session = Depends(get_db)):
    return await cruds.get_all_sensor_data(db, limit)

# POST: 센서 데이터 저장
@router.post("", summary="센서 데이터 저장")
async def post_sensor_data(data: SensorDataCreate, db: AsyncSession = Depends(get_db)):
    saved = await create_sensor_data(db, data)
    return {
        "message": "✅ 센서 데이터가 성공적으로 저장되었습니다.",
        "data": {
            "collection_time": saved.collection_time,
            "fail": saved.fail,
            "fail_probability": saved.fail_probability
        }
    }