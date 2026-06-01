# 1. 파이썬 공식 이미지 사용
FROM python:3.10-slim

# 2. 작업 폴더 지정
WORKDIR /app

# 3. 필요한 패키지 설치
RUN pip install --no-cache-dir flask pymysql cryptography

# 4. 방금 우리가 작성한 app.py를 컨테이너 내부로 복사!
COPY app.py /app/app.py

# 5. 백엔드 포트 개방
EXPOSE 5000

# 6. 플라스크 서버 실행 (python app.py)
CMD ["python", "app.py"]
