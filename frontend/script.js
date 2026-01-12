// 전역 변수
let currentKeyword = '';
let allData = {};
let currentFilter = 'all';
let autoRefreshInterval = null;
let trackedKeywords = [];
let currentPage = 'dashboard'; // 'dashboard' or 'keywords'

// DOM 요소
const sidebar = document.getElementById('sidebar');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileOverlay = document.getElementById('mobile-overlay');
const themeToggle = document.getElementById('theme-toggle');
const themeToggleKeywords = document.getElementById('theme-toggle-keywords');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');
const refreshBtn = document.getElementById('refreshBtn');
const contents = document.getElementById('contents');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const artistSelect = document.getElementById('artist-select');
const filterTabs = document.querySelectorAll('.filter-tab');
const dashboardContent = document.getElementById('dashboard-content');
const keywordsContent = document.getElementById('keywords-content');
const dashboardHeader = document.getElementById('dashboard-header');
const keywordsHeader = document.getElementById('keywords-header');
const addKeywordBtn = document.getElementById('add-keyword-btn');
const addKeywordForm = document.getElementById('add-keyword-form');
const keywordInput = document.getElementById('keyword-input');
const submitKeywordBtn = document.getElementById('submit-keyword-btn');
const cancelKeywordBtn = document.getElementById('cancel-keyword-btn');
const keywordsList = document.getElementById('keywords-list');
const keywordsEmpty = document.getElementById('keywords-empty');
const keywordError = document.getElementById('keyword-error');

// 초기화
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[INIT] 애플리케이션 초기화 시작');
    initDarkMode();
    loadKeywords();
    setupEventListeners();
    showPage('dashboard');
    
    // 키워드가 있으면 자동으로 데이터 로드
    if (trackedKeywords.length > 0) {
        console.log('[INIT] 저장된 키워드로 데이터 로드:', trackedKeywords);
        await loadAllContent(false);
    } else {
        console.log('[INIT] 저장된 키워드 없음, 기본 키워드로 데이터 로드');
        await loadAllContent(false);
    }
    
    startAutoRefresh();
    console.log('[INIT] 애플리케이션 초기화 완료');
});

// 다크모드 초기화
function initDarkMode() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    updateThemeIcons();
}

// 다크모드 토글
function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcons();
}

// 테마 아이콘 업데이트
function updateThemeIcons() {
    const isDark = document.documentElement.classList.contains('dark');
    sunIcon.classList.toggle('hidden', !isDark);
    sunIcon.classList.toggle('block', isDark);
    moonIcon.classList.toggle('hidden', isDark);
    moonIcon.classList.toggle('block', !isDark);
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 다크모드 토글
    themeToggle.addEventListener('click', toggleDarkMode);
    
    // 모바일 메뉴
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('-translate-x-full');
        mobileOverlay.classList.toggle('hidden');
    });
    
    mobileOverlay.addEventListener('click', () => {
        sidebar.classList.add('-translate-x-full');
        mobileOverlay.classList.add('hidden');
    });
    
    // 새로고침 버튼
    refreshBtn.addEventListener('click', handleRefresh);
    
    // 필터 탭
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentFilter = tab.dataset.filter;
            filterContent();
        });
    });
    
    // 메뉴 아이템
    document.getElementById('menu-dashboard').addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
        document.getElementById('menu-dashboard').classList.add('active');
        showPage('dashboard');
    });
    
    document.getElementById('menu-keywords').addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
        document.getElementById('menu-keywords').classList.add('active');
        showPage('keywords');
    });

    // 키워드 추가 관련
    addKeywordBtn.addEventListener('click', () => {
        addKeywordForm.classList.remove('hidden');
        keywordInput.focus();
    });

    cancelKeywordBtn.addEventListener('click', () => {
        addKeywordForm.classList.add('hidden');
        keywordInput.value = '';
        keywordError.classList.add('hidden');
    });

    submitKeywordBtn.addEventListener('click', handleAddKeyword);
    keywordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleAddKeyword();
        }
    });

    // Keywords 페이지의 다크모드 토글
    if (themeToggleKeywords) {
        themeToggleKeywords.addEventListener('click', toggleDarkMode);
    }
}

