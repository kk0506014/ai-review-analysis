import pymysql
import pandas as pd

# DB 연결
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="3213",
    database="reviews",
    charset="utf8mb4"
)

# 테이블 조회
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

# SQL 조회 결과를 pandas DataFrame으로 변환
df = pd.read_sql(query, conn)

# DB 연결 종료
conn.close()

# 데이터 기본 확인
print("데이터 조회 완료")
print("전체 리뷰 수:", len(df))

print("\n[상위 5개 데이터]")
print(df.head())

print("\n[데이터 컬럼 정보]")
print(df.info())

print("\n[결측치 확인]")
print(df.isnull().sum())

# 추천 여부 분포 확인
print("\n[추천 여부 분포]")
print(df["recommend"].value_counts())

print("\n[추천 여부 비율]")
print(df["recommend"].value_counts(normalize=True) * 100)

# 수치형 데이터 기초 통계
print("\n[수치형 데이터 기초 통계]")
print(df[["likes", "funny", "playtime"]].describe())

# 좋아요 수가 많은 리뷰 조회
top_likes = df.sort_values(by="likes", ascending=False).head(10)

print("\n[좋아요 수 상위 10개 리뷰]")
print(top_likes[["id", "review", "recommend", "likes", "playtime", "created_at"]])

# 플레이 시간이 긴 사용자 리뷰 조회
top_playtime = df.sort_values(by="playtime", ascending=False).head(10)

print("\n[플레이 시간이 긴 사용자 리뷰 상위 10개]")
print(top_playtime[["id", "review", "recommend", "likes", "playtime"]])

# 분석용 CSV 저장
df.to_csv("steam_reviews_analysis.csv", index=False, encoding="utf-8-sig")
print("\n분석용 CSV 파일 저장 완료: steam_reviews_analysis.csv")