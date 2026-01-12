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
    
    def collect_all(self, keyword_obj):
        """
        키워드에 대한 모든 콘텐츠 수집 (유튜브 + 뉴스)
        영문과 한글 키워드를 모두 검색합니다.
        
        Args:
            keyword_obj: 키워드 객체 (문자열 또는 {en, ko} 딕셔너리)
        
        Returns:
            dict: 수집된 콘텐츠 딕셔너리
        """
        # 키워드 정규화
        try:
            from .keyword_mapper import normalize_keyword
        except ImportError:
            from keyword_mapper import normalize_keyword
        
        if isinstance(keyword_obj, dict):
            keyword_en = keyword_obj.get('en', '')
            keyword_ko = keyword_obj.get('ko', '')
            keyword_display = keyword_en or keyword_ko
        else:
            # 문자열인 경우 정규화
            normalized = normalize_keyword(keyword_obj)
            keyword_en = normalized['en']
            keyword_ko = normalized['ko']
            keyword_display = keyword_en
        
        print(f"[COLLECT] 키워드 검색: 영문='{keyword_en}', 한글='{keyword_ko}'")
        
        # 중복 제거기 초기화
        self.deduplicator.clear()
        
        # 유튜브 콘텐츠 수집 (영문과 한글 모두 검색)
        youtube_results = []
        if keyword_en:
            youtube_results.extend(self.youtube_collector.search(
                keyword_en, 
                max_results=Config.MAX_RESULTS_YOUTUBE
            ))
        if keyword_ko and keyword_ko != keyword_en:
            youtube_results.extend(self.youtube_collector.search(
                keyword_ko,
                max_results=Config.MAX_RESULTS_YOUTUBE
            ))
        
        # 뉴스 콘텐츠 수집 (영문과 한글 모두 검색)
        news_results = []
        if keyword_en:
            news_results.extend(self.news_collector.search(
                keyword_en,
                max_results=Config.MAX_RESULTS_NEWS
            ))
        if keyword_ko and keyword_ko != keyword_en:
            news_results.extend(self.news_collector.search(
                keyword_ko,
                max_results=Config.MAX_RESULTS_NEWS
            ))
        
        # 중복 제거
        all_results = youtube_results + news_results
        unique_results = self.deduplicator.remove_duplicates(all_results)
        
        # 각 콘텐츠에 키워드 정보 추가
        for result in unique_results:
            result['keyword_en'] = keyword_en
            result['keyword_ko'] = keyword_ko
            result['keyword_display'] = keyword_display
        
        # 날짜순 정렬 (최신순)
        unique_results.sort(
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        
        return {
            'keyword': keyword_display,
            'keyword_en': keyword_en,
            'keyword_ko': keyword_ko,
            'total_count': len(unique_results),
            'youtube_count': len(youtube_results),
            'news_count': len(news_results),
            'contents': unique_results
        }
    
    def collect_multiple_keywords(self, keywords):
        """
        여러 키워드에 대한 콘텐츠 수집
        
        Args:
            keywords: 키워드 리스트 (문자열 또는 {en, ko} 딕셔너리)
        
        Returns:
            dict: 키워드별 수집 결과
        """
        results = {}
        
        for keyword in keywords:
            result = self.collect_all(keyword)
            # 키워드 표시명을 키로 사용
            key = result.get('keyword_display', result.get('keyword', str(keyword)))
            results[key] = result
        
        return results
