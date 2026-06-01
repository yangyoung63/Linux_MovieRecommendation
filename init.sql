CREATE DATABASE IF NOT EXISTS movie_recommend_db;
USE movie_recommend_db;

-- 1. 영화 테이블 생성
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    year INT,
    rating DECIMAL(3, 1) DEFAULT 0.0,
    emotion VARCHAR(100) NOT NULL,
    time INT, -- 상영 시간(분)
    positive_review TEXT,
    negative_review TEXT
);

-- 2. OTT 정보 테이블 생성 (영화와 1:N 관계)
CREATE TABLE IF NOT EXISTS ott_offers (
    ott_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    platform VARCHAR(100) NOT NULL, -- 예: Netflix, Watcha
    type VARCHAR(50),               -- 예: 구독, 대여, 소장
    rent_price INT DEFAULT NULL,
    buy_price INT DEFAULT NULL,
    price INT DEFAULT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

-- 3. 테스트용 데이터 삽입
INSERT INTO movies (movie_id, title, genre, year, rating, emotion, time, positive_review, negative_review) VALUES
(1, '식스 센스', '스릴러', 1999, 4.8, '반전을 보고 싶어', 130, '소름 돋는 연출과 완벽한 플롯', '중반부 전개가 다소 느림'),
(2, '인셉션', 'SF', 2010, 4.7, '반전을 보고 싶어', 148, '각본과 영상미의 완벽한 조화', '설명이 많아 다소 복잡함');

INSERT INTO ott_offers (movie_id, platform, type, rent_price, buy_price, price) VALUES
(1, 'Netflix', '구독', NULL, NULL, NULL),
(1, 'Wave', '대여', 1200, NULL, NULL),
(2, 'Netflix', '구독', NULL, NULL, NULL),
(2, 'Google Play', '소장', NULL, 4500, NULL);