from typing import Dict, Any
from datetime import datetime

def notify_retraining_start(before_acc: float, threshold: float) -> Dict[str, Any]:
    """
    모델 재학습 시작 전 알림 메시지 생성
    
    Args:
        before_acc: 현재 모델의 정확도
        threshold: 재학습 결정 기준 정확도 임계값
    
    Returns:
        Dict: 재학습 시작 메시지 정보
    """
    # 정확도를 백분율로 계산 (0.0-1.0 범위이면 100을 곱함)
    before_acc_percent = before_acc * 100 if before_acc <= 1.0 else before_acc
    threshold_percent = threshold * 100 if threshold <= 1.0 else threshold
    
    # 날짜 및 시간 포맷
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 메시지 생성
    message = f"🔄 모델 재학습 시작 알림\n\n"
    message += f"현재 시간: {current_time}\n\n"
    message += f"현재 모델 성능이 임계치보다 낮아 재학습을 시작합니다.\n"
    message += f"• 현재 정확도: {before_acc_percent:.2f}%\n"
    message += f"• 요구 임계치: {threshold_percent:.2f}%\n\n"
    message += f"재학습이 완료되면 추가 알림이 전송됩니다."
    
    return {
        "retraining_start_message": message,
        "timestamp": current_time
    }

def notify_retraining_completed(before_acc: float, after_acc: float, threshold: float) -> Dict[str, Any]:
    """
    모델 재학습 완료 알림 메시지 생성
    
    Args:
        before_acc: 이전 모델의 정확도
        after_acc: 재학습 후 모델의 정확도
        threshold: 모델 배포 결정 기준 정확도 임계값
    
    Returns:
        Dict: 재학습 완료 메시지 정보
    """
    # 정확도를 백분율로 계산 (0.0-1.0 범위이면 100을 곱함)
    before_acc_percent = before_acc * 100 if before_acc <= 1.0 else before_acc
    after_acc_percent = after_acc * 100 if after_acc <= 1.0 else after_acc
    threshold_percent = threshold * 100 if threshold <= 1.0 else threshold
    
    # 성능 향상 계산
    improvement = after_acc_percent - before_acc_percent
    improvement_message = f"향상: +{improvement:.2f}%" if improvement > 0 else f"하락: {improvement:.2f}%"
    
    # 날짜 및 시간 포맷
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 배포 성공 여부 확인
    is_deployed = after_acc >= threshold
    deployment_status = "✅ 배포 완료" if is_deployed else "❌ 배포 실패"
    
    # 메시지 생성
    message = f"✅ 모델 재학습 완료 알림\n\n"
    message += f"현재 시간: {current_time}\n\n"
    message += f"모델 재학습이 완료되었습니다.\n"
    message += f"• 이전 정확도: {before_acc_percent:.2f}%\n"
    message += f"• 새 정확도: {after_acc_percent:.2f}% ({improvement_message})\n"
    message += f"• 요구 임계치: {threshold_percent:.2f}%\n\n"
    
    if is_deployed:
        message += f"배포 상태: {deployment_status}\n"
        message += f"새 모델이 성공적으로 배포되었습니다."
    else:
        message += f"배포 상태: {deployment_status}\n"
        message += f"재학습된 모델이 임계치에 도달하지 못해 배포되지 않았습니다."
    
    return {
        "retraining_done_message": message,
        "timestamp": current_time,
        "is_deployed": is_deployed
    }