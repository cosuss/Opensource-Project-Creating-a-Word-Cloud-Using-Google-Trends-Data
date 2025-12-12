import re
import os
import json
from typing import List

KOREAN_STOP_WORDS = [
    '은','는','이','가','을','를','에','와','과','도',
    '으로','에게','에서','다','의','좀','것','수','할','고',
    '하다','있다','없다','되다','이다','아니다','보다','해주다',
    '말','같다','싶다','우리','네','내','저','저희','나','입니다',
    '뉴스','속보','오늘','연합','기자','단독','종합','금일','해당','관련'
]

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub('<[^>]*>', '', text)
    text = re.sub(r'[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
    text = re.sub(r'[^가-힣A-Za-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_konlpy(text: str) -> List[str]:
    from konlpy.tag import Okt
    okt = Okt()
    tokens = okt.pos(text, norm=True, stem=True)
    return [
        w for w, t in tokens
        if t == "Noun" and w not in KOREAN_STOP_WORDS and len(w) > 1
    ]

def tokenize_fallback(text: str) -> List[str]:
    # konlpy가 안 될 때: 공백 기준 + 한글/영문만 남긴 뒤 stopword 제거
    words = text.split()
    words = [w for w in words if w not in KOREAN_STOP_WORDS and len(w) > 1]
    return words

def preprocess_data(directory_path: str) -> List[str]:
    if not os.path.isdir(directory_path):
        print(f"❌ 폴더 없음: {directory_path}")
        return []

    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
    if not json_files:
        print(f"⚠️ {directory_path} 폴더에 JSON 파일이 없습니다.")
        return []

    # konlpy 사용 가능 여부 체크
    use_konlpy = True
    try:
        import konlpy  # noqa
        from konlpy.tag import Okt  # noqa
    except Exception as e:
        use_konlpy = False
        print("⚠️ konlpy 사용 불가 → fallback 토크나이저로 진행")
        print("   이유:", repr(e))

    all_tokens: List[str] = []
    print(f"📰 총 {len(json_files)}개 JSON 처리")

    for filename in json_files:
        filepath = os.path.join(directory_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        titles = [item.get("title", "") for item in data if isinstance(item, dict)]
        print(f" - {filename}: {len(titles)}건")

        for t in titles:
            cleaned = clean_text(t)
            if not cleaned:
                continue
            if use_konlpy:
                tokens = tokenize_konlpy(cleaned)
            else:
                tokens = tokenize_fallback(cleaned)
            all_tokens.extend(tokens)

    print(f"✅ 총 토큰 수: {len(all_tokens)}")
    return all_tokens

if __name__ == "__main__":
    DATA_DIRECTORY = "collected_data"
    OUTPUT_FILENAME = "final_tokenized_words.txt"

    words = preprocess_data(DATA_DIRECTORY)
    if not words:
        print("❌ 결과가 비어있음 (수집 데이터/폴더 확인)")
        raise SystemExit(1)

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(words))

    print(f"✅ 저장 완료: {OUTPUT_FILENAME}")