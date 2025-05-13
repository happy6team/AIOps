from api.models.sensor_data import SensorData
# from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.sensor_data import SensorDataCreate

# limit 기준으로 센서 데이터 불러오기 
async def get_all_sensor_data(db: AsyncSession, limit: int):
    stmt = select(SensorData).order_by(SensorData.collection_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 새로운 센서 데이터 추가
async def create_sensor_data(db: AsyncSession, data: SensorDataCreate):
    new_entry = SensorData(**data.dict())
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)