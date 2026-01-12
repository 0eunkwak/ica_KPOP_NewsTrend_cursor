"""
키워드 매핑 모듈
영문 키워드를 한국어로 매핑합니다.
"""
KEYWORD_MAP = {
    'BTS': '방탄소년단',
    'BLACKPINK': '블랙핑크',
    'BLACK PINK': '블랙핑크',
    'NewJeans': '뉴진스',
    'NEW JEANS': '뉴진스',
    'IVE': '아이브',
    'LE SSERAFIM': '르세라핌',
    'LE SERAFIM': '르세라핌',
    'LESSERAFIM': '르세라핌',
    'aespa': '에스파',
    'AESPA': '에스파',
    'ITZY': '있지',
    'TWICE': '트와이스',
    'Red Velvet': '레드벨벳',
    'RED VELVET': '레드벨벳',
    'Girls Generation': '소녀시대',
    'SNSD': '소녀시대',
    'EXO': '엑소',
    'NCT': '엔시티',
    'Stray Kids': '스트레이 키즈',
    'STRAY KIDS': '스트레이 키즈',
    'SEVENTEEN': '세븐틴',
    'GOT7': '갓세븐',
    'MAMAMOO': '마마무',
    'IU': '아이유',
    'TAEYEON': '태연',
    'Jennie': '제니',
    'JENNIE': '제니',
    'Jisoo': '지수',
    'JISOO': '지수',
    'Rose': '로제',
    'ROSE': '로제',
    'Lisa': '리사',
    'LISA': '리사',
}

def get_korean_keyword(keyword):
    """
    영문 키워드를 한국어로 변환
    
    Args:
        keyword: 영문 키워드
    
    Returns:
        str: 한국어 키워드 (매핑이 없으면 원본 반환)
    """
    # 대소문자 무시하고 매핑
    keyword_upper = keyword.upper().strip()
    
    # 정확한 매칭
    if keyword_upper in KEYWORD_MAP:
        return KEYWORD_MAP[keyword_upper]
    
    # 부분 매칭 시도
    for en_key, ko_key in KEYWORD_MAP.items():
        if en_key.upper() in keyword_upper or keyword_upper in en_key.upper():
            return ko_key
    
    # 매핑이 없으면 원본 반환
    return keyword

def normalize_keyword(keyword):
    """
    키워드를 정규화하고 영문/한글 쌍 반환
    
    Args:
        keyword: 입력 키워드 (영문 또는 한글)
    
    Returns:
        dict: {en: 영문키워드, ko: 한글키워드}
    """
    keyword = keyword.strip()
    
    # 한글이 포함되어 있는지 확인
    has_korean = any('\uAC00' <= char <= '\uD7A3' for char in keyword)
    
    if has_korean:
        # 한글 키워드인 경우, 역매핑 시도
        ko_keyword = keyword
        # 역매핑 (한글 -> 영문)
        en_keyword = None
        for en_key, ko_value in KEYWORD_MAP.items():
            if ko_value == keyword:
                en_keyword = en_key
                break
        
        if not en_keyword:
            # 역매핑이 없으면 영문도 한글과 동일하게 설정
            en_keyword = keyword
        
        return {'en': en_keyword, 'ko': ko_keyword}
    else:
        # 영문 키워드인 경우
        en_keyword = keyword
        ko_keyword = get_korean_keyword(keyword)
        return {'en': en_keyword, 'ko': ko_keyword}
