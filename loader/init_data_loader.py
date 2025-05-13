import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists
from config.db_config import Base, AsyncSessionLocal
from api.models.sensor_data import SensorData
from sqlalchemy.ext.asyncio import AsyncEngine


# 1. 테이블이 존재하지 않으면 생성
async def init_db(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 2. 중복 없이 한 행 삽입
async def insert_row_if_not_exists(session: AsyncSession, row: dict):
    # 중복 기준: collection_time
    stmt = select(exists().where(SensorData.collection_time == row['collection_time']))
    result = await session.execute(stmt)
    exists_flag = result.scalar()

    if not exists_flag:
        data = SensorData(**row)
        session.add(data)
        return 1  # 성공
    return 0  # 중복

# 3. 전체 CSV 로드 및 삽입
async def load_csv_to_db(csv_path):
    df = pd.read_csv(csv_path)
    
    # 컬럼 정제
    df.rename(columns={
        'tempMode': 'temp_mode',
        'Temperature': 'temperature'
    }, inplace=True)

    # 시간 컬럼 datetime 변환
    df['collection_time'] = pd.to_datetime(df['collection_time'])

    async with AsyncSessionLocal() as session:
        inserted = 0
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict = {k: None if pd.isna(v) else v for k, v in row_dict.items()}
            inserted += await insert_row_if_not_exists(session, row_dict)
        await session.commit()
        print(f"총 {inserted}건의 새 데이터가 삽입되었습니다.")