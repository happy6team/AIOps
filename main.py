# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from api.schemas.sensor_data import SensorDataCreate
from cruds.sensordata import create_sensor_data

import asyncio
from monitor.scheduler import predict_failures, evaluate_and_retrain, periodic_task

app = FastAPI()

@app.post("/sensor-data", summary="센서 데이터 저장")
async def post_sensor_data(data: SensorDataCreate, db: AsyncSession = Depends(get_db)):
    saved = await create_sensor_data(db, data)
    return {
        "message": "✅ 센서 데이터가 저장되었습니다.",
        "collection_time": saved.collection_time,
        "fail": saved.fail,
        "fail_probability": saved.fail_probability
    }

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_task(predict_failures(), 5)) # 5초 마다 
    asyncio.create_task(periodic_task(evaluate_and_retrain(), 86400)) # 24시간 마다