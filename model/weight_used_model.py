# weight_used_model.py
# 학습된 모델을 가져와 예측 결과 반환
# 5초에 한번 실행

import joblib
import pandas as pd

from model.refit_model import load_model

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 경로 설정
MODEL_PATH = "model/result/saved_model.joblib"
SCALER_PATH = "model/result/scaler.joblib"

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

    X = pd.DataFrame([data])
    X['collection_time'] = pd.to_datetime(X['collection_time'])
    X = X.sort_values(by="collection_time")

    # 시간 정보 컬럼 추가
    X["hour"] = X["collection_time"].dt.hour
    X["dayofweek"] = X["collection_time"].dt.dayofweek
    X["is_weekend"] = (X["dayofweek"] >= 5).astype(int)

    X = X.drop(columns=["collection_time"])

    # 스케일링
    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(X)

    # 확률 예측
    probability = model.predict_proba(X_scaled)[:, 1]

    # 사용자 정의 threshold 적용
    threshold = 0.7
    y_pred = (probability >= threshold).astype(int)

    print(f'고장 발생 확률: {probability[0]:.4f}')
    print(f'예측된 클래스 (0: 고장 없음, 1: 고장 발생): {y_pred[0]}')

    return y_pred[0], probability[0]
