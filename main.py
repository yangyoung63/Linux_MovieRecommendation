import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI()

# 프론트엔드가 포트 80에서 동작하므로 CORS 접근 허용 필수
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    # docker-compose.yml의 환경변수 매핑 반영 (DB_NAME 주의)
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root_password_1234"),
        database=os.getenv("DB_NAME", "movie_recommend_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/api/movies")
def get_movies(
    emotion: str = Query(None),
    order_by: str = Query("rating")
):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 1. 메인 영화 정보 쿼리 (m.movie_id 명시하여 에러 해결)
            sql = """
                SELECT 
                    m.movie_id, m.title, m.genre, m.year, m.rating, m.emotion, m.time,
                    m.positive_review, m.negative_review
                FROM movies m
            """
            params = []
            
            if emotion:
                sql += " WHERE m.emotion = %s"
                params.append(emotion)
                
            if order_by == "rating":
                sql += " ORDER BY m.rating DESC"
            elif order_by == "title":
                sql += " ORDER BY m.title ASC"
                
            cursor.execute(sql, params)
            movies = cursor.fetchall()
            
            # 2. 각 영화별 OTT 플랫폼 매핑 (HTML의 renderOttInfo 연동)
            for movie in movies:
                ott_sql = """
                    SELECT platform, type, rent_price, buy_price, price 
                    FROM ott_offers 
                    WHERE movie_id = %s
                """
                cursor.execute(ott_sql, (movie['movie_id'],))
                movie['ott'] = cursor.fetchall() # html 내부의 movie.ott 키값과 일치하게 매핑
                
            # 3. CRITICAL: 프론트엔드 규격에 맞춘 딕셔너리 구조 반환
            return {
                "status": "success",
                "data": movies
            }

    except Exception as e:
        print(f"서버 내부 에러 발생: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
