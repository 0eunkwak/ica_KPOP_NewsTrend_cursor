"""
유틸리티 함수 모듈
공통으로 사용되는 유틸리티 함수들을 정의합니다.
"""
from datetime import datetime, timedelta
import hashlib

def is_within_24_hours(published_time):
    """
    게시 시간이 최근 24시간 이내인지 확인
    
    Args:
        published_time: 게시 시간 (datetime 객체 또는 ISO 형식 문자열)
    
    Returns:
        bool: 24시간 이내면 True, 아니면 False
    """
    if isinstance(published_time, str):
        try:
            # ISO 형식 문자열 파싱
            published_time = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
        except:
            # 다른 형식 시도
            try:
                published_time = datetime.strptime(published_time, '%Y-%m-%dT%H:%M:%S')
            except:
                return False
    
    now = datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
    time_diff = now - published_time
    
    return time_diff <= timedelta(hours=24)

def generate_content_hash(title, url):
    """
    콘텐츠의 고유 해시값 생성 (중복 검사용)
    
    Args:
        title: 콘텐츠 제목
        url: 콘텐츠 URL
    
    Returns:
        str: 해시값
    """
    content_string = f"{title}|{url}"
    return hashlib.md5(content_string.encode('utf-8')).hexdigest()

def format_datetime(dt):
    """
    datetime 객체를 사용자 친화적인 형식으로 변환
    
    Args:
        dt: datetime 객체
    
    Returns:
        str: 포맷된 날짜 문자열
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"
