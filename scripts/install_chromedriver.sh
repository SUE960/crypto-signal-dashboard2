#!/bin/bash

echo "============================================================"
echo "ChromeDriver 설치 스크립트"
echo "============================================================"

# ChromeDriver 설치 (Homebrew)
echo ""
echo "1. ChromeDriver 설치 중..."
brew install --cask chromedriver 2>&1 | grep -v "already installed" || echo "ChromeDriver 설치 완료 또는 이미 설치됨"

# ChromeDriver 경로 확인
CHROMEDRIVER_PATH="/opt/homebrew/bin/chromedriver"

if [ ! -f "$CHROMEDRIVER_PATH" ]; then
    CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"
fi

if [ -f "$CHROMEDRIVER_PATH" ]; then
    echo ""
    echo "2. ChromeDriver 경로: $CHROMEDRIVER_PATH"
    
    # 실행 권한 부여
    chmod +x "$CHROMEDRIVER_PATH"
    
    # macOS Gatekeeper 제거
    echo ""
    echo "3. macOS 보안 제한 해제 중..."
    xattr -d com.apple.quarantine "$CHROMEDRIVER_PATH" 2>/dev/null || true
    
    # 버전 확인
    echo ""
    echo "4. ChromeDriver 버전:"
    "$CHROMEDRIVER_PATH" --version
    
    echo ""
    echo "✅ ChromeDriver 설치 완료!"
    echo "   경로: $CHROMEDRIVER_PATH"
else
    echo ""
    echo "❌ ChromeDriver를 찾을 수 없습니다."
    echo ""
    echo "수동 설치 방법:"
    echo "1. 터미널에서 실행:"
    echo "   brew install --cask chromedriver"
    echo ""
    echo "2. 또는 다운로드:"
    echo "   https://googlechromelabs.github.io/chrome-for-testing/"
fi

echo ""
echo "============================================================"








