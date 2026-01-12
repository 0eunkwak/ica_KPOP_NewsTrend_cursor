@echo off
chcp 65001 >nul
echo ========================================
echo K-POP 뉴스 트렌드 서버 시작 중...
echo ========================================
cd /d "%~dp0backend"
python app.py
pause
