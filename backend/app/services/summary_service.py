# app/services/summary_service.py
# 수정된 파일: 텍스트 추출, 요약 모델 로직 등 핵심 서비스 로직.
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
        print(f"URL 요청 시작: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 던짐
        print("URL 요청 성공.")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_body = soup.find('div', id='articleWrap')
        
        if not article_body:
            print("BeautifulSoup으로 본문 추출 실패, trafilatura 재시도...")
            downloaded = trafilatura.fetch_url(url, no_ssl=False)
            if not downloaded:
                print("trafilatura로 본문 가져오기 실패.")
                raise ExtractionError("본문을 가져올 수 없습니다. 웹사이트가 접근을 차단했거나 동적 콘텐츠일 수 있습니다.")
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
            print("trafilatura로 텍스트 추출 완료.")
        else:
            text = article_body.get_text(separator='\n', strip=True)
            print("BeautifulSoup으로 텍스트 추출 완료.")

        if len(text) < 300:
            print("텍스트 길이가 너무 짧음.")
            raise ContentTooShortError("기사 본문이 너무 짧아 요약할 수 없습니다.")
        
        return text

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 오류 발생: {e.response.status_code}")
        raise ExtractionError(f"URL 접근 중 HTTP 오류가 발생했습니다. (상태 코드: {e.response.status_code})")
    except requests.exceptions.ConnectionError as e:
        print(f"연결 오류 발생: {e}")
        raise ExtractionError("URL에 연결할 수 없습니다. URL을 확인하거나 네트워크 설정을 점검해주세요.")
    except requests.exceptions.Timeout as e:
        print(f"시간 초과 오류 발생: {e}")
        raise ExtractionError("요청 시간 초과. 웹사이트가 응답하지 않습니다.")
    except Exception as e:
        print(f"일반 예외 발생: {e}")
        raise ExtractionError(f"본문 추출 중 알 수 없는 오류 발생: {e}")

@lru_cache(maxsize=settings.CACHE_SIZE)
def summarize_text_by_chars(text: str, target_chars: int) -> str:
    """
    텍스트를 요약하고, 지정된 글자 수에 맞춰 마지막 문장이 잘리지 않도록 후처리합니다.
    """
    print(f"요약 함수 호출 (목표 글자 수: {target_chars})")
    # 목표 글자 수에 맞춰 min_length와 max_length를 더 보수적으로 설정
    # 한국어는 글자:토큰 비율이 1:1.5 정도이므로, 토큰 수를 글자 수의 2배로 설정
    target_tokens = int(target_chars * 2)
    min_tokens = int(target_tokens * 0.5) # 최소 길이를 더 여유롭게 설정하여 문장 완결성을 높임
    
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
            min_length=min_tokens,
            no_repeat_ngram_size=3,
            num_beams=4,
            length_penalty=1.0,
            early_stopping=True,
        )
    
    raw_summary = tokenizer.decode(out[0], skip_special_tokens=True).strip()
    
    # 후처리: kss를 사용하여 요약문을 문장 단위로 분리하고
    # 지정된 글자 수를 넘지 않는 선에서 마지막 문장이 잘리지 않도록 합니다.
    return postprocess_summary_by_chars(raw_summary, target_chars)


def postprocess_summary_by_chars(summary: str, target_chars: int) -> str:
    """
    주어진 요약문을 문장 단위로 끊어 목표 글자 수를 맞추는 후처리 함수.
    """
    print(f"후처리 함수 호출 (목표 글자 수: {target_chars})")
    sentences = [s.strip() for s in kss.split_sentences(summary) if s.strip()]
    
    final_summary = []
    current_length = 0
    
    for sentence in sentences:
        # 다음 문장을 추가했을 때 목표 글자 수를 초과하는지 확인
        # 문장 길이 + 문장 구분자(space) 길이 고려
        # 마지막 문장이더라도 목표 글자 수를 초과하면 추가하지 않음
        if current_length + len(sentence) + 1 > target_chars:
            break
        
        final_summary.append(sentence)
        current_length += len(sentence) + 1
        
    return " ".join(final_summary)
