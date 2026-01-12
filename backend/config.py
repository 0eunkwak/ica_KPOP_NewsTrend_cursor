"""
설정 파일
환경 변수와 기본 설정을 관리합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 경로 명시적으로 지정 (프로젝트 루트)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

# .env 파일 로드
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] .env 파일 로드 완료: {env_path}")
else:
    print(f"[WARNING] .env 파일을 찾을 수 없습니다: {env_path}")
    # 현재 디렉토리에서도 시도
    load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # API 키 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '').strip()
    NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '').strip()
    NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '').strip()
    
    @classmethod
    def print_api_status(cls):
        """API 키 로드 상태 출력"""
        print("\n=== API 키 로드 상태 ===")
        print(f"YouTube API Key: {'[OK] 설정됨' if cls.YOUTUBE_API_KEY else '[ERROR] 미설정'}")
        if cls.YOUTUBE_API_KEY:
            print(f"  (길이: {len(cls.YOUTUBE_API_KEY)} 문자, 시작: {cls.YOUTUBE_API_KEY[:10]}...)")
        print(f"Naver Client ID: {'[OK] 설정됨' if cls.NAVER_CLIENT_ID else '[ERROR] 미설정'}")
        if cls.NAVER_CLIENT_ID:
            print(f"  (길이: {len(cls.NAVER_CLIENT_ID)} 문자)")
        print(f"Naver Client Secret: {'[OK] 설정됨' if cls.NAVER_CLIENT_SECRET else '[ERROR] 미설정'}")
        if cls.NAVER_CLIENT_SECRET:
            print(f"  (길이: {len(cls.NAVER_CLIENT_SECRET)} 문자)")
        print("=" * 25 + "\n")
    
    # 서비스 설정
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 15))  # 분 단위
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 수집 설정
    MAX_RESULTS_YOUTUBE = int(os.getenv('MAX_RESULTS_YOUTUBE', 50))
    MAX_RESULTS_NEWS = int(os.getenv('MAX_RESULTS_NEWS', 50))
    
    # 데이터 유효 기간 (시간 단위)
    DATA_VALID_HOURS = 24
    
    # 기본 검색 키워드 (예시)
    DEFAULT_KEYWORDS = ['BTS', 'BLACKPINK', 'NewJeans', 'IVE', 'LE SSERAFIM']
