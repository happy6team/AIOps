from config.db_config import AsyncSessionLocal
from api.models.sensor_data import SensorData
from sqlalchemy import select
import asyncio
import sys

async def test_db_connection():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                SensorData.__table__.select().limit(5)
            )
            rows = result.fetchall()
            for row in rows:
                print(f"[✔] 시간: {row.collection_time}, 고장 여부: {row.fail}")
        except Exception as e:
            print(f"[❌] DB 연결 또는 쿼리 실패: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_db_connection())
    finally:
        # Windows 환경에서 event loop 닫힘 오류 방지
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())