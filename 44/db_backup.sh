#!/bin/bash
# 백업 파일을 저장할 폴더 생성
BACKUP_DIR="./db_backups"
mkdir -p $BACKUP_DIR

# 날짜를 파일명에 붙이기 위한 변수
DATE=$(date +%Y%m%d_%H%M%S)

# 도커 컨테이너 내부의 mysqldump를 실행하여 외부로 백업 파일 추출
docker exec movie_mysql mysqldump -u root -proot_password_1234 movie_recommend_db > $BACKUP_DIR/backup_$DATE.sql

echo "데이터베이스 백업 완료: backup_$DATE.sql"
