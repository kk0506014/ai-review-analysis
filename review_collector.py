import requests
import pymysql
import re
from datetime import datetime

# DB 연결
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="3213",
    database="reviews",
    charset="utf8mb4"
)

cursor_db = conn.cursor()

# 테이블 생성
cursor_db.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    review TEXT,
    recommend BOOLEAN,
    likes INT,
    funny INT,
    playtime INT,
    created_at DATETIME
)
""")

url = "https://store.steampowered.com/appreviews/413150"

params = {
    "json": 1,
    "language": "korean",
    "num_per_page": 100
}

cursor_api = "*"


def clean_text(text):
    # HTML 태그 제거
    text = re.sub(r"<.*?>", "", text)

    # 특수문자 제거
    text = re.sub(r"[^\w\s가-힣]", "", text)

    # 소문자 변환
    text = text.lower()

    # 공백 정리
    text = re.sub(r"\s+", " ", text).strip()

    return text


count = 0
review_set = set()
prev_cursor = None

while count < 400:
    params["cursor"] = cursor_api

    response = requests.get(url, params=params)
    data = response.json()

    new_cursor = data.get("cursor")

    if new_cursor == prev_cursor:
        print("cursor 고정 → 종료")
        break

    if not data.get("reviews"):
        print("리뷰 없음 → 종료")
        break

    count_before = count

    for r in data["reviews"]:
        raw_text = r["review"]
        review_text = clean_text(raw_text)

        # 너무 짧은 리뷰 제외
        if len(review_text) < 10:
            continue

        # 중복 리뷰 제외
        if review_text in review_set:
            continue

        review_set.add(review_text)

        user_id = r["author"]["steamid"]
        recommend = r["voted_up"]
        likes = r["votes_up"]
        funny = r["votes_funny"]
        playtime = r["author"]["playtime_forever"]

        # 작성 시간 수집
        timestamp = r.get("timestamp_created")

        if timestamp:
            created_at = datetime.fromtimestamp(timestamp)
        else:
            created_at = None

        cursor_db.execute("""
        INSERT INTO reviews (
            user_id,
            review,
            recommend,
            likes,
            funny,
            playtime,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            review_text,
            recommend,
            likes,
            funny,
            playtime,
            created_at
        ))

        count += 1

        if count >= 400:
            break

    conn.commit()

    # 새로 저장된 리뷰가 없으면 종료
    if count == count_before:
        print(f"새 리뷰 없음 (총 {count}개) → 종료")
        break

    prev_cursor = cursor_api
    cursor_api = new_cursor

    print(f"현재 count: {count}")

print("전처리 및 DB 저장 완료:", count)

conn.close()