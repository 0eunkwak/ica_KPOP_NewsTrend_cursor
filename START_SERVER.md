# 서버 실행 방법

## 방법 1: 배치 파일 사용 (권장)

프로젝트 루트 디렉토리에서 `run_server.bat` 파일을 더블클릭하거나 명령 프롬프트에서 실행:

```bash
run_server.bat
```

## 방법 2: 수동 실행

1. 명령 프롬프트(CMD) 또는 PowerShell 열기
2. 프로젝트 디렉토리로 이동:
   ```bash
   cd "C:\Users\YG PLUS\Documents\GitHub\ica_KPOP_NewsTrend_cursor\backend"
   ```
3. 서버 실행:
   ```bash
   python app.py
   ```

## 서버 확인

서버가 정상적으로 시작되면 다음과 같은 메시지가 표시됩니다:

```
[OK] .env 파일 로드 완료: ...

=== API 키 로드 상태 ===
YouTube API Key: [OK] 설정됨
Naver Client ID: [OK] 설정됨
Naver Client Secret: [OK] 설정됨
===================

서버 시작: http://localhost:5000
자동 갱신 주기: 15분
서버가 시작되었습니다. 브라우저에서 http://localhost:5000 에 접속하세요.
```

## 브라우저 접속

서버가 시작된 후 브라우저에서 다음 주소로 접속:
**http://localhost:5000**

## 문제 해결

### 포트 5000이 이미 사용 중인 경우

다른 프로그램이 포트 5000을 사용하고 있을 수 있습니다. 다음 명령으로 확인:

```bash
netstat -ano | findstr :5000
```

포트를 변경하려면 `.env` 파일에 다음을 추가:
```
PORT=5001
```

### 서버가 시작되지 않는 경우

1. Python이 설치되어 있는지 확인:
   ```bash
   python --version
   ```

2. 필요한 패키지가 설치되어 있는지 확인:
   ```bash
   pip install -r requirements.txt
   ```

3. 오류 메시지를 확인하고 문제를 해결하세요.
