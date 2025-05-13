from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from api.routers import file

# 애플리케이션 시작 시 환경 변수 로드 및 그래프 초기화
load_dotenv()

app = FastAPI(
    title="AIOps API", 
    description="AIOps 미니 프로젝트 API 명세서입니다.(수정 필요)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def welcome():
    return {"message": "Welcome to the FastAPI server!"}

app.include_router(file.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 