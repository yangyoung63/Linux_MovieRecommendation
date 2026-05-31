from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from typing import List, Dict

app = FastAPI()

# HTML 파일들을 담아둘 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 💡 임시 영화 데이터베이스 (나중에 엑셀이나 SQL 파일이 오면 이 부분을 DB 조회 코드로 바꿉니다!)
# 프론트엔드 버튼에 적힌 텍스트('친구랑 보고 싶어', '웃고 싶어' 등)를 key로 잡았습니다.
movie_db: Dict[str, List[Dict]] = {
    "친구랑 보고 싶어": [
        {
            "id": 1, "title": "극한직업", "genre": "코미디", "year": "2019", "time": "111분", "rating": "⭐️ 8.5",
            "ott": ["Netflix", "Wave"], "pos": "아무 생각 없이 친구들이랑 배 찢어지게 웃기 최고입니다.", "neg": "스토리가 다소 유치할 수 있습니다."
        },
        {
            "id": 2, "title": "어벤져스: 엔드게임", "genre": "액션/SF", "year": "2019", "time": "181분", "rating": "⭐️ 9.3",
            "ott": ["Disney+"], "pos": "마블의 정점, 친구들과 관람 후 밤새 토론 가능합니다.", "neg": "앞선 시리즈를 안 보면 이해가 안 됩니다."
        }
    ],
    "웃고 싶어": [
        {
            "id": 3, "title": "아이 캔 스피크", "genre": "드라마/코미디", "year": "2017", "time": "119분", "rating": "⭐️ 8.9",
            "ott": ["Wave", "Tving"], "pos": "초반엔 엄청 웃기다가 후반엔 감동까지 챙기는 명작!", "neg": "눈물 짜내는 신파라고 느낄 수도 있어요."
        }
    ],
    "설레고 싶어": [
        {
            "id": 4, "title": "어바웃 타임", "genre": "로맨스/판타지", "year": "2013", "time": "123분", "rating": "⭐️ 9.2",
            "ott": ["Netflix"], "pos": "연애 세포 심폐소생술 가능, 영상미와 음악이 너무 달달함", "neg": "시간 여행 판타지 개연성이 조금 부족해요."
        }
    ]
}

# 1. 웹 브라우저로 처음 접속했을 때 HTML 화면을 띄워주는 API
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 2. 💡 특정 감정을 선택했을 때 영화 목록을 반환하는 API
@app.get("/api/movies")
def get_movies_by_emotion(emotion: str):
    # 등록되지 않은 감정이 들어오면 빈 리스트를 반환하거나 기본값 제공
    movies = movie_db.get(emotion, [])
    return {"status": "success", "data": movies}
