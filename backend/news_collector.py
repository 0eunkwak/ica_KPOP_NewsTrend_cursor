"""
뉴스 콘텐츠 수집 모듈
네이버 뉴스 API를 사용하여 연예 뉴스를 수집합니다.
"""
import requests
from datetime import datetime, timedelta
try:
    from .utils import is_within_24_hours, format_datetime
    from .config import Config
except ImportError:
    from utils import is_within_24_hours, format_datetime
    from config import Config

class NewsCollector:
    """뉴스 콘텐츠 수집 클래스"""
    
    def __init__(self):
        self.client_id = Config.NAVER_CLIENT_ID
        self.client_secret = Config.NAVER_CLIENT_SECRET
        self.base_url = 'https://openapi.naver.com/v1/search/news.json'
    
    def search(self, keyword, max_results=50):
        """
        키워드로 네이버 뉴스 검색
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 결과 수
        
        Returns:
            list: 검색 결과 리스트
        """
        if not self.client_id or not self.client_secret:
            print("네이버 API 인증 정보가 설정되지 않았습니다.")
            return []
        
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': keyword,
            'display': min(max_results, 100),  # 네이버 API 최대값은 100
            'sort': 'date',
            'start': 1
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                pub_date = item.get('pubDate', '')
                
                # pubDate 파싱 (예: "Mon, 01 Jan 2024 12:00:00 +0900")
                try:
                    # 네이버 API의 날짜 형식 파싱
                    published_at = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    # 파싱 실패 시 현재 시간으로 설정 (필터링됨)
                    published_at = datetime.now() - timedelta(hours=25)
                
                # 24시간 이내 확인
                if is_within_24_hours(published_at):
                    news_data = {
                        'title': item.get('title', '').replace('<b>', '').replace('</b>', ''),
                        'description': item.get('description', '').replace('<b>', '').replace('</b>', ''),
                        'url': item.get('link', ''),
                        'thumbnail': '',  # 네이버 뉴스 API는 썸네일을 제공하지 않음
                        'source': item.get('originallink', ''),
                        'published_at': published_at.isoformat(),
                        'published_at_formatted': format_datetime(published_at),
                        'source_type': 'naver',
                        'type': 'news'
                    }
                    results.append(news_data)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"네이버 뉴스 API 오류: {e}")
            return []
        except Exception as e:
            print(f"뉴스 검색 중 오류 발생: {e}")
            return []
