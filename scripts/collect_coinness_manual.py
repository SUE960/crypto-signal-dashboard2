"""
코인니스 뉴스 수집 (수동 ChromeDriver 경로 지정)

ChromeDriver를 수동으로 설치하고 경로를 직접 지정합니다.
"""

import os
import sys
import time
import random
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# 감정 분석기
sentiment_analyzer = SentimentIntensityAnalyzer()


def find_chromedriver():
    """ChromeDriver 경로 찾기"""
    possible_paths = [
        '/opt/homebrew/bin/chromedriver',  # Apple Silicon Mac
        '/usr/local/bin/chromedriver',     # Intel Mac
        '/usr/bin/chromedriver',           # Linux
        os.path.expanduser('~/.local/bin/chromedriver'),  # 사용자 설치
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


class CoinnessCollector:
    """코인니스 수집기"""
    
    def __init__(self, chromedriver_path=None, headless=True):
        """
        초기화
        
        Args:
            chromedriver_path: ChromeDriver 실행 파일 경로
            headless: Headless 모드 사용 여부
        """
        self.chromedriver_path = chromedriver_path or find_chromedriver()
        self.headless = headless
        self.driver = None
        self.base_url = 'https://coinness.com'
        self.news_data = []
    
    def setup_driver(self):
        """ChromeDriver 설정"""
        if not self.chromedriver_path:
            print("❌ ChromeDriver를 찾을 수 없습니다!")
            print("\n설치 방법:")
            print("1. 터미널에서 실행:")
            print("   bash scripts/install_chromedriver.sh")
            print("\n2. 또는 수동 설치:")
            print("   brew install --cask chromedriver")
            print("   xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver")
            sys.exit(1)
        
        print(f"ChromeDriver 경로: {self.chromedriver_path}")
        
        # Chrome 옵션 설정
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        # Chrome 바이너리
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        
        # Service 생성
        service = Service(executable_path=self.chromedriver_path)
        
        # Driver 생성
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✓ ChromeDriver 설정 완료\n")
        except Exception as e:
            print(f"❌ ChromeDriver 실행 실패: {e}")
            print("\n해결 방법:")
            print("xattr -d com.apple.quarantine " + self.chromedriver_path)
            raise
    
    def close_driver(self):
        """Driver 종료"""
        if self.driver:
            self.driver.quit()
    
    def parse_time_with_date(self, time_str, date_str):
        """시간 파싱"""
        now = datetime.now()
        try:
            if '년' in date_str and '월' in date_str and '일' in date_str:
                numbers = re.findall(r'\d+', date_str)
                if len(numbers) >= 3:
                    year = int(numbers[0])
                    month = int(numbers[1])
                    day = int(numbers[2])
                    
                    if ':' in time_str:
                        time_parts = time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    else:
                        hour = 0
                        minute = 0
                    
                    return datetime(year, month, day, hour, minute)
            return now
        except:
            return now
    
    def parse_articles(self, html):
        """HTML에서 기사 파싱"""
        soup = BeautifulSoup(html, 'html.parser')
        articles_data = []
        
        articles = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in x)
        
        for article in articles:
            try:
                link = article.get('href', '')
                
                title_elem = article.find('h3', class_=lambda x: x and 'ArticleTitle' in x)
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                time_wrap = article.find('div', class_=lambda x: x and 'TimeWrap' in x)
                if time_wrap:
                    time_badge = time_wrap.find('span', class_='time-badge')
                    time_str = time_badge.get_text(strip=True) if time_badge else ''
                    date_text = time_wrap.get_text(strip=True).replace(time_str, '').strip()
                else:
                    time_str = ''
                    date_text = ''
                
                pub_time = self.parse_time_with_date(time_str, date_text)
                
                content_elem = article.find('p', class_=lambda x: x and 'ArticleDesc' in x)
                content = content_elem.get_text(strip=True) if content_elem else ''
                
                text = f"{title} {content}"
                sentiment = sentiment_analyzer.polarity_scores(text)
                
                articles_data.append({
                    'timestamp': pub_time,
                    'title': title,
                    'content': content,
                    'link': link,
                    'sentiment_compound': sentiment['compound'],
                    'sentiment_positive': sentiment['pos'],
                    'sentiment_negative': sentiment['neg'],
                    'sentiment_neutral': sentiment['neu'],
                })
            except Exception as e:
                continue
        
        return articles_data
    
    def collect_news(self, max_pages=50, start_date=None):
        """뉴스 수집"""
        if start_date is None:
            start_date = datetime(2025, 1, 1)
        
        print(f"코인니스 뉴스 수집 시작")
        print(f"수집 기간: {start_date.date()} ~ 현재")
        print(f"최대 페이지: {max_pages}\n")
        
        self.setup_driver()
        
        # 중복 체크를 위한 Set (제목 + 시간)
        seen_articles = set()
        
        try:
            collected = 0
            duplicates = 0
            
            for page in range(1, max_pages + 1):
                print(f"페이지 {page}/{max_pages} 수집 중...", end=' ')
                
                url = f"{self.base_url}/article?page={page}"
                
                try:
                    self.driver.get(url)
                    
                    # ArticleWrapper 로딩 대기
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ArticleWrapper-sc-42qvi5-0"))
                    )
                    
                    # 스크롤
                    for _ in range(2):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                    
                    time.sleep(random.uniform(1, 2))
                    
                    # 파싱
                    html = self.driver.page_source
                    articles = self.parse_articles(html)
                    
                    if not articles:
                        print("❌ 기사 없음")
                        if page == 1:
                            break
                        continue
                    
                    # 필터링 및 중복 제거
                    page_count = 0
                    stop = False
                    
                    for article in articles:
                        if article['timestamp'] < start_date:
                            stop = True
                            break
                        
                        # 중복 체크 (제목 + 시간)
                        article_key = (article['title'], article['timestamp'])
                        
                        if article_key in seen_articles:
                            duplicates += 1
                            continue
                        
                        seen_articles.add(article_key)
                        self.news_data.append(article)
                        page_count += 1
                        collected += 1
                    
                    print(f"✓ {page_count}개 수집 (총 {collected}개, 중복 제외: {duplicates}개)")
                    
                    if stop:
                        print(f"\n✓ 목표 날짜 도달. 수집 종료.")
                        break
                    
                except Exception as e:
                    print(f"❌ 오류: {e}")
                    continue
            
            print(f"\n총 {len(self.news_data)}개 기사 수집 완료!")
            print(f"중복 제거: {duplicates}개\n")
            
            if self.news_data:
                df = pd.DataFrame(self.news_data)
                
                # 추가 중복 제거 (혹시 모를 경우 대비)
                before_dedup = len(df)
                df = df.drop_duplicates(subset=['title', 'timestamp'])
                after_dedup = len(df)
                
                if before_dedup > after_dedup:
                    print(f"⚠️  최종 중복 제거: {before_dedup - after_dedup}개")
                
                df = df.sort_values('timestamp', ascending=True)
                return df
            else:
                return pd.DataFrame()
        
        finally:
            self.close_driver()


