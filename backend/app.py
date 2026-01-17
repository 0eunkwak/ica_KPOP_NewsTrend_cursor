"""
Flask 백엔드 메인 애플리케이션
API 엔드포인트와 스케줄링을 관리합니다.
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# backend 디렉토리를 sys.path에 추가 (현재 디렉토리에서 실행 시)
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import schedule
import time
import threading

# import 시도 (절대 import 먼저, 실패 시 상대 import)
try:
    from backend.data_collector import DataCollector
    from backend.config import Config
    from backend.utils import generate_content_hash
    from backend.blacklist_store import get_blacklist, add_to_blacklist, remove_from_blacklist
except ImportError:
    from data_collector import DataCollector
    from config import Config
    from utils import generate_content_hash
    from blacklist_store import get_blacklist, add_to_blacklist, remove_from_blacklist

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# 정적 파일 서빙
@app.route('/styles.css')
def styles():
    return send_from_directory('../frontend', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('../frontend', 'script.js')

# API 키 상태 확인
Config.print_api_status()

# 데이터 수집기 인스턴스
collector = DataCollector()

# 캐시된 데이터
cached_data = {}

# 추적 중인 키워드 (기본값은 Config에서 가져옴, 정규화)
try:
    from backend.keyword_mapper import normalize_keyword
except ImportError:
    from keyword_mapper import normalize_keyword

# 기본 키워드를 정규화
tracked_keywords = [normalize_keyword(kw) for kw in Config.DEFAULT_KEYWORDS]

def collect_and_cache(keywords):
    """데이터 수집 및 캐시 업데이트"""
    global cached_data
    print(f"데이터 수집 시작: {keywords}")
    
    try:
        results = collector.collect_multiple_keywords(keywords)
        cached_data = results
        print(f"데이터 수집 완료: 총 {sum(r['total_count'] for r in results.values())}개 콘텐츠")
    except Exception as e:
        print(f"데이터 수집 중 오류: {e}")

def scheduled_update():
    """스케줄된 업데이트 실행"""
    global tracked_keywords
    collect_and_cache(tracked_keywords)

# 스케줄러 설정
schedule.every(Config.UPDATE_INTERVAL).minutes.do(scheduled_update)

def run_scheduler():
    """스케줄러 실행 (별도 스레드)"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

# 스케줄러 스레드 시작
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# 초기 데이터 수집 (별도 스레드에서 실행하여 서버 시작을 블로킹하지 않음)
def initial_data_collection():
    """초기 데이터 수집 (별도 스레드)"""
    global tracked_keywords
    print("초기 데이터 수집 중...")
    try:
        collect_and_cache(tracked_keywords)
    except Exception as e:
        print(f"초기 데이터 수집 실패 (서버는 계속 실행됩니다): {e}")
        print("API 키가 설정되지 않았을 수 있습니다. .env 파일을 확인하세요.")

initial_collection_thread = threading.Thread(target=initial_data_collection, daemon=True)
initial_collection_thread.start()

