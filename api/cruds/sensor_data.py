from api.models.sensor_data import SensorData
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
# from sqlalchemy import select
from api.schemas.sensor_data import SensorDataCreate

# 새로운 센서 데이터 추가
async def create_sensor_data(db: AsyncSession, data: SensorDataCreate):
    new_entry = SensorData(**data.dict())
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

# limit 기준으로 센서 데이터 불러오기 
async def get_all_sensor_data(db: AsyncSession, limit: int):
    stmt = select(SensorData).order_by(SensorData.collection_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# (start_date, end_date) 기간동안의 데이터 조회
async def get_sensor_data_by_date_range(db: AsyncSession, start_date: datetime, end_date: datetime):
    stmt = select(SensorData).where(
        and_(
            SensorData.collection_time >= start_date,
            SensorData.collection_time <= end_date
        )
    ).order_by(SensorData.collection_time.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

# 가장 최근 데이터 하나 가져옴
async def get_latest_sensor_data(db: AsyncSession):
    stmt = select(SensorData).order_by(SensorData.collection_time.desc()).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first()
