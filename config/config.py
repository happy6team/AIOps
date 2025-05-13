import os

# 기본 경로 설정 (환경 변수에서 가져오거나 기본값 사용)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # AIOps/
DATA_DIR = os.path.join(BASE_DIR, "data")

# 데이터 경로
GNERATE_DATA_SOURCE_PATH = os.path.join(DATA_DIR, "generated_data.csv")
DATA_SOURCE_PATH = os.path.join(DATA_DIR, "data.csv") 