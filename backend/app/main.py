# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import summarizer

app = FastAPI(
    title="뉴스 요약 API",
    description="URL을 입력받아 기사를 요약해주는 API",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(summarizer.router, prefix="/api")

@app.get("/healthz")
def health_check():
    return {"status": "ok"}