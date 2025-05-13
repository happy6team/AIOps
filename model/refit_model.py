# model.py
# 기존에 저장된 모델을 가져와 재학습
# 24시간에 한번 실행 예정 

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# 경로 설정
MODEL_PATH = "model/result/saved_model.joblib"
SCALER_PATH = "model/result/scaler.joblib"
DATA_PATH = "model/result/data.csv"
THRESHOLD = 0.90  # 기준 정확도 -> 모델 최적화하면서 봐야함

# 모델 로드
def load_model(path=MODEL_PATH):
    if os.path.exists(path):
        return joblib.load(path)
    else:
        raise FileNotFoundError(f"{path}에 모델이 존재하지 않습니다.")

# 모델 저장
def save_model(model, path=MODEL_PATH):
    joblib.dump(model, path)
    print(f"모델이 저장되었습니다: {path}")

# 모델 재학습 및 평가
# ! 새로운 dataset을 DB에서 가져오는 건지 csv 파일을 읽어오는 건지 정확하지 않음
# ! 만약에 이 함수 그대로 사용할 거라면 dataset을 dataframe 형태로 입력하는 것을 권장
def train_and_evaluate(dataset, threshold=THRESHOLD):
    model = load_model(MODEL_PATH)

    # 시간 처리
    dataset["collection_time"] = pd.to_datetime(dataset["collection_time"])
    dataset = dataset.sort_values("collection_time")

    # 전처리
    n_dataset_test = len(dataset) // 8
    dataset_test = dataset.iloc[-n_dataset_test:]
    dataset_train_val = dataset.iloc[:-n_dataset_test]
    
    X_train_val = dataset_train_val.drop(columns=["fail"])
    y_train_val = dataset_train_val["fail"]

    # 테스트 데이터 준비
    X_test = dataset_test.drop(columns=["fail"])
    y_test = dataset_test["fail"]

    # 스케일링
    scaler = joblib.load(SCALER_PATH)
    X_train_val_scaled = scaler.fit_transform(X_train_val)
    X_test_scaled = scaler.transform(X_test)

    # 모델 재학습
    model.fit(X_train_val_scaled, y_train_val)

    # 모델 예측 및 평가
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"현재 모델 정확도: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    if acc >= threshold:
        save_model(model)
    else:
        print("기준 정확도 미달로 모델 저장이 생략되었습니다.")
    
    # 재학습하고 모델을 저장함으로 결과값 반환 X

# 데이터 로드
df = pd.read_csv(DATA_PATH)

# 시간 처리
df["collection_time"] = pd.to_datetime(df["collection_time"])
df = df.sort_values("collection_time")

# 데이터 전처리
n_total = len(df)
n_test = n_total // 8
df_test = df.iloc[-n_test:]
df_train_val = df.iloc[:-n_test]

X = df_train_val.drop(columns=["fail"])
y = df_train_val["fail"]

# 데이터 스케일링
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 스케일러 저장
joblib.dump(scaler, SCALER_PATH)

# 학습셋 / 검증셋 분리
X_train, X_val, y_train, y_val = train_test_split(
    X_scaled, y, test_size=0.2, stratify=y, random_state=42
)

# 테스트 데이터 준비
X_test = df_test.drop(columns=["fail"])
y_test = df_test["fail"]
X_test_scaled = scaler.transform(X_test)

# 모델 훈련
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# 모델 예측
y_pred = model.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred))

# 모델 저장
save_model(model)
print(f"Model structure saved to '{MODEL_PATH}'")
