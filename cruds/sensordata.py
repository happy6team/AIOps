from api.models.sensor_data import SensorData
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas.sensor_data import SensorDataCreate
import asyncio
from config.db_config import AsyncSessionLocal

# 전체 센서 데이터 불러오기 
async def get_all_sensor_data(db: AsyncSession):
    stmt = select(SensorData).order_by(SensorData.collection_time.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

# 새로운 센서 데이터 추가
async def create_sensor_data(db: AsyncSession, data: SensorDataCreate):
    new_entry = SensorData(**data.dict())
    db.add(new_entry)
    await db.commit()
    return new_entry
    # await db.refresh(new_entry)

# 테스트 실행 함수
async def main():
    print("센서 데이터 불러오기 테스트 시작...")

    try:
        # 기존 db_config에서 세션 생성
        async with AsyncSessionLocal() as session:
            print("데이터베이스 연결 성공")
            print("센서 데이터 쿼리 실행 중...")
            
            # 데이터 가져오기
            sensor_data = await get_all_sensor_data(session)
            
            # 결과 출력
            print(f"총 {len(sensor_data)}개의 센서 데이터를 가져왔습니다.")

            # 첫 번째 데이터만 상세 출력
            if sensor_data and len(sensor_data) > 0:
                first_data = sensor_data[0]
                print("\n첫 번째 데이터 상세 정보:")
                print(f"  수집 시간: {first_data.collection_time}")
                print(f"  통행량: {first_data.footfall if hasattr(first_data, 'footfall') else 'N/A'}")
                print(f"  온도 모드: {first_data.temp_mode if hasattr(first_data, 'temp_mode') else 'N/A'}")
                print(f"  공기질(AQ): {first_data.AQ if hasattr(first_data, 'AQ') else 'N/A'}")
                print(f"  초음파 센서(USS): {first_data.USS if hasattr(first_data, 'USS') else 'N/A'}")
                print(f"  전류 센서(CS): {first_data.CS if hasattr(first_data, 'CS') else 'N/A'}")
                print(f"  휘발성 유기 화합물(VOC): {first_data.VOC if hasattr(first_data, 'VOC') else 'N/A'}")
                print(f"  회전 위치(RP): {first_data.RP if hasattr(first_data, 'RP') else 'N/A'}")
                print(f"  입력 압력(IP): {first_data.IP if hasattr(first_data, 'IP') else 'N/A'}")
                print(f"  온도: {first_data.temperature if hasattr(first_data, 'temperature') else 'N/A'}")
                print(f"  고장 여부: {'예' if first_data.fail else '아니오' if hasattr(first_data, 'fail') else 'N/A'}")
                # 고장 확률 필드에 대한 안전한 출력
                fail_prob = first_data.fail_probability if hasattr(first_data, 'fail_probability') else None
                if fail_prob is not None:
                    print(f"  고장 확률: {fail_prob:.4f}")
                else:
                    print("  고장 확률: N/A")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

# 스크립트가 직접 실행될 때만 main() 호출
if __name__ == "__main__":
    # 비동기 함수 실행
    asyncio.run(main())