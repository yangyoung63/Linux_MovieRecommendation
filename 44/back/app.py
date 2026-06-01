import json
from decimal import Decimal
from flask import Flask, request, Response
import pymysql
import os

app = Flask(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root_password_1234'),
        database=os.environ.get('DB_NAME', 'movie_recommend_db'),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

@app.route('/api/moods', methods=['GET'])
def get_moods():
    data = {
        "moods": ["울고 싶어", "웃고 싶어", "감동받고 싶어", "설레고 싶어", "긴장감을 느끼고 싶어", 
                  "몰입하고 싶어", "반전을 보고 싶어", "생각하게 만드는 영화를 보고 싶어", 
                  "성장 이야기가 보고 싶어", "미장센이 좋은 영화를 보고 싶어", "음악이 좋은 영화를 보고 싶어", 
                  "가벼운 마음으로 시간을 보내고 싶어", "친구랑 보고 싶어", "가족이랑 보고 싶어"]
    }
    return Response(json.dumps(data, ensure_ascii=False), mimetype='application/json')

# 2. 랜덤 추천 API
@app.route('/api/recommend/random', methods=['GET'])
def recommend_random():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM movies ORDER BY RAND() LIMIT 1")
    movie = cursor.fetchone()
    
    if movie:
        cursor.execute("SELECT * FROM ott_offers WHERE movie_id = %s", (movie['id'],))
        ott_offers = cursor.fetchall()
        movie['ott_offers'] = ott_offers
        
        conn.close()
        result = {"status": "success", "movie": movie}
        return Response(json.dumps(result, ensure_ascii=False, cls=CustomJSONEncoder), mimetype='application/json')
    
    conn.close()
    error_result = {"status": "error", "message": "영화가 없습니다."}
    return Response(json.dumps(error_result, ensure_ascii=False), mimetype='application/json', status=404)

# 3. 맞춤 영화 추천 API (평론 정보는 movies 테이블에 포함되어 함께 나갑니다)
@app.route('/api/recommend', methods=['POST'])
def recommend_movies():
    data = request.json
    selected_mood = data.get('mood') if data else None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM movies 
        WHERE label1 = %s OR label2 = %s 
        ORDER BY rating DESC
    """
    cursor.execute(query, (selected_mood, selected_mood))
    movies = cursor.fetchall()
    
    if movies:
        movie_ids = [m['id'] for m in movies]
        format_strings = ','.join(['%s'] * len(movie_ids))
        
        cursor.execute(f"SELECT * FROM ott_offers WHERE movie_id IN ({format_strings})", tuple(movie_ids))
        all_ott_offers = cursor.fetchall()
        
        for movie in movies:
            movie['ott_offers'] = [ott for ott in all_ott_offers if ott['movie_id'] == movie['id']]
            
        conn.close()
        result = {"status": "success", "count": len(movies), "movies": movies}
        return Response(json.dumps(result, ensure_ascii=False, cls=CustomJSONEncoder), mimetype='application/json')
        
    conn.close()
    error_result = {"status": "error", "message": "조건에 맞는 영화가 없습니다."}
    return Response(json.dumps(error_result, ensure_ascii=False), mimetype='application/json', status=404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
