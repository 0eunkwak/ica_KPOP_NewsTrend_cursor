# K-POP 뉴스 트렌드 수집 서비스

K-POP 아티스트 키워드 기반으로 유튜브 콘텐츠와 연예 뉴스(네이버 포함)를 수집하여 한 화면에 모아 보여주는 서비스입니다.

## 주요 기능

- 🎵 K-POP 아티스트 키워드 기반 콘텐츠 수집
- 📺 유튜브 콘텐츠 수집
- 📰 네이버 연예 뉴스 수집
- ⏰ 최근 24시간 이내 데이터만 표시
- 🔄 10~30분 주기 자동 갱신
- 🚫 중복 기사/영상 자동 제거

## 프로젝트 구조

```
ica_KPOP_NewsTrend_cursor/
├── backend/
│   ├── app.py                 # Flask 백엔드 메인
│   ├── config.py              # 설정 파일
│   ├── data_collector.py      # 데이터 수집 통합 모듈
│   ├── youtube_collector.py   # 유튜브 수집 모듈
│   ├── news_collector.py      # 뉴스 수집 모듈
│   ├── deduplicator.py        # 중복 제거 모듈
│   └── utils.py               # 유틸리티 함수
├── frontend/
│   ├── index.html             # 메인 HTML
│   ├── styles.css             # 스타일시트
│   └── script.js              # 프론트엔드 로직
├── .env.example               # 환경 변수 예시
├── .gitignore                 # Git 제외 파일
├── requirements.txt           # Python 의존성
└── README.md                  # 프로젝트 설명
```

## 설치 방법

1. 저장소 클론
```bash
git clone <repository-url>
cd ica_KPOP_NewsTrend_cursor
```

2. Python 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 API 키 등을 설정
```

## 실행 방법

1. 백엔드 서버 실행
```bash
cd backend
python app.py
```

2. 브라우저에서 `http://localhost:5000` 접속

## 환경 변수

- `YOUTUBE_API_KEY`: YouTube Data API 키
- `NAVER_CLIENT_ID`: 네이버 API 클라이언트 ID
- `NAVER_CLIENT_SECRET`: 네이버 API 클라이언트 시크릿
- `UPDATE_INTERVAL`: 자동 갱신 주기 (분 단위, 기본값: 15)

## API 엔드포인트

- `GET /api/content?keyword={키워드}`: 키워드 기반 콘텐츠 조회
- `GET /api/status`: 서비스 상태 확인

## 개발 참고사항

- 소스 추가/변경 시에도 유지보수가 쉬운 구조로 설계됨
- 모듈화된 구조로 각 기능이 독립적으로 관리됨
- 설정은 config.py와 환경 변수를 통해 중앙 관리
