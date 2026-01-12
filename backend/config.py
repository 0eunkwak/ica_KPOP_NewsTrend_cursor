"""
설정 파일
환경 변수와 기본 설정을 관리합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # API 키 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '')
    NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '')
    
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
