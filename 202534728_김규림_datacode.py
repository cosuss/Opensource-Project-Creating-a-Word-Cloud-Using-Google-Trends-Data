import requests
from bs4 import BeautifulSoup
import json
import os
import time

# ---------------------------------------------------------
# [설정] 검색할 키워드와 연도를 여기서 수정하세요
KEYWORD = "인공지능"
YEAR = 2024
# ---------------------------------------------------------

def get_google_news_titles(keyword, start_date, end_date):
    """구글 뉴스 RSS를 통해 빠르고 안정적으로 뉴스 수집"""
    base_url = "https://news.google.com/rss/search"
    query = f"{keyword} after:{start_date} before:{end_date}"
    
    params = {
        "q": query,
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko"
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    
    news_list = []
    for item in items:
        news_data = {
            "title": item.title.text,
            "link": item.link.text,
            "pub_date": item.pubDate.text
        }
        news_list.append(news_data)
        
    return news_list

def save_to_json(data, filename):
    os.makedirs("collected_data", exist_ok=True)
    filepath = os.path.join("collected_data", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ 저장 완료: {filepath} ({len(data)}건)")

def main():
    print(f"🚀 [{KEYWORD}] 데이터 수집 시작...")
    quarters = {
        "1Q": ("01-01", "03-31"), "2Q": ("04-01", "06-30"),
        "3Q": ("07-01", "09-30"), "4Q": ("10-01", "12-31")
    }

    for q, (start, end) in quarters.items():
        s_date, e_date = f"{YEAR}-{start}", f"{YEAR}-{end}"
        data = get_google_news_titles(KEYWORD, s_date, e_date)
        if data:
            save_to_json(data, f"{YEAR}_{q}_{KEYWORD}.json")
        else:
            print(f"⚠️ {q} 데이터 없음")
        time.sleep(1)

if __name__ == "__main__":
    main()