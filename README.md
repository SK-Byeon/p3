# Yahoo Finance 뉴스 기반 주식 추천 프로그램

`https://finance.yahoo.com/` 메인 페이지 기사 제목을 수집해 테마를 판별하고, 테마별 대표 종목 1개를 추천합니다.

출력에는 아래 항목이 포함됩니다.
- 추천 종목명/종목코드
- 추천 사유(500자 이내)
- 관련 기사 링크

## 설치

```powershell
python -m pip install -r requirements.txt
```

## 실행

```powershell
python stock_recommender.py --article-limit 40 --link-limit 3
```

또는 브라우저용 단일 페이지 버전:

```powershell
start index.html
```

## 옵션

- `--article-limit`: 분석할 기사 최대 개수 (기본값: 40)
- `--link-limit`: 출력할 관련 기사 링크 개수 (기본값: 3)

## 참고

- 본 프로그램은 뉴스 키워드 기반의 예시 추천 도구입니다.
- 실제 투자 판단은 재무지표, 밸류에이션, 공시, 리스크 요인을 함께 검토해 주세요.
