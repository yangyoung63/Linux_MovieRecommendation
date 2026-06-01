"""
영화 추천 서비스 - FastAPI 백엔드 (SQL 전용)
======================================
- MySQL 전용. DB 연결 실패 시 서버 구동 중단.
- 환경변수는 docker-compose.yml 기준:
    DB_HOST=db
    DB_USER=root
    DB_PASSWORD=root_password_1234
    DB_NAME=movie_recommend_db
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ── 환경 변수 (docker-compose.yml 기준) ───────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "db")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root_password_1234")
DB_NAME     = os.getenv("DB_NAME", "movie_recommend_db")

# ── 전역 커넥션 풀 ─────────────────────────────────────────────────────────────
_db_pool = None


# ── DB 연결 풀 초기화 ──────────────────────────────────────────────────────────
def init_db_pool():
    global _db_pool
    try:
        from mysql.connector import pooling
        _db_pool = pooling.MySQLConnectionPool(
            pool_name="movie_pool",
            pool_size=5,
            pool_reset_session=True,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
        )
        # 연결 테스트
        conn = _db_pool.get_connection()
        conn.close()
        print(f"[INFO] MySQL 연결 성공: {DB_HOST}/{DB_NAME}")
    except Exception as e:
        print(f"[CRITICAL] MySQL 연결 실패: {e}")
        raise e


# ── FastAPI Lifespan ───────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_pool()
    yield


app = FastAPI(title="영화 추천 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── DB 조회 헬퍼 ───────────────────────────────────────────────────────────────

def _db_get_movies_by_emotion(emotion: str, order_by: str = "rating") -> list[dict]:
    conn = _db_pool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        order_sql = "ORDER BY m.is_certain DESC, m.rating DESC"
        if order_by == "year":
            order_sql = "ORDER BY m.year DESC"

        query = f"""
            SELECT m.movie_id AS id, m.title, m.genre, m.year,
                   CONCAT(m.runtime, '분') AS time,
                   m.rating, m.label1, m.label2, m.is_certain,
                   m.positive_review AS pos, m.negative_review AS neg
            FROM movies m
            WHERE m.label1 = %s OR m.label2 = %s
            {order_sql}
        """
        cur.execute(query, (emotion, emotion))
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    for row in rows:
        row["ott"] = _db_get_ott(row["id"])
        if row["rating"]:
            row["rating"] = float(row["rating"])
    return rows


def _db_get_ott(movie_id: str) -> list[dict]:
    conn = _db_pool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT platform, type, rent_price, buy_price FROM ott_offers WHERE movie_id = %s",
            (movie_id,),
        )
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    return rows


def _db_get_movie_detail(movie_id: str) -> Optional[dict]:
    conn = _db_pool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT movie_id AS id, title, genre, year,
                   CONCAT(runtime, '분') AS time, rating,
                   label1, label2, is_certain,
                   positive_review AS pos, negative_review AS neg
            FROM movies WHERE movie_id = %s
            """,
            (movie_id,),
        )
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not row:
        return None
    row["ott"] = _db_get_ott(movie_id)
    if row["rating"]:
        row["rating"] = float(row["rating"])
    return row


def _db_search_movies(q: str) -> list[dict]:
    conn = _db_pool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT movie_id AS id, title, genre, year,
                   CONCAT(runtime, '분') AS time, rating,
                   label1, label2, is_certain,
                   positive_review AS pos, negative_review AS neg
            FROM movies
            WHERE LOWER(title) LIKE %s
            ORDER BY rating DESC
            """,
            (f"%{q.lower()}%",),
        )
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    for row in rows:
        row["ott"] = _db_get_ott(row["id"])
        if row["rating"]:
            row["rating"] = float(row["rating"])
    return rows


# ── API 엔드포인트 ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "db", "db_host": DB_HOST}


@app.get("/api/emotions")
def get_emotions():
    emotions = [
        "울고 싶어", "웃고 싶어", "감동받고 싶어", "설레고 싶어",
        "긴장감을 느끼고 싶어", "몰입하고 싶어", "반전을 보고 싶어",
        "생각하게 만드는 영화를 보고 싶어", "성장 이야기가 보고 싶어",
        "미장센이 좋은 영화를 보고 싶어", "음악이 좋은 영화를 보고 싶어",
        "가벼운 마음으로 시간을 보내고 싶어", "친구랑 보고 싶어", "가족이랑 보고 싶어",
    ]
    return {"emotions": emotions}


@app.get("/api/movies")
def get_movies(emotion: str = "", order_by: str = "rating"):
    """
    감정 기반 영화 추천.
    order_by="rating" → 별점순 (기본값)
    order_by="year"   → 최신순
    """
    if not emotion:
        raise HTTPException(status_code=400, detail="emotion 파라미터가 필요합니다.")

    movies = _db_get_movies_by_emotion(emotion.strip(), order_by)
    for m in movies:
        m["ott_names"] = [o["platform"] for o in m.get("ott", [])]
    return {"status": "success", "emotion": emotion, "count": len(movies), "data": movies}


@app.get("/api/movies/{movie_id}")
def get_movie_detail(movie_id: str):
    movie = _db_get_movie_detail(movie_id.upper())
    if not movie:
        raise HTTPException(status_code=404, detail=f"영화 ID '{movie_id}'를 찾을 수 없습니다.")
    movie["ott_names"] = [o["platform"] for o in movie.get("ott", [])]
    return {"status": "success", "data": movie}


@app.get("/api/search")
def search_movies(q: str = ""):
    if not q:
        raise HTTPException(status_code=400, detail="q 파라미터가 필요합니다.")
    results = _db_search_movies(q)
    for m in results:
        m["ott_names"] = [o["platform"] for o in m.get("ott", [])]
    return {"status": "success", "query": q, "count": len(results), "data": results}


# ── 정적 파일 서빙 ─────────────────────────────────────────────────────────────
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
def serve_index():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "index.html 이 없습니다."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
