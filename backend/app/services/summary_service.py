# app/services/summary_service.py
import kss
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from functools import lru_cache
from app.core.config import settings
import trafilatura

# 사용자 정의 예외 클래스 정의
class ExtractionError(Exception):
    pass

class ContentTooShortError(Exception):
    pass

# 전역 변수로 선언하되, 초기화는 하지 않습니다.
tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model_if_not_loaded():
    """모델과 토크나이저를 필요할 때 한 번만 로드합니다."""
    global tokenizer, model
    if tokenizer is None or model is None:
        print("모델과 토크나이저를 로드하는 중...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
            model = AutoModelForSeq2SeqLM.from_pretrained(settings.MODEL_NAME).to(device)
            print("모델 로딩 완료.")
        except Exception as e:
            print(f"모델 로딩 중 오류 발생: {e}")
            raise RuntimeError("모델을 로드할 수 없습니다.") from e

def extract_text(url: str) -> str:
    """
    URL에서 본문을 추출합니다. trafilatura가 실패하는 경우를 대비해 requests와 BeautifulSoup를 사용합니다.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    headers = {'User-Agent': user_agent}

    try:
        # requests로 URL에 접근하여 HTML을 가져옴
        print(f"URL 요청 시작: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 던짐
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 연합뉴스 기사 본문을 찾는 로직 (기존 코드)
        article_body = soup.find('div', id='articleWrap')
        
        if not article_body:
            print("BeautifulSoup으로 본문 추출 실패, trafilatura 재시도...")
            # trafilatura.fetch_url()는 'user_agent' 인자를 받지 않으므로 제거
            downloaded = trafilatura.fetch_url(url, no_ssl=False)
            if not downloaded:
                raise ExtractionError("본문을 가져올 수 없습니다. 웹사이트가 접근을 차단했거나 동적 콘텐츠일 수 있습니다.")
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
        else:
            text = article_body.get_text(separator='\n', strip=True)

        if len(text) < 300:
            raise ContentTooShortError("기사 본문이 너무 짧아 요약할 수 없습니다.")
        
        return text

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 오류 발생: {e.response.status_code}")
        # 4xx, 5xx 에러에 대한 메시지
        raise ExtractionError(f"URL 접근 중 HTTP 오류가 발생했습니다. (상태 코드: {e.response.status_code})")
    except requests.exceptions.ConnectionError as e:
        print(f"연결 오류 발생: {e}")
        # DNS 오류, 연결 거부 등
        raise ExtractionError("URL에 연결할 수 없습니다. URL을 확인하거나 네트워크 설정을 점검해주세요.")
    except requests.exceptions.Timeout as e:
        print(f"시간 초과 오류 발생: {e}")
        # 서버 응답 시간 초과
        raise ExtractionError("요청 시간 초과. 웹사이트가 응답하지 않습니다.")
    except Exception as e:
        # 기타 모든 예외를 처리
        print(f"일반 예외 발생: {e}")
        raise ExtractionError(f"본문 추출 중 알 수 없는 오류 발생: {e}")

@lru_cache(maxsize=settings.CACHE_SIZE)
def generate_summary(text: str, target_tokens: int = 420) -> str:
    """텍스트를 요약합니다."""
    load_model_if_not_loaded()
    
    input_text = f"summarize: {text}"
    inputs = tokenizer(
        [input_text], 
        max_length=2048, 
        truncation=True, 
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_length=target_tokens,
            min_length=min(120, target_tokens // 2),
            no_repeat_ngram_size=3,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True).strip()

def to_n_lines(summary: str, n: int) -> str:
    """요약된 텍스트를 kss로 문장 분리 후 n줄로 자릅니다."""
    sents = [s.strip() for s in kss.split_sentences(summary) if s.strip()]
    return "\n".join(sents[:n])
