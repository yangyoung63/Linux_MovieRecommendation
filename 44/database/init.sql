USE movie_recommend_db;

-- 1. 영화 테이블 생성 (총 10개 컬럼 구조)
CREATE TABLE IF NOT EXISTS movies (
    id VARCHAR(50) PRIMARY KEY,               -- 영화ID
    title VARCHAR(255) NOT NULL,              -- 영화제목
    genre VARCHAR(100),                       -- 장르
    release_year INT,                         -- 개봉 연도
    runtime INT,                              -- 상영 시간(분)
    rating DECIMAL(3, 1),                     -- 평점
    label1 VARCHAR(100),                      -- label1
    label2 VARCHAR(100),                      -- label2
    positive_review TEXT,                     -- 긍정 평론 (핵심 요약)
    negative_review TEXT                      -- 부정 평론 (핵심 요약)
);

-- 2. OTT 제공 정보 테이블 생성
CREATE TABLE IF NOT EXISTS ott_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id VARCHAR(50),                     -- 영화ID
    platform VARCHAR(100),                    -- OTT 플랫폼
    type VARCHAR(50),                         -- 제공 방식
    rent_price INT NULL,                      -- 대여 가격
    buy_price INT NULL,                       -- 소장 가격
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);
