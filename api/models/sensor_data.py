from sqlalchemy import Column, Integer, Float, Boolean, DateTime
from api.config.db_config import Base

class SensorData(Base):
    __tablename__ = "sensor_data"
    collection_time = Column(DateTime, primary_key=True)  # 센서 데이터 수집 시간 (PK)
    footfall = Column(Integer)                            # 지나가는 사람 수
    temp_mode = Column(Integer)                           # 온도 모드
    AQ = Column(Float)                                    # 공기질 지수
    USS = Column(Float)                                   # 초음파 센서 값
    CS = Column(Float)                                    # 전류 센서 값
    VOC = Column(Float)                                   # 휘발성 유기 화합물
    RP = Column(Float)                                    # 회전 위치 또는 RPM
    IP = Column(Float)                                    # 입력 압력
    temperature = Column(Float)                           # 작동 온도
    fail = Column(Boolean)                                # 고장 여부 (0: 정상, 1: 고장)
    fail_probability = Column(Float)                    # 고장 확률 (0~1)