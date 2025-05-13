# main.py
from fastapi import FastAPI

import asyncio
from monitor.scheduler import predict_each_row_periodically, evaluate_and_retrain, periodic_task
from config.config import GNERATE_DATA_SOURCE_PATH
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup():
    try:
        # 데이터 로드
        database = pd.read_csv(GNERATE_DATA_SOURCE_PATH)

        if database.empty:
            print("데이터가 없습니다.")
            return

        # 각 행을 5초 간격으로 순차 예측
        asyncio.create_task(predict_each_row_periodically(database, 5))

        # 24시간마다 평가 및 재학습
        # asyncio.create_task(periodic_task(evaluate_and_retrain, 86400))
        asyncio.create_task(periodic_task(evaluate_and_retrain, 20)) # 20초마다 결과 확인

    except Exception as e:
        print(f"시작 이벤트 중 오류 발생: {e}")