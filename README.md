# AIOps
SKALA 1기 AIOps 미니 프로젝트 이상치 예측형 모델 관리 Fast API 서버입니다.

## 프로젝트 시작하기

1. 저장소 클론
   ```
   git clone {저장소 url}
   cd AIOps
   ```
   
2. 가상환경 생성
   
   ```
   python -m venv venv
   ```

3. 가상환경 활성화
   ```
   source venv/bin/activate  # mac
   venv\Scripts\activate # Windows powershell
   ```
   
4. 패키지 설치
   ```
   pip install -r requirements.txt
   ```

5. .env 파일 만들기  
   .env.example 파일 참고해서 만드시면 됩니다.
   
6. 프로젝트 실행
   ```
   uvicorn api.main:app --reload  
   ```
