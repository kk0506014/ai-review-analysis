import requests
import csv
import re

url = "https://store.steampowered.com/appreviews/413150"

params = {
    "json": 1,
    "language": "korean",
    "num_per_page": 100
}

reviews_list = []
cursor = "*"

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

sample_reviews = [
    "<b>정말 재미있어요!!</b>",
    "농장 게임 중 최고입니다ㅎㅎㅎㅎ",
    "GOOD GAME!!!"
]

for review in sample_reviews:
    print("원본:", review)
    print("전처리:", clean_text(review))
    print("-" * 50)

while len(reviews_list) < 1000:

    params["cursor"] = cursor
    response = requests.get(url, params=params)
    data = response.json()

    for r in data["reviews"]:
        reviews_list.append(r["review"])

    cursor = data["cursor"]

with open("stardew_valley_reviews_kr.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["review"])

    for review in reviews_list:
        writer.writerow([review])

print("리뷰 수집 완료:", len(reviews_list))