// 페이지 전환
function showPage(page) {
    currentPage = page;
    
    if (page === 'dashboard') {
        dashboardContent.classList.remove('hidden');
        keywordsContent.classList.add('hidden');
        dashboardHeader.classList.remove('hidden');
        keywordsHeader.classList.add('hidden');
    } else if (page === 'keywords') {
        dashboardContent.classList.add('hidden');
        keywordsContent.classList.remove('hidden');
        dashboardHeader.classList.add('hidden');
        keywordsHeader.classList.remove('hidden');
        renderKeywordsList();
    }
}

// 키워드 로드 (localStorage)
function loadKeywords() {
    const saved = localStorage.getItem('trackedKeywords');
    if (saved) {
        trackedKeywords = JSON.parse(saved);
    } else {
        // 기본 키워드
        trackedKeywords = ['BTS', 'BLACKPINK', 'NewJeans', 'IVE', 'LE SSERAFIM'];
        saveKeywords();
    }
}

// 키워드 저장 (localStorage)
function saveKeywords() {
    localStorage.setItem('trackedKeywords', JSON.stringify(trackedKeywords));
    // 백엔드에 키워드 동기화
    syncKeywordsToBackend();
}

// 키워드 추가 처리
async function handleAddKeyword() {
    console.log('[KEYWORD] 키워드 추가 시작');
    const keyword = keywordInput.value.trim();
    
    if (!keyword) {
        console.warn('[KEYWORD] 빈 키워드 입력');
        showKeywordError('Please enter a keyword');
        return;
    }
    
    if (trackedKeywords.includes(keyword)) {
        console.warn('[KEYWORD] 중복 키워드:', keyword);
        showKeywordError('This keyword is already added');
        return;
    }
    
    console.log('[KEYWORD] 새 키워드 추가:', keyword);
    
    // 키워드 추가
    trackedKeywords.push(keyword);
    saveKeywords();
    
    // 폼 초기화
    keywordInput.value = '';
    addKeywordForm.classList.add('hidden');
    keywordError.classList.add('hidden');
    
    // 목록 업데이트
    renderKeywordsList();
    
    console.log('[KEYWORD] 키워드 목록 업데이트 완료:', trackedKeywords);
    
    // 백엔드 동기화 및 데이터 수집
    console.log('[KEYWORD] 백엔드 동기화 시작...');
    try {
        await syncKeywordsToBackend();
        console.log('[KEYWORD] 백엔드 동기화 완료');
        
        // Dashboard로 전환하고 데이터 로드
        console.log('[KEYWORD] Dashboard로 전환 및 데이터 로드 시작...');
        showPage('dashboard');
        await loadAllContent(true); // 강제 새로고침
        console.log('[KEYWORD] 데이터 로드 완료');
    } catch (error) {
        console.error('[KEYWORD] 키워드 추가 후 데이터 로드 실패:', error);
        showError(`키워드는 추가되었지만 데이터를 불러오는데 실패했습니다: ${error.message}`);
    }
}

// 키워드 삭제 처리
function handleDeleteKeyword(keyword) {
    if (confirm(`Are you sure you want to remove "${keyword}"?`)) {
        trackedKeywords = trackedKeywords.filter(k => k !== keyword);
        saveKeywords();
        renderKeywordsList();
        
        // Dashboard로 전환
        if (currentPage === 'keywords' && trackedKeywords.length === 0) {
            showPage('dashboard');
        }
    }
}

