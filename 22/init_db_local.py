"""
로컬 DB 초기화 스크립트
======================================
CSV 파일을 읽어서 MySQL에 데이터를 넣습니다.
Docker 실행 전 or 후에 한 번만 실행하면 됩니다.

실행 방법:
    python init_db_local.py

필요한 패키지:
    pip install pandas mysql-connector-python openpyxl
"""

import os
import re
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ── 접속 정보 (docker-compose.yml 기준과 동일하게 맞춤) ──────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")   # 로컬 실행이므로 localhost
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root_password_1234")
DB_NAME     = os.getenv("DB_NAME", "movie_recommend_db")

# ── CSV 파일 경로 (같은 폴더에 있어야 함) ────────────────────────────────────
MOVIES_CSV = "movies.xlsx - Movies.csv"
OTT_CSV    = "movies.xlsx - OTT_Offers.csv"


def create_database_and_tables(cursor):
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.execute(f"USE `{DB_NAME}`")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id     VARCHAR(20)  PRIMARY KEY,
            title        VARCHAR(255),
            genre        VARCHAR(100),
            year         INT,
            runtime      INT,
            rating       FLOAT,
            label1       VARCHAR(100),
            label2       VARCHAR(100),
            is_certain   INT DEFAULT 0,
            positive_review  TEXT,
            negative_review  TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ott_offers (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            movie_id   VARCHAR(20),
            platform   VARCHAR(50),
            type       VARCHAR(20),
            rent_price INT,
            buy_price  INT,
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("[INFO] DB 및 테이블 준비 완료.")


def insert_data(cursor, connection):
    if not os.path.exists(MOVIES_CSV) or not os.path.exists(OTT_CSV):
        print(f"[ERROR] CSV 파일을 찾을 수 없습니다.\n"
              f"  찾는 파일: {MOVIES_CSV}\n"
              f"             {OTT_CSV}\n"
              f"  이 스크립트와 같은 폴더에 넣어주세요.")
        return

    movies_df = pd.read_csv(MOVIES_CSV).where(pd.notnull(pd.read_csv(MOVIES_CSV)), None)
    ott_df    = pd.read_csv(OTT_CSV).where(pd.notnull(pd.read_csv(OTT_CSV)), None)

    # 기존 데이터 초기화 (재실행 시 중복 방지)
    cursor.execute("DELETE FROM ott_offers")
    cursor.execute("DELETE FROM movies")

    # ── 영화 삽입 ─────────────────────────────────────────────────────────────
    movie_sql = """
        INSERT INTO movies
            (movie_id, title, genre, year, runtime, rating,
             label1, label2, is_certain, positive_review, negative_review)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    movie_records = []
    for _, row in movies_df.iterrows():
        if not row.iloc[0]:
            continue
        movie_records.append((
            str(row.iloc[0]),   # movie_id
            row.iloc[1],        # title
            row.iloc[2],        # genre
            row.iloc[3],        # year
            row.iloc[4],        # runtime
            row.iloc[5],        # rating
            row.iloc[6],        # label1
            row.iloc[7],        # label2
            row.iloc[8],        # is_certain
            row.iloc[9],        # positive_review
            row.iloc[10],       # negative_review
        ))
    cursor.executemany(movie_sql, movie_records)
    print(f"[INFO] 영화 {len(movie_records)}건 삽입 완료.")

    # ── OTT 삽입 (M42 → M042 오타 보정 포함) ─────────────────────────────────
    ott_sql = """
        INSERT INTO ott_offers (movie_id, platform, type, rent_price, buy_price)
        VALUES (%s, %s, %s, %s, %s)
    """
    ott_records = []
    for _, row in ott_df.iterrows():
        if not row.iloc[0]:
            continue
        raw_mid = str(row.iloc[0]).strip()
        mid = re.sub(r'^(M)(\d{2})$', lambda m: m.group(1) + '0' + m.group(2), raw_mid)
        ott_records.append((
            mid,          # movie_id (오타 보정됨)
            row.iloc[1],  # platform
            row.iloc[2],  # type
            row.iloc[3],  # rent_price
            row.iloc[4],  # buy_price
        ))
    cursor.executemany(ott_sql, ott_records)
    print(f"[INFO] OTT {len(ott_records)}건 삽입 완료.")

    connection.commit()
    print("[SUCCESS] 데이터 삽입 완료!")


def main():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        if connection.is_connected():
            cursor = connection.cursor()
            create_database_and_tables(cursor)
            insert_data(cursor, connection)
    except Error as e:
        print(f"[ERROR] MySQL 연결 실패: {e}\n"
              f"MySQL 서버가 켜져 있는지, 비밀번호가 맞는지 확인하세요.\n"
              f"현재 설정: host={DB_HOST}, user={DB_USER}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
