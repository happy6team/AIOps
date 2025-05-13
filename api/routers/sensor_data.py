from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
import os
from config.db_config import get_db
from api.cruds import sensor_data as cruds
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# 예시 코드 입니다. import가 안되어 있을지도
router = APIRouter(
    prefix="/sensor-data",
    tags=["센서 데이터 관리"])


# 실시간 데이터 스트림 가져오는 api : 가장 최근거 하나 가져옴
@router.get("/latest")
async def get_latest_sensor_data(db: AsyncSession = Depends(get_db)):
    return await cruds.get_latest_sensor_data(db)

# 데이터 상세 분석 그래프 조회
@router.get("")
async def get_sensor_data_list(
    start_date: datetime = Query(..., description="시작 날짜/시간 (YYYY-MM-DD HH:MM:SS 형식)"),
    end_date: datetime = Query(..., description="종료 날짜/시간 (YYYY-MM-DD HH:MM:SS 형식)"),
    db: AsyncSession = Depends(get_db)):
    return await cruds.get_sensor_data_by_date_range(db, start_date, end_date)