@app.route('/')
def index():
    """메인 페이지"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/content', methods=['GET'])
def get_content():
    """
    키워드 기반 콘텐츠 조회 API
    
    Query Parameters:
        keyword: 검색 키워드 (선택사항, 없으면 모든 키워드 반환)
    """
    keyword = request.args.get('keyword', '').strip()
    
    print(f"[API] 콘텐츠 조회 요청: keyword='{keyword}'")
    print(f"[API] 캐시된 키워드: {list(cached_data.keys())}")
    
    if keyword:
        # 특정 키워드만 조회
        if keyword in cached_data:
            data = cached_data[keyword]
            print(f"[API] 캐시에서 반환: {keyword}, 콘텐츠 수: {data.get('total_count', 0)}")
            return jsonify(data)
        else:
            # 실시간 수집
            print(f"[API] 실시간 수집 시작: {keyword}")
            result = collector.collect_all(keyword)
            cached_data[keyword] = result
            print(f"[API] 실시간 수집 완료: {keyword}, 콘텐츠 수: {result.get('total_count', 0)}")
            return jsonify(result)
    else:
        # 모든 키워드 반환
        print(f"[API] 모든 키워드 반환: {len(cached_data)}개 키워드")
        return jsonify(cached_data)

@app.route('/api/status', methods=['GET'])
def get_status():
    """서비스 상태 확인 API"""
    total_contents = sum(r['total_count'] for r in cached_data.values())
    
    return jsonify({
        'status': 'running',
        'update_interval_minutes': Config.UPDATE_INTERVAL,
        'cached_keywords': list(cached_data.keys()),
        'total_cached_contents': total_contents,
        'last_update': time.time(),
        'api_keys': {
            'youtube': 'configured' if Config.YOUTUBE_API_KEY else 'missing',
            'naver_id': 'configured' if Config.NAVER_CLIENT_ID else 'missing',
            'naver_secret': 'configured' if Config.NAVER_CLIENT_SECRET else 'missing'
        }
    })

@app.route('/api/admin/blacklist', methods=['GET'])
def get_blacklist_api():
    """관리자용 블랙리스트 조회 API"""
    return jsonify(get_blacklist())

@app.route('/api/admin/block', methods=['POST'])
def block_content():
    """관리자용 콘텐츠 차단 API"""
    data = request.json or {}
    content_id = data.get('content_id')
    url = data.get('url')
    title = data.get('title', '')

    if not content_id and (title or url):
        content_id = generate_content_hash(title, url or '')

    if not content_id and not url:
        return jsonify({'error': 'content_id 또는 url이 필요합니다'}), 400

    updated = add_to_blacklist(content_id=content_id, url=url)
    return jsonify({
        'message': '블랙리스트에 추가되었습니다',
        'content_id': content_id,
        'url': url,
        'blacklist': updated
    })

@app.route('/api/admin/unblock', methods=['POST'])
def unblock_content():
    """관리자용 콘텐츠 차단 해제 API"""
    data = request.json or {}
    content_id = data.get('content_id')
    url = data.get('url')

    if not content_id and not url:
        return jsonify({'error': 'content_id 또는 url이 필요합니다'}), 400

    updated = remove_from_blacklist(content_id=content_id, url=url)
    return jsonify({
        'message': '블랙리스트에서 제거되었습니다',
        'content_id': content_id,
        'url': url,
        'blacklist': updated
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """수동 데이터 갱신 API"""
    global tracked_keywords
    
    request_data = request.json or {}
    keywords = request_data.get('keywords', [])
    
    print(f"[API] 데이터 갱신 요청: keywords={keywords}")
    
    if keywords:
        # 키워드 정규화
        try:
            from backend.keyword_mapper import normalize_keyword
        except ImportError:
            from keyword_mapper import normalize_keyword
        
        normalized_keywords = []
        for kw in keywords:
            if isinstance(kw, dict) and 'en' in kw:
                normalized_keywords.append(kw)
            else:
                normalized = normalize_keyword(str(kw))
                normalized_keywords.append(normalized)
        
        tracked_keywords = normalized_keywords
        print(f"[API] 추적 키워드 업데이트: {tracked_keywords}")
        keywords = normalized_keywords
    else:
        keywords = tracked_keywords
        print(f"[API] 기존 추적 키워드 사용: {keywords}")
    
    # 데이터 수집 (별도 스레드에서 실행하여 응답 지연 방지)
    def collect_in_background():
        print(f"[API] 백그라운드 데이터 수집 시작: {keywords}")
        collect_and_cache(keywords)
        print(f"[API] 백그라운드 데이터 수집 완료")
    
    collection_thread = threading.Thread(target=collect_in_background, daemon=True)
    collection_thread.start()
    
    return jsonify({
        'message': '데이터 갱신 시작됨', 
        'keywords': keywords,
        'status': 'collecting'
    })

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    """키워드 관리 API"""
    global tracked_keywords
    
    if request.method == 'GET':
        print(f"[API] 키워드 조회 요청: {tracked_keywords}")
        return jsonify({'keywords': tracked_keywords})
    
    elif request.method == 'POST':
        data = request.json
        print(f"[API] 키워드 업데이트 요청: {data}")
        
        if 'keywords' in data:
            old_keywords = tracked_keywords.copy()
            # 키워드를 정규화 (문자열 또는 객체 모두 처리)
            try:
                from backend.keyword_mapper import normalize_keyword
            except ImportError:
                from keyword_mapper import normalize_keyword
            
            normalized_keywords = []
            for kw in data['keywords']:
                if isinstance(kw, dict) and 'en' in kw:
                    normalized_keywords.append(kw)
                else:
                    normalized = normalize_keyword(str(kw))
                    normalized_keywords.append(normalized)
            
            tracked_keywords = normalized_keywords
            print(f"[API] 키워드 업데이트: {old_keywords} -> {tracked_keywords}")
            
            # 키워드 변경 시 데이터 수집 (별도 스레드에서 실행하여 응답 지연 방지)
            def collect_in_background():
                print(f"[API] 백그라운드 데이터 수집 시작: {tracked_keywords}")
                collect_and_cache(tracked_keywords)
                print(f"[API] 백그라운드 데이터 수집 완료")
            
            collection_thread = threading.Thread(target=collect_in_background, daemon=True)
            collection_thread.start()
            
            return jsonify({
                'message': '키워드 업데이트 완료', 
                'keywords': tracked_keywords,
                'status': 'collecting'
            })
        else:
            return jsonify({'error': 'keywords 필드가 필요합니다'}), 400

if __name__ == '__main__':
    try:
        print(f"\n서버 시작: http://localhost:{Config.PORT}")
        print(f"자동 갱신 주기: {Config.UPDATE_INTERVAL}분")
        print("서버가 시작되었습니다. 브라우저에서 http://localhost:5000 에 접속하세요.\n")
        app.run(host='127.0.0.1', port=Config.PORT, debug=Config.DEBUG, use_reloader=False)
    except Exception as e:
        print(f"\n[ERROR] 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
