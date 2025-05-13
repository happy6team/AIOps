# weight_used_model.py
# 학습된 모델을 가져와 예측 결과 반환
# 5초에 한번 실행

import joblib
import pandas as pd
from datetime import datetime, timedelta

from model.refit_model import load_model

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 경로 설정
MODEL_PATH = "model/result/saved_model.joblib"
SCALER_PATH = "model/result/scaler.joblib"

# 모델 예측 및 결과
def predict_and_result(dataset) -> (bool, float):
    # 모델 로드
    model = load_model(MODEL_PATH)

    data = {
    "footfall": dataset.iloc[0],
    "tempMode": dataset.iloc[1],
    "AQ": dataset.iloc[2],
    "USS": dataset.iloc[3],
    "CS": dataset.iloc[4],
    "VOC": dataset.iloc[5],
    "RP": dataset.iloc[6],
    "IP": dataset.iloc[7],
    "Temperature": dataset.iloc[8],
    "collection_time": dataset.iloc[9]
    }

    # 시계열 컬럼 처리
    X = pd.DataFrame([data])

    # 'collection_time'을 datetime 형식으로 변환
    X['collection_time'] = pd.to_datetime(X['collection_time'])

    # 'collection_time' 기준으로 데이터 정렬
    X = X.sort_values(by="collection_time")

    # 컬럼 변환 (필요한 특성만 사용)
    X["hour"] = X["collection_time"].dt.hour
    X["dayofweek"] = X["collection_time"].dt.dayofweek
    X["is_weekend"] = (X["dayofweek"] >= 5).astype(int)
    
    # 시계열 컬럼 제거
    X = X.drop(columns=["collection_time"])

    # 스케일링
    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(X)

    # 확률 예측
    probability = model.predict_proba(X_scaled)[:, 1]

    # 모델 예측
    y_pred = model.predict(X_scaled)

    # 출력
    print(f'고장 발생 확률: {probability[0]:.4f}')
    print(f'예측된 클래스 (0: 고장 없음, 1: 고장 발생): {y_pred[0]}')

    return y_pred[0], probability[0]  # 예측 결과, 고장 발생 확률 반환