// 키워드 목록 렌더링
function renderKeywordsList() {
    keywordsList.innerHTML = '';
    
    if (trackedKeywords.length === 0) {
        keywordsEmpty.classList.remove('hidden');
        keywordsList.parentElement.classList.add('hidden');
    } else {
        keywordsEmpty.classList.add('hidden');
        keywordsList.parentElement.classList.remove('hidden');
        
        trackedKeywords.forEach(keyword => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 dark:hover:bg-dark-sidebar transition-colors';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100">${escapeHtml(keyword)}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        Active
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                        onclick="handleDeleteKeyword('${escapeHtml(keyword)}')" 
                        class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 transition-colors"
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </td>
            `;
            
            keywordsList.appendChild(row);
        });
    }
}

// 키워드 오류 표시
function showKeywordError(message) {
    keywordError.textContent = message;
    keywordError.classList.remove('hidden');
}

// 백엔드에 키워드 동기화
async function syncKeywordsToBackend() {
    console.log('[SYNC] 백엔드 키워드 동기화 시작:', trackedKeywords);
    
    try {
        // 1. 키워드 업데이트
        console.log('[SYNC] 1단계: 키워드 업데이트 API 호출');
        const keywordsResponse = await fetch('/api/keywords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keywords: trackedKeywords })
        });
        
        if (!keywordsResponse.ok) {
            throw new Error(`키워드 업데이트 실패: ${keywordsResponse.status}`);
        }
        
        const keywordsData = await keywordsResponse.json();
        console.log('[SYNC] 키워드 업데이트 응답:', keywordsData);
        
        // 2. 데이터 수집 트리거
        if (trackedKeywords.length > 0) {
            console.log('[SYNC] 2단계: 데이터 수집 API 호출');
            const refreshResponse = await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords: trackedKeywords })
            });
            
            if (!refreshResponse.ok) {
                throw new Error(`데이터 수집 실패: ${refreshResponse.status}`);
            }
            
            const refreshData = await refreshResponse.json();
            console.log('[SYNC] 데이터 수집 응답:', refreshData);
            
            // 수집이 완료될 때까지 잠시 대기 (백엔드에서 비동기로 처리되므로)
            console.log('[SYNC] 데이터 수집 완료 대기 중...');
            await new Promise(resolve => setTimeout(resolve, 2000)); // 2초 대기
        }
        
        console.log('[SYNC] 백엔드 동기화 완료');
    } catch (error) {
        console.error('[SYNC] 키워드 동기화 오류:', error);
        throw error; // 상위로 에러 전파
    }
}

// 새로고침 처리
function handleRefresh() {
    if (currentKeyword) {
        loadContent(currentKeyword, true);
    } else {
        loadAllContent(true);
    }
}

// 모든 콘텐츠 로드
async function loadAllContent(forceRefresh = false) {
    console.log('[LOAD] 모든 콘텐츠 로드 시작, forceRefresh:', forceRefresh);
    showLoading();
    
    try {
        // trackedKeywords 사용
        const keywordsToLoad = trackedKeywords.length > 0 ? trackedKeywords : ['BTS', 'BLACKPINK'];
        console.log('[LOAD] 로드할 키워드:', keywordsToLoad);
        
        let response;
        if (forceRefresh) {
            console.log('[LOAD] 강제 새로고침 모드: /api/refresh 호출');
            response = await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords: keywordsToLoad })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const refreshData = await response.json();
            console.log('[LOAD] 새로고침 응답:', refreshData);
            
            // 수집 완료 대기
            console.log('[LOAD] 데이터 수집 완료 대기 중...');
            await new Promise(resolve => setTimeout(resolve, 3000)); // 3초 대기
            
            // 수집된 데이터 가져오기
            console.log('[LOAD] 수집된 데이터 가져오기: /api/content 호출');
            response = await fetch('/api/content');
        } else {
            console.log('[LOAD] 일반 모드: /api/content 호출');
            response = await fetch('/api/content');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('[LOAD] 받은 데이터:', {
            키워드수: Object.keys(data).length,
            키워드목록: Object.keys(data),
            총콘텐츠수: Object.values(data).reduce((sum, d) => sum + (d.total_count || 0), 0)
        });
        
        allData = data;
        
        // 아티스트 선택 옵션 업데이트
        updateArtistSelect(Object.keys(data));
        
        // 첫 번째 키워드 선택
        if (Object.keys(data).length > 0) {
            currentKeyword = Object.keys(data)[0];
            console.log('[LOAD] 첫 번째 키워드 선택:', currentKeyword);
            displayContent(data[currentKeyword]);
        } else {
            console.warn('[LOAD] 수집된 데이터가 없습니다.');
            showEmpty();
            console.warn('⚠️ 수집된 데이터가 없습니다. API 키를 확인하세요.');
        }
    } catch (error) {
        console.error('[LOAD] 데이터 로드 오류:', error);
        showError(`데이터를 불러올 수 없습니다: ${error.message}`);
        showEmpty();
    } finally {
        hideLoading();
    }
}

// 특정 키워드 콘텐츠 로드
async function loadContent(keyword, forceRefresh = false) {
    console.log('[LOAD] 특정 키워드 콘텐츠 로드 시작:', keyword, 'forceRefresh:', forceRefresh);
    showLoading();
    
    try {
        if (forceRefresh) {
            console.log('[LOAD] 강제 새로고침: /api/refresh 호출');
            const refreshResponse = await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords: [keyword] })
            });
            
            if (!refreshResponse.ok) {
                throw new Error(`새로고침 실패: ${refreshResponse.status}`);
            }
            
            const refreshData = await refreshResponse.json();
            console.log('[LOAD] 새로고침 응답:', refreshData);
            
            // 수집 완료 대기
            console.log('[LOAD] 데이터 수집 완료 대기 중...');
            await new Promise(resolve => setTimeout(resolve, 3000)); // 3초 대기
        }
        
        const url = `/api/content?keyword=${encodeURIComponent(keyword)}`;
        console.log('[LOAD] 데이터 가져오기:', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('[LOAD] 받은 데이터:', {
            키워드: keyword,
            총콘텐츠수: data.total_count || 0,
            유튜브수: data.youtube_count || 0,
            뉴스수: data.news_count || 0,
            콘텐츠배열길이: data.contents ? data.contents.length : 0
        });
        
        allData[keyword] = data;
        currentKeyword = keyword;
        
        displayContent(data);
        
        // 결과가 없으면 경고
        if (!data.contents || data.contents.length === 0) {
            console.warn(`[LOAD] '${keyword}'에 대한 콘텐츠가 없습니다. API 키를 확인하세요.`);
        }
    } catch (error) {
        console.error('[LOAD] 콘텐츠 로드 오류:', error);
        showError(`콘텐츠를 불러올 수 없습니다: ${error.message}`);
        showEmpty();
    } finally {
        hideLoading();
    }
}

// 에러 메시지 표시
function showError(message) {
    // 간단한 알림 (나중에 더 나은 UI로 개선 가능)
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// 아티스트 선택 옵션 업데이트
function updateArtistSelect(keywords) {
    artistSelect.innerHTML = '<option value="all">All Artists</option>';
    keywords.forEach(keyword => {
        const option = document.createElement('option');
        option.value = keyword;
        option.textContent = keyword;
        artistSelect.appendChild(option);
    });
    
    artistSelect.addEventListener('change', (e) => {
        const selected = e.target.value;
        if (selected === 'all') {
            // 모든 키워드 표시
            displayAllContent();
        } else {
            if (allData[selected]) {
                currentKeyword = selected;
                displayContent(allData[selected]);
            } else {
                loadContent(selected);
            }
        }
    });
}

// 모든 콘텐츠 표시
function displayAllContent() {
    const allContents = [];
    Object.values(allData).forEach(data => {
        if (data.contents) {
            allContents.push(...data.contents);
        }
    });
    
    displayContent({ contents: allContents });
}

// 콘텐츠 표시
function displayContent(data) {
    console.log('[DISPLAY] 콘텐츠 표시 시작:', {
        데이터존재: !!data,
        콘텐츠배열존재: !!(data && data.contents),
        콘텐츠수: data && data.contents ? data.contents.length : 0
    });
    
    if (!data || !data.contents || data.contents.length === 0) {
        console.warn('[DISPLAY] 표시할 콘텐츠가 없습니다.');
        showEmpty();
        return;
    }
    
    hideEmpty();
    
    // 콘텐츠 카드 생성
    console.log('[DISPLAY] 카드 생성 시작, 콘텐츠 수:', data.contents.length);
    contents.innerHTML = '';
    data.contents.forEach((content, index) => {
        const card = createContentCard(content, index);
        contents.appendChild(card);
    });
    
    console.log('[DISPLAY] 카드 생성 완료, 생성된 카드 수:', contents.children.length);
    contents.classList.remove('hidden');
    filterContent();
    console.log('[DISPLAY] 콘텐츠 표시 완료');
}

// 콘텐츠 필터링
function filterContent() {
    const cards = contents.querySelectorAll('.content-card');
    cards.forEach(card => {
        const type = card.dataset.type;
        const shouldShow = currentFilter === 'all' || 
                          (currentFilter === 'news' && type === 'news') ||
                          (currentFilter === 'video' && type === 'video');
        card.style.display = shouldShow ? 'block' : 'none';
    });
    
    // 필터링 후 빈 상태 확인
    const visibleCards = Array.from(cards).filter(card => card.style.display !== 'none');
    if (visibleCards.length === 0 && cards.length > 0) {
        showEmpty();
    }
}

// 콘텐츠 카드 생성
function createContentCard(content, index) {
    const card = document.createElement('div');
    card.className = 'content-card';
    card.dataset.type = content.type;
    card.style.animationDelay = `${index * 0.05}s`;
    
    const thumbnail = content.thumbnail 
        ? `<img src="${content.thumbnail}" alt="${escapeHtml(content.title)}" class="card-thumbnail" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'card-thumbnail-placeholder\\'>${content.type === 'video' ? '▶️' : '📰'}</div>'">`
        : `<div class="card-thumbnail-placeholder">${content.type === 'video' ? '▶️' : '📰'}</div>`;
    
    const badgeClass = content.type === 'video' ? 'video' : 'news';
    const badgeText = content.type === 'video' ? 'Video' : 'Article';
    const source = content.channel || content.source || 'Unknown';
    
    card.innerHTML = `
        <div class="relative">
            ${thumbnail}
            <div class="card-badge ${badgeClass}">${badgeText}</div>
        </div>
        <div class="card-body">
            <h3 class="card-title">${escapeHtml(content.title)}</h3>
            <div class="card-source">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                ${escapeHtml(source)}
            </div>
            <div class="card-time">${content.published_at_formatted || ''}</div>
            <a href="${content.url}" target="_blank" rel="noopener noreferrer" class="card-link" onclick="event.stopPropagation()">
                Read Source
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
            </a>
        </div>
    `;
    
    card.addEventListener('click', () => {
        window.open(content.url, '_blank', 'noopener,noreferrer');
    });
    
    return card;
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// UI 상태 관리
function showLoading() {
    loading.classList.remove('hidden');
    contents.classList.add('hidden');
    emptyState.classList.add('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showEmpty() {
    emptyState.classList.remove('hidden');
    contents.classList.add('hidden');
}

function hideEmpty() {
    emptyState.classList.add('hidden');
}

// 자동 새로고침
function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        if (currentKeyword) {
            loadContent(currentKeyword, true);
        } else {
            loadAllContent(true);
        }
    }, 15 * 60 * 1000); // 15분
}

// 서비스 상태 확인
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        console.log('서비스 상태:', status);
        
        // API 키 상태 확인 및 경고
        if (status.api_keys) {
            const missing = [];
            if (status.api_keys.youtube === 'missing') missing.push('YouTube API Key');
            if (status.api_keys.naver_id === 'missing') missing.push('Naver Client ID');
            if (status.api_keys.naver_secret === 'missing') missing.push('Naver Client Secret');
            
            if (missing.length > 0) {
                console.warn('⚠️ API 키가 설정되지 않았습니다:', missing.join(', '));
            }
        }
        
        return status;
    } catch (error) {
        console.error('상태 확인 오류:', error);
        return null;
    }
}

// 주기적으로 상태 확인
setInterval(checkStatus, 5 * 60 * 1000); // 5분마다

// 전역 함수 (HTML에서 호출)
window.handleDeleteKeyword = handleDeleteKeyword;
