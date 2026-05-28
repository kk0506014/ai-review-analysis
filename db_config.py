import pymysql

# DB 연결
def get_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="3213",
        database="reviews",
        charset="utf8mb4"
    )

    return conn