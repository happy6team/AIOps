# main.py
from fastapi import FastAPI

import asyncio
from monitor.scheduler import predict_each_row_periodically, evaluate_and_retrain, periodic_task
from config.config import GNERATE_DATA_SOURCE_PATH, DATA_SOURCE_PATH
import pandas as pd

import logging

from config.db_config import async_engine
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from api.routers import sensor_data
from loader.init_data_loader import load_csv_to_db, init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 애플리케이션 시작 시 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="AIOps API", 
    description="AIOps 미니 프로젝트 API 명세서입니다.(수정 필요)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def welcome():
    return {"message": "Welcome to the FastAPI server!"}

app.include_router(sensor_data.router)

@app.on_event("startup")
async def startup():
    try:
        # 테이블 생성
        await init_db(async_engine)

        # 초기 데이터 자동 생성
        await load_csv_to_db(DATA_SOURCE_PATH)
        
        # 데이터 로드
        database = pd.read_csv(GNERATE_DATA_SOURCE_PATH)

        if database.empty:
            print("데이터가 없습니다.")
            return

        # 각 행을 5초 간격으로 순차 예측 
        # -> 실제 상황에서는 10분에 한 번씩 (10분~1시간) :
        asyncio.create_task(predict_each_row_periodically(database, 5))

        # 24시간마다 평가 및 재학습
        # asyncio.create_task(periodic_task(evaluate_and_retrain, 86400))
        # 20초마다 결과 확인
        # -> 실제 상황에서는 하루 한 번씩(ex. 자정)
        asyncio.create_task(periodic_task(evaluate_and_retrain, 20)) 

    except Exception as e:
        print(f"시작 이벤트 중 오류 발생: {e}")