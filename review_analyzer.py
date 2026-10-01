import re
from collections import Counter

import pandas as pd

from db_config import get_connection

def load_reviews():
    query = """
    SELECT
        id,
        user_id,
        review,
        recommend,
        likes,
        funny,
        playtime,
        created_at
    FROM reviews
    ORDER BY id ASC
    """

    if get_connection is not None:
        try:
            conn = get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            print("DB 데이터 조회 완료")
            return df
        except Exception as e:
            print("DB 조회 실패, CSV 파일로 대체")
            print("오류 내용:", e)

    df = pd.read_csv("steam_reviews_analysis.csv")
    print("CSV 데이터 조회 완료")
    return df


# 데이터 불러오기
df = load_reviews()

# 분석에 필요한 파생 변수 생성
df["recommend"] = df["recommend"].astype(int)
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["review_length"] = df["review"].astype(str).str.len()
df["playtime_hours"] = (df["playtime"] / 60).round(1)
df["created_date"] = df["created_at"].dt.date

# 전체 데이터 규모 확인
print("\n전체 데이터 규모")
print("전체 리뷰 수:", len(df))
print("고유 사용자 수:", df["user_id"].nunique())
print("수집 기간:", df["created_at"].min(), "~", df["created_at"].max())

# 결측치 확인
print("\n결측치 확인")
print(df[["id", "user_id", "review", "recommend", "likes", "funny", "playtime", "created_at"]].isnull().sum())

# 추천 여부 분포
recommend_count = df["recommend"].value_counts().sort_index()
recommend_ratio = (df["recommend"].value_counts(normalize=True).sort_index() * 100).round(2)

recommend_summary = pd.DataFrame({
    "구분": ["비추천", "추천"],
    "리뷰 수": [recommend_count.get(0, 0), recommend_count.get(1, 0)],
    "비율(%)": [recommend_ratio.get(0, 0), recommend_ratio.get(1, 0)]
})

print("\n추천 여부 분포")
print(recommend_summary)

# 수치형 데이터 기초 통계
numeric_summary = df[["likes", "funny", "playtime", "playtime_hours", "review_length"]].describe().round(2)

print("\n수치형 데이터 기초 통계")
print(numeric_summary)

# 작성일 기준 리뷰 수
daily_review_count = df.groupby("created_date").size().reset_index(name="review_count")
daily_review_count = daily_review_count.sort_values(by="created_date")

print("\n날짜별 리뷰 수 상위 10개")
print(daily_review_count.sort_values(by="review_count", ascending=False).head(10))

# 좋아요 수 상위 리뷰
top_likes = df.sort_values(by="likes", ascending=False).head(10)

print("\n좋아요 수 상위 10개 리뷰")
print(top_likes[["id", "review", "recommend", "likes", "funny", "playtime_hours", "created_at"]])

# 플레이 시간이 긴 사용자 리뷰
top_playtime = df.sort_values(by="playtime", ascending=False).head(10)

print("\n플레이 시간이 긴 사용자 리뷰 상위 10개")
print(top_playtime[["id", "review", "recommend", "likes", "funny", "playtime_hours", "created_at"]])

# 분석 결과 저장
recommend_summary.to_csv("recommend_summary.csv", index=False, encoding="utf-8-sig")
numeric_summary.to_csv("numeric_summary.csv", encoding="utf-8-sig")
daily_review_count.to_csv("daily_review_count.csv", index=False, encoding="utf-8-sig")
top_likes.to_csv("top_likes.csv", index=False, encoding="utf-8-sig")
top_playtime.to_csv("top_playtime.csv", index=False, encoding="utf-8-sig")

print("\n기초 통계 분석 결과 저장 완료")

df["recommend_label"] = df["recommend"].map({
    1: "추천",
    0: "비추천"
})

df["has_likes"] = df["likes"] >= 1
df["has_funny"] = df["funny"] >= 1


recommend_group_summary = []

for label in ["추천", "비추천"]:
    group = df[df["recommend_label"] == label]

    if len(group) == 0:
        continue

    recommend_group_summary.append({
        "구분": label,
        "리뷰 수": len(group),

        "좋아요 평균": round(group["likes"].mean(), 2),
        "좋아요 중앙값": round(group["likes"].median(), 2),
        "좋아요 최댓값": group["likes"].max(),
        "좋아요 1개 이상 비율(%)": round(
            group["has_likes"].mean() * 100, 2
        ),

        "재미 평가 평균": round(group["funny"].mean(), 2),
        "재미 평가 중앙값": round(group["funny"].median(), 2),
        "재미 평가 최댓값": group["funny"].max(),
        "재미 평가 1개 이상 비율(%)": round(
            group["has_funny"].mean() * 100, 2
        ),

        "플레이 시간 평균(시간)": round(
            group["playtime_hours"].mean(), 2
        ),
        "플레이 시간 중앙값(시간)": round(
            group["playtime_hours"].median(), 2
        ),
        "플레이 시간 최댓값(시간)": round(
            group["playtime_hours"].max(), 2
        ),

        "리뷰 길이 평균(자)": round(
            group["review_length"].mean(), 2
        ),
        "리뷰 길이 중앙값(자)": round(
            group["review_length"].median(), 2
        ),
        "리뷰 길이 최댓값(자)": group["review_length"].max()
    })


recommend_group_summary = pd.DataFrame(
    recommend_group_summary
)

print("\n추천 여부 기반 사용자 반응 분석")
print(recommend_group_summary.to_string(index=False))


representative_reviews = []

for label in ["추천", "비추천"]:
    group = df[df["recommend_label"] == label]

    top_reviews = (
        group
        .sort_values(
            by=["likes", "review_length"],
            ascending=[False, False]
        )
        .head(5)
    )

    representative_reviews.append(
        top_reviews[
            [
                "id",
                "recommend_label",
                "review",
                "likes",
                "funny",
                "playtime_hours",
                "review_length",
                "created_at"
            ]
        ]
    )


representative_reviews = pd.concat(
    representative_reviews,
    ignore_index=True
)


print("\n추천/비추천 대표 리뷰")
print(representative_reviews.to_string(index=False))


recommend_group_summary.to_csv(
    "recommend_group_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

representative_reviews.to_csv(
    "recommend_group_representative_reviews.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n추천 여부 기반 사용자 반응 분석 완료")