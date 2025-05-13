from dotenv import load_dotenv
import os
import requests
from agents.diagnose_machine_failure import diagnose_machine_failure
from agents.retraining_message import notify_retraining_start, notify_retraining_completed

# .env 파일 로드
load_dotenv()

def send_slack_message(option_type, input):
    """
    Slack 메시지 전송 함수
    
    Args:
        option_type: 메시지 유형 ("failure", "retraining_start", "retraining_done")
        input: 메시지 생성에 필요한 입력 데이터
    """
    if option_type == "failure":
        result = diagnose_machine_failure(input)
        message = {"text": result["failure_message"]}
    
    elif option_type == "retraining_start":
        before_acc = input.get("before_acc", 0)
        threshold = input.get("threshold", 0)
        result = notify_retraining_start(before_acc, threshold)
        message = {"text": result["retraining_start_message"]}
    
    elif option_type == "retraining_done":
        before_acc = input.get("before_acc", 0)
        after_acc = input.get("after_acc", 0)
        threshold = input.get("threshold", 0)
        result = notify_retraining_completed(before_acc, after_acc, threshold)
        message = {"text": result["retraining_done_message"]}
    
    else:
        message = {"text": "알 수 없는 메시지 유형입니다."}

    WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")

    requests.post(WEB_HOOK_URL, json=message)
    
    return result