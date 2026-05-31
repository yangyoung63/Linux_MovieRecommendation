프로젝트 실행 방법
<폴더 다운>
movie-project/
├── main.py             ← 백엔드
├── data/
│   └── movies.xlsx     ← db
├── index.html          ← 프론트엔드
├── requirements.txt    ← 컴퓨터에 install
└── README.md           ← 설명

<cmd> 
>>cd C:폴더 경로
>>dir(로 main.py등이 들어있음 굿!)
>>pip install -r requirements.txt
>>python main.py

<브라우저>
http://localhost:5000 하면 됩니다!




1. 정렬 기준을 바꾸고 싶을 때 (order_by 파라미터 추가):

별점 높은 순: GET /api/movies?emotion=울고 싶어&order_by=rating

최신 개봉 순: GET /api/movies?emotion=울고 싶어&order_by=year

-UI에 드롭다운이나 버튼 만들어서 선택 창 바뀔 때마다 뒤에 &order_by=rating 또는 &order_by=year 붙여서 다시 호출(fetch)해 주면 실시간으로 정렬된 데이터가 갈 겁니당
-엑셀 모드랑 DB 모드 둘 다 지원하니까 화면에 정렬 UI 붙일 때 참고하세용


2.API 응답 데이터 예시 (movie.ott 구조): 
[
  {
    "platform": "넷플릭스",
    "type": "구독",
    "rent_price": null,
    "buy_price": null
  },
  {
    "platform": "네이버 시리즈온",
    "type": "대여",
    "rent_price": 5000,
    "buy_price": 11000
  }
]
index.html 파일 맨 아래쪽에 보면 OTT 리스트를 화면에 그려주는 function renderOtt(ottList) 함수가 있습니당

지금은 그냥 단순 텍스트로 합쳐서 (platform | type | 가격) 띄우게 짜여 있는데, 
원하는 UI 레이아웃이나 디자인이 있다면 이 renderOtt 함수 내부를 커스텀해서 띄우면 된답니당
