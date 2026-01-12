// 전역 변수
let currentKeyword = '';
let allData = {};
let currentFilter = 'all';
let autoRefreshInterval = null;

// DOM 요소
const sidebar = document.getElementById('sidebar');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileOverlay = document.getElementById('mobile-overlay');
const themeToggle = document.getElementById('theme-toggle');
const sunIcon = document.getElementById('sun-icon');
const moonIcon = document.getElementById('moon-icon');
const refreshBtn = document.getElementById('refreshBtn');
const contents = document.getElementById('contents');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const artistSelect = document.getElementById('artist-select');
const filterTabs = document.querySelectorAll('.filter-tab');

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    setupEventListeners();
    loadAllContent();
    startAutoRefresh();
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
    });
    
    document.getElementById('menu-keywords').addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
        document.getElementById('menu-keywords').classList.add('active');
    });
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
    showLoading();
    
    try {
        const url = forceRefresh ? '/api/refresh' : '/api/content';
        const options = forceRefresh ? {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keywords: [] })
        } : {};
        
        const response = await fetch(url, options);
        const data = await response.json();
        
        allData = data;
        
        // 아티스트 선택 옵션 업데이트
        updateArtistSelect(Object.keys(data));
        
        // 첫 번째 키워드 선택
        if (Object.keys(data).length > 0) {
            currentKeyword = Object.keys(data)[0];
            displayContent(data[currentKeyword]);
        } else {
            showEmpty();
        }
    } catch (error) {
        console.error('데이터 로드 오류:', error);
        showEmpty();
    } finally {
        hideLoading();
    }
}

// 특정 키워드 콘텐츠 로드
async function loadContent(keyword, forceRefresh = false) {
    showLoading();
    
    try {
        let url = `/api/content?keyword=${encodeURIComponent(keyword)}`;
        if (forceRefresh) {
            await fetch('/api/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keywords: [keyword] })
            });
            url = `/api/content?keyword=${encodeURIComponent(keyword)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        allData[keyword] = data;
        currentKeyword = keyword;
        
        displayContent(data);
    } catch (error) {
        console.error('콘텐츠 로드 오류:', error);
        showEmpty();
    } finally {
        hideLoading();
    }
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
    if (!data || !data.contents || data.contents.length === 0) {
        showEmpty();
        return;
    }
    
    hideEmpty();
    
    // 콘텐츠 카드 생성
    contents.innerHTML = '';
    data.contents.forEach((content, index) => {
        const card = createContentCard(content, index);
        contents.appendChild(card);
    });
    
    contents.classList.remove('hidden');
    filterContent();
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
    } catch (error) {
        console.error('상태 확인 오류:', error);
    }
}

// 주기적으로 상태 확인
setInterval(checkStatus, 5 * 60 * 1000); // 5분마다
