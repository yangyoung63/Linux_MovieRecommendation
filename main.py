import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from typing import List, Dict

app = FastAPI()

# HTML 렌더링을 위한 템플릿 엔진 설정
templates = Jinja2Templates(directory="templates")

# 💡 Mock 데이터베이스 (추후 SQL/Excel 전달받으면 이 영역을 실제 DB 쿼리로 교체합니다.)
movie_db: Dict[str, List[Dict]] = {
    "친구랑 보고 싶어": [
        {
            "id": 1, "title": "극한직업", "genre": "코미디", "year": "2019", "time": "111분", "rating": "8.5",
            "ott": ["Netflix", "Wavve", "Coupang Play"], "pos": "친구들이랑 통닭 시켜놓고 깔깔거리며 보기 최적화된 영화!", "neg": "웃음 타율은 높지만 깊은 스토리를 기대하긴 어렵습니다."
        },
        {
            "id": 2, "title": "어벤져스: 엔드게임", "genre": "액션/SF", "year": "2019", "time": "181분", "rating": "9.3",
            "ott": ["Disney+"], "pos": "웅장함의 끝판왕. 마블 팬인 친구와 밤새 수다 떨 수 있습니다.", "neg": "이전 세계관 시리즈들을 정주행하지 않았다면 소외감 느낍니다."
        },
        {
            "id": 3, "title": "써니", "genre": "드라마", "year": "2011", "time": "124분", "rating": "8.9",
            "ott": ["Netflix", "Wavve", "TVING"], "pos": "학창 시절 추억 소환 제대로 됩니다. 친구들과 옛날 얘기하게 만드는 마법.", "neg": "일부 과거 미화나 다소 자극적인 욕설 신이 호불호 갈려요."
        }
    ],
    "웃고 싶어": [
        {
            "id": 4, "title": "스파이", "genre": "코미디/액션", "year": "2015", "time": "120분", "rating": "8.8",
            "ott": ["Disney+"], "pos": "멜리사 맥카시와 제이슨 스타뎀의 말도 안 되는 코믹 티키타카!", "neg": "미국식 B급 유머와 드립이 안 맞으면 유치할 수 있어요."
        },
        {
            "id": 5, "title": "육사오(6/45)", "genre": "코미디", "year": "2022", "time": "113분", "rating": "8.3",
            "ott": ["Netflix", "TVING"], "pos": "로또 한 장으로 시작되는 남북 군인들의 선 넘는 대환장 코미디.", "neg": "후반부 결말 처리가 살짝 억지스럽게 느껴질 수 있습니다."
        }
    ],
    "설레고 싶어": [
        {
            "id": 6, "title": "어바웃 타임", "genre": "로맨스/판타지", "year": "2013", "time": "123분", "rating": "9.2",
            "ott": ["Netflix", "Wavve"], "pos": "레이첼 맥아담스의 미소와 인생에 대한 따뜻한 교훈이 녹아있음.", "neg": "시간 여행 판타지 장르 특성상 개연성 구멍이 조금 보입니다."
        }
    ]
}

# 1. 처음 도메인 주소 진입 시 프론트엔드 화면을 보여주는 엔드포인트
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 2. 💡 감정명을 매개변수로 받아 목록을 랜덤으로 섞어 돌려주는 API
@app.get("/api/movies")
def get_movies_by_emotion(emotion: str):
    # 등록되지 않은 감정이 오면 빈 리스트 반환
    movies = movie_db.get(emotion, []).copy()
    
    # 🎲 데이터 순서를 랜덤하게 무작위로 섞어줍니다.
    random.shuffle(movies)
    
    return {"status": "success", "data": movies}
