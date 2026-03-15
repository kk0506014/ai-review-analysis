import requests
import csv

url = "https://store.steampowered.com/appreviews/413150"

params = {
    "json": 1,
    "language": "korean",
    "num_per_page": 100
}

reviews_list = []
cursor = "*"

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