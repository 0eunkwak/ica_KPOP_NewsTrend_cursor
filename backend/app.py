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
except ImportError:
    from data_collector import DataCollector
    from config import Config

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# 정적 파일 서빙
@app.route('/styles.css')
def styles():
    return send_from_directory('../frontend', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('../frontend', 'script.js')

# 데이터 수집기 인스턴스
collector = DataCollector()

# 캐시된 데이터
cached_data = {}

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
    keywords = Config.DEFAULT_KEYWORDS
    collect_and_cache(keywords)

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
    print("초기 데이터 수집 중...")
    try:
        collect_and_cache(Config.DEFAULT_KEYWORDS)
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
    
    if keyword:
        # 특정 키워드만 조회
        if keyword in cached_data:
            return jsonify(cached_data[keyword])
        else:
            # 실시간 수집
            result = collector.collect_all(keyword)
            return jsonify(result)
    else:
        # 모든 키워드 반환
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
        'last_update': time.time()
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """수동 데이터 갱신 API"""
    keywords = request.json.get('keywords', Config.DEFAULT_KEYWORDS) if request.json else Config.DEFAULT_KEYWORDS
    collect_and_cache(keywords)
    return jsonify({'message': '데이터 갱신 완료', 'keywords': keywords})

if __name__ == '__main__':
    print(f"서버 시작: http://localhost:{Config.PORT}")
    print(f"자동 갱신 주기: {Config.UPDATE_INTERVAL}분")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
