# 202534823 박진환 - 워드클라우드 생성 코드

from collections import Counter
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 병준이가 만든 토큰 결과 파일
TOKEN_FILE = "final_tokenized_words.txt"

# 출력 폴더
OUTPUT_DIR = Path("wordcloud_outputs")

# 윈도우 기준 한글 폰트 경로 (맑은고딕)
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"


def load_tokens(path: str) -> list:
    """토큰 txt 파일 읽기"""
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 토큰 파일을 찾을 수 없습니다: {p.resolve()}")
        print("→ JSON 수집 & 전처리 코드를 먼저 실행하세요.")
        return []

    with p.open("r", encoding="utf-8") as f:
        tokens = [line.strip() for line in f if line.strip()]

    print(f"[INFO] 총 {len(tokens)}개의 토큰을 로드했습니다.")
    return tokens


def build_freq(tokens: list) -> dict:
    """단어별 빈도 계산"""
    return dict(Counter(tokens))


def make_wordcloud(freq: dict, output_name: str):
    """워드클라우드 생성"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    wc = WordCloud(
        width=1000,
        height=600,
        background_color="white",
        font_path=FONT_PATH
    ).generate_from_frequencies(freq)

    plt.figure(figsize=(15, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")

    save_path = OUTPUT_DIR / output_name
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()

    print(f"[DONE] 워드클라우드 저장 완료 → {save_path.resolve()}")


def main():
    tokens = load_tokens(TOKEN_FILE)
    if not tokens:
        return
    
    freq = build_freq(tokens)
    make_wordcloud(freq, "wordcloud_all.png")


if __name__ == "__main__":
    main()

