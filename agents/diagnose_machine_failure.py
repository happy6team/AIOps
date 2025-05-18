from typing import Dict, Any, List
import numpy as np
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()

# 기준 통계 정보 (정상 기계 데이터 기반)
NORMAL_STATS = {
    'footfall': {'mean': 373.150635, 'std': 1192.714722, 'min': 0.0, 'max': 7300.0},
    'temp_mode': {'mean': 3.760436, 'std': 2.668461, 'min': 0.0, 'max': 7.0},
    'AQ': {'mean': 3.617060, 'std': 1.267926, 'min': 1.0, 'max': 7.0},
    'USS': {'mean': 3.484574, 'std': 1.360227, 'min': 1.0, 'max': 7.0},
    'CS': {'mean': 5.373866, 'std': 1.476472, 'min': 1.0, 'max': 7.0},
    'VOC': {'mean': 1.312160, 'std': 1.464928, 'min': 0.0, 'max': 6.0},
    'RP': {'mean': 46.299456, 'std': 16.396097, 'min': 19.0, 'max': 91.0},
    'IP': {'mean': 4.450091, 'std': 1.629488, 'min': 1.0, 'max': 7.0},
    'temperature': {'mean': 15.372051, 'std': 6.293247, 'min': 1.0, 'max': 24.0}
}

# 센서 설명 정보
SENSOR_DESCRIPTIONS = {
    'footfall': '지나가는 사람/물체 수 (정수)',
    'temp_mode': '온도 모드 (정수 설정값)',
    'AQ': '공기질 지수 (소수 포함 가능)',
    'USS': '초음파 센서 값 (소수 포함 가능)',
    'CS': '전류 센서 값 (소수 포함 가능)',
    'VOC': '휘발성 유기 화합물 수치',
    'RP': '회전 위치 또는 RPM',
    'IP': '입력 압력',
    'temperature': '작동 온도'
}

def identify_abnormal_sensors(sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """센서 데이터에서 비정상 센서 식별"""
    abnormal_sensors = []
    
    for sensor, value in sensor_data.items():
        # collection_time, fail, fail_probability 필드는 건너뜀
        if sensor in ['collection_time', 'fail', 'fail_probability']:
            continue
            
        if sensor in NORMAL_STATS:
            stats = NORMAL_STATS[sensor]
            
            # Z-score 계산
            z_score = abs((value - stats['mean']) / stats['std']) if stats['std'] > 0 else 0
            
            # 정상 범위 계산
            lower_bound = max(stats['min'], stats['mean'] - 2 * stats['std'])
            upper_bound = min(stats['max'], stats['mean'] + 2 * stats['std'])
            
            # 비정상 여부 판단 (정상 범위를 벗어나거나 Z-score가 높은 경우)
            is_abnormal = value < lower_bound or value > upper_bound or z_score > 2
            
            if is_abnormal:
                if value < lower_bound:
                    status = "낮음"
                else:
                    status = "높음"
                    
                severity = min(10, int(z_score))  # 심각도 (1-10)
                
                abnormal_sensors.append({
                    'sensor': sensor,
                    'value': value,
                    'normal_range': (lower_bound, upper_bound),
                    'normal_mean': stats['mean'],
                    'status': status,
                    'z_score': z_score,
                    'severity': severity,
                    'description': SENSOR_DESCRIPTIONS.get(sensor, '')
                })
    
    # 심각도에 따라 정렬
    abnormal_sensors.sort(key=lambda x: x['severity'], reverse=True)
    return abnormal_sensors

def generate_diagnosis_message(abnormal_sensors: List[Dict[str, Any]]) -> str:
    """비정상 센서 정보를 기반으로 LLM을 사용하여 진단 메시지 생성"""
    if not abnormal_sensors:
        return "알 수 없는 원인으로 인한 고장 발생. 전체 시스템 점검을 권장합니다."
    
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # 상위 3개 비정상 센서에 대한 설명 생성
    abnormal_descriptions = []
    for sensor in abnormal_sensors[:3]:
        description = (
            f"{sensor['sensor']} ({sensor['description']}): "
            f"값 {sensor['value']}이(가) 정상 범위 "
            f"{sensor['normal_range'][0]:.2f}~{sensor['normal_range'][1]:.2f}보다 {sensor['status']}"
        )
        abnormal_descriptions.append(description)
    
    # LLM 프롬프트 템플릿
    prompt_template = PromptTemplate.from_template("""
    당신은 제조 설비 고장 진단 AI 전문가입니다. 다음 비정상 센서 데이터를 분석하여 고장의 원인과 해결책을 제시하는 간결한 메시지를 생성해주세요.
    
    비정상 센서 데이터:
    {abnormal_descriptions}
    
    다음 형식으로 진단 결과를 생성해주세요:
    1. 고장 원인 (가장 심각한 문제점 1-2개 중심으로 설명)
    2. 권장 점검 및 조치 사항 (구체적인 센서와 관련된 부품 언급)
    
    진단 결과는 기술적이면서도 간결해야 하며, 제조 현장 담당자가 빠르게 이해할 수 있도록 작성해주세요.
    진단 결과는 100자 내외로 간결하게 작성해주세요.
    """)
    
    # 프롬프트 생성 및 LLM 호출
    prompt = prompt_template.format(abnormal_descriptions="\n".join(abnormal_descriptions))
    response = llm([HumanMessage(content=prompt)])
    
    return response.content.strip()

def format_final_message(diagnosis: str, abnormal_sensors: List[Dict[str, Any]], fail_probability: int) -> str:
    """최종 메시지 포맷팅 - fail_probability 매개변수 추가"""
    message = "⚠️ 기계 고장 예측 알림\n\n"
    # message += f"고장 가능성이 있으며, 확률이 {fail_probability}%로 판단되었습니다.\n\n"
    message += f"고장 가능성이 있으며, 재현율(recall) 기준 확률이 {fail_probability}%로 판단되었습니다.\n\n"  # 변경된 코드
    message += "진단 요약:\n"
    message += diagnosis
    
    if abnormal_sensors:
        message += "\n\n이상 감지된 센서:"
        for sensor in abnormal_sensors[:3]:  # 상위 3개만 표시
            message += f"\n• {sensor['sensor']}: {sensor['value']} (정상 범위: {sensor['normal_range'][0]:.2f}~{sensor['normal_range'][1]:.2f})"
    
    return message

def diagnose_machine_failure(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """기계 고장 진단 메인 함수"""
    # 입력 데이터 검증
    if 'fail' not in sensor_data or sensor_data['fail'] != 1:
        return {
            'error': "이 함수는 fail=1(고장)인 데이터만 처리합니다."
        }
    
    # fail_probability 값 확인 (기본값 설정)
    fail_probability = sensor_data.get('fail_probability', 100)
    
    # 비정상 센서 식별
    abnormal_sensors = identify_abnormal_sensors(sensor_data)
    
    # 진단 메시지 생성
    diagnosis = generate_diagnosis_message(abnormal_sensors)
    
    # 최종 메시지 포맷팅 - fail_probability 전달
    message = format_final_message(diagnosis, abnormal_sensors, fail_probability)
    
    # 결과 반환
    return {
        'failure_message': message,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
