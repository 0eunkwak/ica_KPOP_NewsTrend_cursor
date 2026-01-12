"""
유튜브 콘텐츠 수집 모듈
YouTube Data API를 사용하여 관련 콘텐츠를 수집합니다.
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
try:
    from .utils import is_within_24_hours, format_datetime
    from .config import Config
except ImportError:
    from utils import is_within_24_hours, format_datetime
    from config import Config

class YouTubeCollector:
    """유튜브 콘텐츠 수집 클래스"""
    
    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.youtube = None
        
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                print(f"YouTube API 초기화 실패: {e}")
    
    def search(self, keyword, max_results=50):
        """
        키워드로 유튜브 검색
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 결과 수
        
        Returns:
            list: 검색 결과 리스트
        """
        if not self.youtube:
            print("YouTube API가 초기화되지 않았습니다.")
            return []
        
        try:
            # 24시간 전 시간 계산
            published_after = (datetime.now() - timedelta(hours=24)).isoformat() + 'Z'
            
            # 검색 요청
            request = self.youtube.search().list(
                part='snippet',
                q=keyword,
                type='video',
                maxResults=max_results,
                order='date',
                publishedAfter=published_after,
                regionCode='KR'
            )
            
            response = request.execute()
            
            results = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId', '')
                
                published_at = snippet.get('publishedAt', '')
                
                # 24시간 이내 확인
                if published_at and is_within_24_hours(published_at):
                    video_data = {
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                        'channel': snippet.get('channelTitle', ''),
                        'published_at': published_at,
                        'published_at_formatted': format_datetime(published_at),
                        'source': 'youtube',
                        'type': 'video'
                    }
                    results.append(video_data)
            
            return results
            
        except HttpError as e:
            print(f"YouTube API 오류: {e}")
            return []
        except Exception as e:
            print(f"유튜브 검색 중 오류 발생: {e}")
            return []
