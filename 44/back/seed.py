# 2. Movies.csv 삽입 (칸 수 불일치 에러 완벽 방어 코드로 수정)
    try:
        with open('/app/Movies.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader) # 헤더행 건너뛰기
            success_count = 0
            for row in reader:
                if not row: continue
                
                # [여기가 핵심!] 공백 제거 가공
                clean_row = [None if str(val).strip() == '' else str(val).strip() for val in row]
                
                # 🚨 데이터 개수가 10개가 안 되거나 넘치면 10개로 강제로 맞춰주는 무적 코드
                if len(clean_row) < 10:
                    clean_row += [None] * (10 - len(clean_row)) # 부족하면 None으로 채움
                elif len(clean_row) > 10:
                    clean_row = clean_row[:10] # 넘치면 앞의 10개만 자름

                try:
                    cursor.execute("""
                        INSERT INTO movies (id, title, genre, release_year, runtime, rating, label1, label2, positive_review, negative_review)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, clean_row)
                    success_count += 1
                except Exception as e:
                    print(f"영화 삽입 에러 ({clean_row[0] if clean_row else '알수없음'}): {e}")
                    continue
        print(f"Movies.csv 데이터 주입 완료 ({success_count}개)")
    except Exception as e:
        print(f"Movies.csv 파일 읽기 실패: {e}")
