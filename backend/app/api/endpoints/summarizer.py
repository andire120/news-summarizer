from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
from app.services.summary_service import (
    extract_text, 
    generate_summary, 
    to_n_lines, 
    ExtractionError,
    ContentTooShortError
)

router = APIRouter()

class SummarizeRequest(BaseModel):
    url: str

@router.post("/summarize")
def summarize_url(req: SummarizeRequest):
    """URL을 입력받아 3, 5, 8줄로 요약된 결과를 반환합니다."""
    try:
        url = req.url
        text = extract_text(url)
        
        base_summary = generate_summary(text, target_tokens=420)
        
        lines3 = to_n_lines(base_summary, 3)
        lines5 = to_n_lines(base_summary, 5)
        lines8 = to_n_lines(base_summary, 8)
        
        item_id = hashlib.sha256((url + base_summary[:64]).encode()).hexdigest()[:12]

        return {
            "id": item_id,
            "lines3": lines3,
            "lines5": lines5,
            "lines8": lines8,
        }
    except ExtractionError as e:
        # 본문 추출 실패 시 422 에러와 함께 구체적인 메시지 반환
        raise HTTPException(status_code=422, detail=str(e))
    except ContentTooShortError as e:
        # 본문 길이가 짧은 경우 422 에러와 함께 구체적인 메시지 반환
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        # 모델 로딩 실패 시 500 에러 반환
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        # 예측 불가능한 서버 내부 오류 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail="요약을 처리하는 중 서버 오류가 발생했습니다.")
