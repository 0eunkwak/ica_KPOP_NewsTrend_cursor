"""
중복 제거 모듈
수집된 콘텐츠에서 중복을 제거합니다.
"""
try:
    from .utils import generate_content_hash
except ImportError:
    from utils import generate_content_hash

class Deduplicator:
    """중복 제거 클래스"""
    
    def __init__(self):
        self.seen_hashes = set()
    
    def is_duplicate(self, title, url):
        """
        콘텐츠가 중복인지 확인
        
        Args:
            title: 콘텐츠 제목
            url: 콘텐츠 URL
        
        Returns:
            bool: 중복이면 True, 아니면 False
        """
        content_hash = generate_content_hash(title, url)
        
        if content_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(content_hash)
        return False
    
    def remove_duplicates(self, contents):
        """
        콘텐츠 리스트에서 중복 제거
        
        Args:
            contents: 콘텐츠 리스트 (각 항목은 title과 url 키를 가져야 함)
        
        Returns:
            list: 중복이 제거된 콘텐츠 리스트
        """
        unique_contents = []
        
        for content in contents:
            if not self.is_duplicate(content.get('title', ''), content.get('url', '')):
                unique_contents.append(content)
        
        return unique_contents
    
    def clear(self):
        """저장된 해시값 초기화"""
        self.seen_hashes.clear()
