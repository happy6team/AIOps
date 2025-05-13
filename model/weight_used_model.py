# weight_used_model.py
# 학습된 모델을 가져와 예측 결과 반환
# 5초에 한번 실행

import joblib
import pandas as pd
from datetime import datetime, timedelta

from refit_model import load_model

# 경로 설정
MODEL_PATH = "model/result/saved_model.joblib"
SCALER_PATH = "model/result/scaler.joblib"

# 모델 예측 및 결과
def predict_and_result(dataset):
    # 모델 로드
    model = load_model(MODEL_PATH)

    # 시계열 컬럼 제거
    X = dataset.copy()

    # 시간 처리
    X["collection_time"] = pd.to_datetime(X["collection_time"])
    X = X.sort_values("collection_time")

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

    return y_pred, probability  # 예측 결과, 고장 발생 확률 반환