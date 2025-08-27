# app/api/endpoints/summarizer.py
# 수정된 파일: 요약 관련 비즈니스 로직
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
from app.services.summary_service import (
    extract_text, 
    summarize_text_by_chars, # 글자 수 기반 요약을 위한 새 함수 import
    ExtractionError,
    ContentTooShortError
)

router = APIRouter()

class SummarizeRequest(BaseModel):
    url: str

@router.post("/summarize")
def summarize_url(req: SummarizeRequest):
    """URL을 입력받아 100자, 200자, 300자 내외로 요약된 결과를 반환합니다."""
    print("summarize_url 요청 시작.")
    try:
        url = req.url
        print(f"URL: {url}")
        
        # 1. URL에서 기사 본문 텍스트를 추출합니다.
        text = extract_text(url)
        print("텍스트 추출 완료.")
        
        # 2. 각 목표 글자 수에 맞춰 독립적으로 요약을 생성합니다.
        print("100자 요약 생성 시작...")
        chars100 = summarize_text_by_chars(text, target_chars=100)
        print("100자 요약 생성 완료.")
        
        print("200자 요약 생성 시작...")
        chars200 = summarize_text_by_chars(text, target_chars=200)
        print("200자 요약 생성 완료.")
        
        print("300자 요약 생성 시작...")
        chars300 = summarize_text_by_chars(text, target_chars=300)
        print("300자 요약 생성 완료.")
        
        # 3. 고유한 ID를 생성하여 반환합니다.
        item_id = hashlib.sha256((url + chars100[:64]).encode()).hexdigest()[:12]
        print("응답 반환 준비 완료.")

        return {
            "id": item_id,
            "chars100": chars100,
            "chars200": chars200,
            "chars300": chars300,
        }
    except ExtractionError as e:
        print(f"ExtractionError 발생: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except ContentTooShortError as e:
        print(f"ContentTooShortError 발생: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        print(f"RuntimeError 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="요약을 처리하는 중 서버 오류가 발생했습니다.")
