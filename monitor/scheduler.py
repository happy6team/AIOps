import time
import schedule
import pandas as pd
import logging
from config import DATA_SOURCE_PATH  # 데이터 소스 경로 설정 필요

logging.info(f"데이터 경로 확인: {DATA_SOURCE_PATH}")
# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

PERFORMANCE_THRESHOLD = 0.9

logger.info(f"데이터 경로 확인: {DATA_SOURCE_PATH}")

# 새로운 데이터 5초마다 불러와서 학습하기
def predict_failures():
    try:
        # 1. 최신 데이터 불러오기
        latest_data = pd.read_csv(GNERATE_DATA_SOURCE_PATH) # 여기는 새로운 데이터 로드해주는 함수로 변경 예정
        
        # 2. 모델로 예측 실행
        prediction_result, fail_probability = predict_and_result(latest_data) # ex) 예측 결과 확률
        
        # @ 여기 retrun값이 어떻게 오냐에 따라 값 다르게 넣어주기
        # 3. 예측 결과 처리 (임계값 이상이면 경고 발생)
        if prediction_result == 1:  # 임계값 설정 필요
            logger.warning(f"고장 가능성 감지! 고장 확률: {fail_probability}")
            # 여기에 알림 전송 로직 추가 (이메일, SMS, 웹훅 등)
            
        logger.info(f"예측 완료: {prediction_result}")
    except Exception as e:
        logger.error(f"예측 중 오류 발생: {str(e)}")

# 5초마다 실행
schedule.every(5).seconds.do(predict_failures)

# 매일 자정에 모델 성능 측정
def evaluate_and_retrain():
    try:
        logger.info("모델 성능 평가 시작")
        
        # 데이터 불러오기
        database = pd.read_csv(DATA_SOURCE_PATH)

        # 모델 성능 평가
        performance_metrics = train_and_evaluate(database) # 데이터 불러오기
        logger.info(f"모델 성능 지표: {performance_metrics}")
        
        # 성능 임계값 체크
        if performance_metrics['accuracy'] < PERFORMANCE_THRESHOLD:
            logger.warning(f"모델 성능 저하 감지. 재학습 시작...")
 
            # 모델 재학습
            retrain_result = model.process() # 데이터넣기
            logger.info(f"모델 재학습 완료: {retrain_result}")
        else:
            logger.info("모델 성능 양호. 재학습 불필요")
    except Exception as e:
        logger.error(f"모델 평가/재학습 중 오류 발생: {str(e)}")

# 매일 자정에 모델 평가 및 재학습 실행
schedule.every().day.at("00:00").do(evaluate_and_retrain)

async def periodic_task(task_func, interval_seconds):
    while True:
        try:
            await task_func()
        except Exception as e:
            logging.exception(f"periodic_task: 예외 발생 - {e}")
        await asyncio.sleep(interval_seconds)

# 메인 루프
if __name__ == "__main__":
    logger.info("고장 예측 스케줄러 시작됨")
    while True:
        schedule.run_pending()
        time.sleep(1)