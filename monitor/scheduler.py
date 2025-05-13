import pandas as pd
import logging
import os
import asyncio

from model.weight_used_model import predict_and_result
from model.refit_model import evaluate, retrain

from config.config import DATA_SOURCE_PATH  # 데이터 소스 경로 설정 필요

from config.db_config import AsyncSessionLocal
from cruds.sensordata import create_sensor_data, get_all_sensor_data
from api.schemas.sensor_data import SensorDataCreate
from agents.send_slack_message import send_slack_message

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

PERFORMANCE_THRESHOLD = 0.9 # 최적화해서 알아내야 함 

logger.info(f"데이터 경로 확인: {DATA_SOURCE_PATH}")

# 새로운 데이터 5초마다 불러와서 학습하기
async def predict_failures(latest_data):
    try:
        message = "failure"
        # 1. 모델로 예측 실행
        prediction_result, fail_probability = predict_and_result(latest_data) # ex) 예측 결과 확률
        
        # @ 여기 retrun값이 어떻게 오냐에 따라 값 다르게 넣어주기
        # 예측 결과 저장
        result = await save_row(latest_data, prediction_result, fail_probability)
        print("😺데이터 저장이")
        print(result)
        
        # 2. 예측 결과 처리 (임계값 이상이면 경고 발생)
        if prediction_result == 1:  # 임계값 설정 필요
            logger.warning(f"고장 가능성 감지! 고장 확률: {fail_probability}")
            # 여기에 알림 전송 로직 추가 (이메일, SMS, 웹훅 등)
            send_slack_message("failure", result)
        logger.info(f"예측 완료: {prediction_result}")
        return prediction_result, fail_probability
    except Exception as e:
        logger.error(f"예측 중 오류 발생: {str(e)}")
    

# # 5초마다 실행
# schedule.every(5).seconds.do(predict_failures)

# 매일 자정에 모델 성능 측정
async def evaluate_and_retrain():
    try:
        logger.info("모델 성능 평가 시작")
        
        # 데이터 불러오기
        database = pd.read_csv(DATA_SOURCE_PATH)

        # 모델 성능 평가
        performance_metrics = evaluate(database)  # 비동기 함수로 처리
        logger.info(f"모델 성능 지표: {performance_metrics}")
        
        # 성능 지표가 float일 경우 직접 비교
        if isinstance(performance_metrics, float):  # 만약 정확도 값이 float로 반환되는 경우
            accuracy = performance_metrics
        else:
            accuracy = performance_metrics.get('accuracy', 0)  # 딕셔너리에서 정확도를 추출
        
        # 성능 임계값 체크
        if accuracy < PERFORMANCE_THRESHOLD:
            slack_before_data = {
                "before_acc": accuracy,
                "threshold": PERFORMANCE_THRESHOLD
            }
            send_slack_message("retraining_start", slack_before_data)
            print("✅슬랙 메시지 전송 완료")
            logger.warning(f"모델 성능 저하 감지. 재학습 시작...")

            # DB 세션 열기 및 저장
            async with AsyncSessionLocal() as session:
                new_database = await get_all_sensor_data(session)

            # 모델 재학습
            retrain_result = retrain(new_database)
            logger.info(f"모델 재학습 완료: {retrain_result}")
            slack_data = {
                "before_acc": accuracy,
                "after_acc":retrain_result,
                "threshold": PERFORMANCE_THRESHOLD
            }
            send_slack_message("retraining_done", slack_data)
            print("😺슬랙 메시지 전송 완료")
        else:
            logger.info("모델 성능 양호. 재학습 불필요")
    except Exception as e:
        logger.error(f"모델 평가/재학습 중 오류 발생: {str(e)}")

# # 매일 자정에 모델 평가 및 재학습 실행
# schedule.every().day.at("00:00").do(evaluate_and_retrain)

async def periodic_task(task_func, interval_seconds):
    if not asyncio.iscoroutinefunction(task_func):
        logging.error(f"task_func는 비동기 함수여야 합니다. {task_func}는 올바른 비동기 함수가 아닙니다.")
        return

    while True:
        try:
            await task_func()
        except Exception as e:
            logging.exception(f"periodic_task: 예외 발생 - {e}")
        await asyncio.sleep(interval_seconds)

# 데이터 저장 함수
async def save_row(row,prediction_result, fail_probability):
    # row → dict
    row_dict = row.to_dict()

        # 키 수동 수정
    if 'tempMode' in row_dict:
        row_dict['temp_mode'] = row_dict.pop('tempMode')
    if 'Temperature' in row_dict:
        row_dict['temperature'] = row_dict.pop('Temperature')
    
    # NaN → None 변환
    row_dict = {k: None if pd.isna(v) else v for k, v in row_dict.items()}

    # 강제로 fail과 fail_probability 지정
    row_dict['fail'] = prediction_result 
    row_dict['fail_probability'] = fail_probability

    # 모델 생성
    sensor_data = SensorDataCreate(**row_dict)
    # DB 세션 열기 및 저장
    async with AsyncSessionLocal() as session:
        await create_sensor_data(session, sensor_data)
        print("새로운 데이터 저장 완료")

async def predict_each_row_periodically(database: pd.DataFrame, interval_seconds: int):
    try:
        while True:
            for index, row in database.iterrows():
                prediction_result, fail_probability = await predict_failures(row)  # 각 행 예측
                await asyncio.sleep(interval_seconds)  # 5초 대기 후 다음 행
    except Exception as e:
        logging.error(f"예측 루프 중 오류 발생: {e}")

# # 메인 루프
# if __name__ == "__main__":
#     logger.info("고장 예측 스케줄러 시작됨")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)