import pandas as pd
import re
import os
import json
from konlpy.tag import Okt
from typing import List

# 1. 형태소 분석기 초기화
okt = Okt() # [cite: 1]

# 2. 불용어 리스트 정의
# 프로젝트의 목적에 맞게 불용어(분석에서 제외할 단어)를 추가하거나 수정하세요.
KOREAN_STOP_WORDS = [ # [cite: 2]
    '은', '는', '이', '가', '을', '를', '에', '와', '과', '도',
    '으로', '에게', '에서', '다', '의', '좀', '것', '수', '할', '고',
    '하다', '있다', '없다', '되다', '이다', '아니다', '보다', '해주다',
    '말', '같다', '싶다', '우리', '네', '내', '저', '저희', '나', '입니다',
    # 뉴스 제목에서 자주 나오는 불필요한 단어 추가
    '뉴스', '속보', '오늘', '연합', '기자', '단독', '종합', '금일', '해당', '관련'
]

def clean_text(text: str) -> str:
    """
    텍스트에서 URL, 특수 문자, 숫자 등을 제거하여 정제합니다. 
    """
    if not isinstance(text, str):
        return ""

    # 1. URL 제거
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text) # 

    # 2. HTML 태그 및 이메일 주소 제거
    text = re.sub('<[^>]*>', '', text) # 
    text = re.sub(r'[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text) # 

    # 3. 특수 문자/구두점/숫자 제거 (한글, 영어, 공백을 제외한 모든 문자 제거)
    text = re.sub(r'[^가-힣A-Za-z\s]', '', text) # 

    # 4. 여러 개의 공백을 하나로 줄임
    text = re.sub(r'\s+', ' ', text).strip() # 

    return text

def tokenize_and_filter(text: str) -> List[str]:
    """
    텍스트를 형태소 분석하여 명사만 추출하고 불용어를 제거하는 함수입니다. [cite: 4, 5]
    """
    # 텍스트를 형태소 단위로 분해하고 품사 태깅
    tokens = okt.pos(text, norm=True, stem=True) # [cite: 5]

    # 명사(Noun)만 추출하고 불용어 및 한 글자 단어 제거
    final_words = [
        word for word, tag in tokens
        if tag == 'Noun' and word not in KOREAN_STOP_WORDS and len(word) > 1
    ] # [cite: 5]

    return final_words

def preprocess_data(directory_path: str) -> List[str]:
    """
    지정된 디렉토리의 모든 JSON 파일을 읽고, 뉴스 제목을 추출하여 정제 및 토큰화합니다.
    """
    all_tokens = []
    
    # 1. 디렉토리 내 JSON 파일 목록 가져오기
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    if not json_files:
        print(f"⚠️ {directory_path} 폴더에 JSON 파일이 없습니다. 수집 코드를 먼저 실행하세요.")
        return []
    
    print(f"📰 총 {len(json_files)}개의 JSON 파일을 처리합니다.")

    # 2. 파일별로 처리
    for filename in json_files:
        filepath = os.path.join(directory_path, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # JSON 파일에서 'title' 키의 값들만 추출
            titles = [item.get('title', '') for item in data]
            
            total_titles = len(titles)
            processed_count = 0
            
            print(f"   -> 파일 '{filename}': {total_titles}건 처리 시작")

            # 3. 추출된 제목에 대해 정제 및 토큰화 적용
            for text in titles:
                cleaned_text = clean_text(text)
                tokens = tokenize_and_filter(cleaned_text)
                all_tokens.extend(tokens)
                processed_count += 1
            
            print(f"   -> 파일 '{filename}': 처리 완료 ({processed_count}건)")

        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
        except json.JSONDecodeError:
            print(f"Error: JSON decoding failed for {filepath}")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print("\n✅ 전체 데이터 정제 및 토큰화 완료.")
    return all_tokens

# --- 실행 예시 ---
if __name__ == "__main__":
    
    # [설정] 팀원의 코드가 저장한 폴더 이름
    DATA_DIRECTORY = 'collected_data' 
    
    # 데이터 정제 및 토큰화 실행
    final_word_list = preprocess_data(DATA_DIRECTORY)

    if final_word_list:
        # 단어 목록을 파일로 저장하여 다음 단계(워드 클라우드)에서 사용
        OUTPUT_FILENAME = 'final_tokenized_words.txt'
        
        # 워드 클라우드 생성을 위해 단어와 빈도를 카운트하는 추가 로직이 필요하지만, 
        # 여기서는 일단 리스트를 저장합니다.
        
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f: # [cite: 12]
            f.write('\n'.join(final_word_list))
        
        print("\n--- 처리 결과 요약 ---")
        print(f"총 추출된 단어 개수: {len(final_word_list)}개")
        print(f"결과가 '{OUTPUT_FILENAME}' 파일로 저장되었습니다.")
    else:
        print("최종 단어 목록이 비어있습니다. 수집 파일이 있는지 확인하세요.")