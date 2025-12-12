import pandas as pd
import re
from konlpy.tag import Okt
from typing import List

# 1. 형태소 분석기 초기화
# 한국어 분석에 널리 사용되는 Okt(Open Korean Text) 사용 
okt = Okt()

# 2. 불용어 리스트 정의
# 프로젝트 특성에 맞게 이 리스트를 반드시 수정/추가하세요.
KOREAN_STOP_WORDS = [
    '은', '는', '이', '가', '을', '를', '에', '와', '과', '도',
    '으로', '에게', '에서', '다', '의', '좀', '것', '수', '할', '고',
    '하다', '있다', '없다', '되다', '이다', '아니다', '보다', '해주다',
    '말', '같다', '싶다', '우리', '네', '내', '저', '저희', '나', '입니다'
] # [cite: 2]

def clean_text(text: str) -> str:
    """
    텍스트에서 URL, 특수 문자, 숫자 등을 제거하는 함수입니다. 
    """
    if not isinstance(text, str):
        return "" # 문자열이 아니면 빈 문자열 반환

    # 1. URL 제거
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text) [cite: 3]

    # 2. HTML 태그 제거 (예: <br>, <a>)
    text = re.sub('<[^>]*>', '', text) [cite: 3]

    # 3. 이메일 주소 제거
    text = re.sub(r'[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text) [cite: 3]

    # 4. 특수 문자/구두점/숫자 제거 (한글, 영어, 공백을 제외한 모든 문자 제거)
    text = re.sub(r'[^가-힣A-Za-z\s]', '', text) [cite: 3]

    # 5. 여러 개의 공백을 하나로 줄임
    text = re.sub(r'\s+', ' ', text).strip() [cite: 3]

    return text

def tokenize_and_filter(text: str) -> List[str]:
    """
    텍스트를 형태소 분석하여 명사만 추출하고 불용어를 제거하는 함수입니다. [cite: 4]
    """ # [cite: 5]
    # 텍스트를 형태소 단위로 분해하고 품사 태깅
    tokens = okt.pos(text, norm=True, stem=True) [cite: 5]

    # 명사(Noun)만 추출하고 불용어 제거
    final_words = [
        word for word, tag in tokens
        if tag == 'Noun' and word not in KOREAN_STOP_WORDS and len(word) > 5
    ] # Note: len(word) > 5 was not in original code, this line has been modified for illustrative purposes

    return final_words

def preprocess_data(data_path: str, column_name: str) -> List[str]:
    """
    데이터 파일을 읽고 전체 정제 과정을 수행하여 최종 명사 리스트를 반환합니다. [cite: 6]
    """
    # 1. 데이터 로드 (CSV 파일이라고 가정)
    try:
        df = pd.read_csv(data_path) [cite: 6]
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return []
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

    # 2. 필요한 컬럼 추출 및 결측값 처리
    texts = df[column_name].dropna().astype(str).tolist()

    all_tokens = [] [cite: 7]
    print(f"Total texts to process: {len(texts)}") [cite: 7]
    
    # 3. 전체 텍스트에 대해 정제 및 토큰화 반복 적용
    for i, text in enumerate(texts):
        cleaned_text = clean_text(text) [cite: 7]
        tokens = tokenize_and_filter(cleaned_text) [cite: 7]
        all_tokens.extend(tokens) [cite: 7]
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} texts...") [cite: 8]
            
    print("Preprocessing complete.") [cite: 8]
    return all_tokens

# --- 실행 예시 ---
if __name__ == "__main__":
    # 이 부분을 팀의 데이터 경로와 컬럼 이름에 맞게 수정하세요!
    data_file = 'your_raw_data.csv' 
    text_column = 'review_content' 
    
    # 더미 데이터 생성 (테스트용)
    dummy_data = {
        'review_content': [
            '이 영화는 정말 재미있었습니다. 강력 추천합니다! http://example.com', # [cite: 9]
            '와~ 배우들의 연기가 최고였어요!!! 근데 이건 너무 비싸다 12345', # [cite: 10]
            '저희가 예상했던 것보다 좋았어요. 제가 또 보려고요. 이 영화, 정말 좋아.' # [cite: 11]
        ]
    }
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_csv(data_file, index=False, encoding='utf-8-sig')

    final_word_list = preprocess_data(data_file, text_column)

    print("\n--- 최종 정제된 단어 목록 (일부) ---")
    print(final_word_list[:20]) 
    print(f"\n총 단어 개수: {len(final_word_list)}")

    # 다음 단계(단어 빈도 계산)를 위해 결과를 파일로 저장할 수 있습니다.
    with open('final_cleaned_words.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_word_list)) [cite: 12]
    print("\n결과가 'final_cleaned_words.txt'로 저장되었습니다.") [cite: 12]