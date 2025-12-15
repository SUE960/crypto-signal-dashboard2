"""
코인니스 페이지네이션 디버깅
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def find_chromedriver():
    """ChromeDriver 경로 찾기"""
    paths = [
        '/opt/homebrew/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

print("=" * 70)
print("코인니스 페이지네이션 디버깅")
print("=" * 70)

# ChromeDriver 찾기
chromedriver_path = find_chromedriver()
if not chromedriver_path:
    print("❌ ChromeDriver를 찾을 수 없습니다!")
    sys.exit(1)

print(f"\n✓ ChromeDriver: {chromedriver_path}")

# Chrome 설정
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 페이지 1, 2, 3 테스트
    for page_num in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"페이지 {page_num} 테스트")
        print('='*70)
        
        url = f"https://coinness.com/article?page={page_num}"
        print(f"URL: {url}")
        
        driver.get(url)
        
        # 로딩 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ArticleWrapper-sc-42qvi5-0"))
            )
        except:
            print("❌ ArticleWrapper 로딩 실패")
            continue
        
        time.sleep(2)
        
        # HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in x)
        
        print(f"발견된 기사: {len(articles)}개")
        
        if articles:
            print(f"\n처음 3개 기사 제목:")
            for i, article in enumerate(articles[:3], 1):
                title_elem = article.find('h3', class_=lambda x: x and 'ArticleTitle' in x)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    print(f"  {i}. {title[:50]}...")
        
        # URL이 변경되었는지 확인
        current_url = driver.current_url
        print(f"\n현재 브라우저 URL: {current_url}")
        
        if current_url != url:
            print(f"⚠️  URL이 변경되었습니다!")
            print(f"   요청: {url}")
            print(f"   실제: {current_url}")

finally:
    driver.quit()

print(f"\n{'='*70}")
print("디버깅 완료")
print("="*70)

print("\n💡 분석:")
print("- 각 페이지에서 같은 기사가 나온다면: 페이지네이션이 작동하지 않음")
print("- 각 페이지에서 다른 기사가 나온다면: 중복 제거 로직 문제")
print("- URL이 리다이렉트된다면: 다른 방식으로 페이지 이동 필요")








