"""
데이터 수집 통합 모듈
유튜브와 뉴스 수집을 통합하여 관리합니다.
"""
try:
    from .youtube_collector import YouTubeCollector
    from .news_collector import NewsCollector
    from .deduplicator import Deduplicator
    from .config import Config
except ImportError:
    from youtube_collector import YouTubeCollector
    from news_collector import NewsCollector
    from deduplicator import Deduplicator
    from config import Config

class DataCollector:
    """데이터 수집 통합 클래스"""
    
    def __init__(self):
        self.youtube_collector = YouTubeCollector()
        self.news_collector = NewsCollector()
        self.deduplicator = Deduplicator()
    
    def collect_all(self, keyword):
        """
        키워드에 대한 모든 콘텐츠 수집 (유튜브 + 뉴스)
        
        Args:
            keyword: 검색 키워드
        
        Returns:
            dict: 수집된 콘텐츠 딕셔너리
        """
        # 중복 제거기 초기화
        self.deduplicator.clear()
        
        # 유튜브 콘텐츠 수집
        youtube_results = self.youtube_collector.search(
            keyword, 
            max_results=Config.MAX_RESULTS_YOUTUBE
        )
        
        # 뉴스 콘텐츠 수집
        news_results = self.news_collector.search(
            keyword,
            max_results=Config.MAX_RESULTS_NEWS
        )
        
        # 중복 제거
        all_results = youtube_results + news_results
        unique_results = self.deduplicator.remove_duplicates(all_results)
        
        # 날짜순 정렬 (최신순)
        unique_results.sort(
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        
        return {
            'keyword': keyword,
            'total_count': len(unique_results),
            'youtube_count': len(youtube_results),
            'news_count': len(news_results),
            'contents': unique_results
        }
    
    def collect_multiple_keywords(self, keywords):
        """
        여러 키워드에 대한 콘텐츠 수집
        
        Args:
            keywords: 키워드 리스트
        
        Returns:
            dict: 키워드별 수집 결과
        """
        results = {}
        
        for keyword in keywords:
            results[keyword] = self.collect_all(keyword)
        
        return results
