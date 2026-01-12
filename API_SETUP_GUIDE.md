# API 키 설정 가이드

## .env 파일 설정 방법

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 형식으로 API 키를 입력하세요:

```env
# YouTube API 설정
YOUTUBE_API_KEY=your_youtube_api_key_here

# 네이버 API 설정
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

# 서비스 설정 (선택사항)
UPDATE_INTERVAL=15
PORT=5000
DEBUG=True

# 수집 설정 (선택사항)
MAX_RESULTS_YOUTUBE=50
MAX_RESULTS_NEWS=50
```

## API 키 발급 방법

### YouTube Data API 키 발급

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "라이브러리"로 이동
4. "YouTube Data API v3" 검색 후 활성화
5. "사용자 인증 정보" > "사용자 인증 정보 만들기" > "API 키" 선택
6. 생성된 API 키를 `.env` 파일의 `YOUTUBE_API_KEY`에 입력

### 네이버 검색 API 키 발급

1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. "Application" > "애플리케이션 등록"
3. 애플리케이션 정보 입력:
   - 애플리케이션 이름 입력
   - 사용 API: "검색" 선택
   - 비로그인 오픈 API 서비스 환경: "WEB 설정" 선택
4. 등록 후 Client ID와 Client Secret 확인
5. `.env` 파일에 입력:
   - `NAVER_CLIENT_ID`: Client ID
   - `NAVER_CLIENT_SECRET`: Client Secret

## 문제 해결

### 1. API 키가 로드되지 않는 경우

**확인 사항:**
- `.env` 파일이 프로젝트 루트에 있는지 확인
- 파일 이름이 정확히 `.env`인지 확인 (`.env.txt` 아님)
- 환경 변수 이름이 정확한지 확인 (대소문자 구분)
- 값에 따옴표나 공백이 없는지 확인

**해결 방법:**
```env
# ❌ 잘못된 예
YOUTUBE_API_KEY="AIzaSy..."
YOUTUBE_API_KEY= AIzaSy...  # 앞뒤 공백

# ✅ 올바른 예
YOUTUBE_API_KEY=AIzaSy...
```

### 2. 서버 시작 시 API 키 상태 확인

서버를 시작하면 콘솔에 다음과 같은 메시지가 표시됩니다:

```
=== API 키 로드 상태 ===
YouTube API Key: ✅ 설정됨
  (길이: 39 문자, 시작: AIzaSyCIUL...)
Naver Client ID: ✅ 설정됨
  (길이: 20 문자)
Naver Client Secret: ✅ 설정됨
  (길이: 20 문자)
===================
```

### 3. API 호출 오류 확인

서버 로그에서 다음 메시지를 확인하세요:

- `✅ YouTube API 초기화 성공`: YouTube API 정상
- `✅ 네이버 API 초기화 성공`: 네이버 API 정상
- `❌ YouTube API 키가 설정되지 않았습니다`: API 키 미설정
- `❌ 네이버 API 인증 정보가 설정되지 않았습니다`: 네이버 API 키 미설정

### 4. API 사용량 제한

**YouTube Data API:**
- 일일 할당량: 기본 10,000 units
- 검색 요청: 100 units/요청
- 일일 약 100회 검색 가능

**네이버 검색 API:**
- 일일 할당량: 25,000건
- 검색 요청: 1건/요청

### 5. CORS 오류

백엔드에서 `flask-cors`가 설치되어 있고 `CORS(app)`이 설정되어 있는지 확인하세요.

## 테스트 방법

1. 서버 시작 후 콘솔에서 API 키 로드 상태 확인
2. 브라우저에서 `http://localhost:5000/api/status` 접속하여 API 키 상태 확인
3. 키워드 추가 후 데이터 수집 로그 확인

## 디버깅 팁

1. **서버 콘솔 로그 확인**: API 호출 시 상세한 로그가 출력됩니다
2. **브라우저 개발자 도구**: Network 탭에서 API 요청/응답 확인
3. **API 상태 엔드포인트**: `/api/status`에서 API 키 설정 상태 확인