def main():
    """메인 함수"""
    print("=" * 60)
    print("코인니스 뉴스 데이터 수집 (수동 ChromeDriver)")
    print("=" * 60)
    print()
    
    # ChromeDriver 찾기
    chromedriver_path = find_chromedriver()
    
    if chromedriver_path:
        print(f"✓ ChromeDriver 발견: {chromedriver_path}\n")
    else:
        print("❌ ChromeDriver를 찾을 수 없습니다!")
        print("\n설치 방법:")
        print("  bash scripts/install_chromedriver.sh")
        print("\n또는:")
        print("  brew install --cask chromedriver")
        print("  xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver")
        return
    
    # 수집 (2025년 전체 커버, 자동 중단 기능 있음)
    collector = CoinnessCollector(chromedriver_path=chromedriver_path, headless=True)
    df = collector.collect_news(max_pages=2000, start_date=datetime(2025, 1, 1))
    
    # 저장
    if not df.empty:
        os.makedirs('data', exist_ok=True)
        output_file = 'data/coinness_data.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ 저장 완료: {output_file}")
        print(f"   총 {len(df)}개 기사")
        print(f"   기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        print(f"\n📊 감정 분석:")
        print(f"   평균: {df['sentiment_compound'].mean():.3f}")
        print(f"   긍정: {(df['sentiment_compound'] > 0.05).sum() / len(df) * 100:.1f}%")
        print(f"   부정: {(df['sentiment_compound'] < -0.05).sum() / len(df) * 100:.1f}%")
    else:
        print("⚠️  수집된 데이터 없음")


if __name__ == '__main__':
    main()

