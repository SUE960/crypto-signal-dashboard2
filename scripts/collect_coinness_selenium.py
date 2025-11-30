"""
코인니스(Coinness) 뉴스 데이터 수집 스크립트 (Selenium 버전)

JavaScript로 렌더링되는 React 기반 사이트를 Selenium으로 수집합니다.
"""

import os
import time
import random
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# 감정 분석기 초기화
sentiment_analyzer = SentimentIntensityAnalyzer()


class CoinnessSeleniumCollector:
    """Selenium을 사용한 코인니스 뉴스 수집기"""
    
    def __init__(self, headless=True):
        """
        초기화
        
        Args:
            headless: 브라우저를 숨김 모드로 실행할지 여부
        """
        self.base_url = 'https://coinness.com'
        self.driver = None
        self.headless = headless
        self.news_data = []
        
    def setup_driver(self):
        """Chrome WebDriver 설정 (Selenium Manager 사용)"""
        print("Chrome WebDriver 설정 중...")
        print("  (Selenium Manager가 자동으로 ChromeDriver를 관리합니다)")
        
        chrome_options = Options()
        
        # Headless 모드 설정
        if self.headless:
            chrome_options.add_argument('--headless=new')
            print("  모드: Headless (백그라운드)")
        else:
            print("  모드: GUI (브라우저 표시)")
        
        # 필수 옵션
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 자동화 감지 회피
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        # Chrome 바이너리 경로 명시 (macOS)
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        
        try:
            # Selenium 4.6+ 의 Selenium Manager가 자동으로 ChromeDriver 관리
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome WebDriver 설정 완료")
            
        except Exception as e:
            print(f"✗ Chrome WebDriver 설정 실패: {e}")
            print("\n해결 방법:")
            print("1. Chrome 브라우저가 설치되어 있는지 확인")
            print("2. 터미널에서 다음 명령어 실행:")
            print("   brew install --cask google-chrome")
            raise
        
        # 타임아웃 설정
        self.driver.implicitly_wait(10)
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            print("✓ Chrome WebDriver 종료")
    
    def scroll_page(self, scroll_pause_time=2):
        """
        페이지를 스크롤하여 동적 콘텐츠 로딩
        
        Args:
            scroll_pause_time: 스크롤 후 대기 시간
        """
        # 페이지 끝까지 스크롤
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for _ in range(3):  # 최대 3번 스크롤
            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 로딩 대기
            time.sleep(scroll_pause_time)
            
            # 새 높이 계산
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 더 이상 스크롤할 수 없으면 중단
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def parse_time_with_date(self, time_str, date_str):
        """
        시간과 날짜 문자열을 datetime으로 변환
        
        Args:
            time_str: 시간 문자열 (예: "13:30")
            date_str: 날짜 문자열 (예: "2025년 11월 30일 일요일")
            
        Returns:
            datetime: 파싱된 시간
        """
        now = datetime.now()
        
        try:
            # 날짜 파싱
            if '년' in date_str and '월' in date_str and '일' in date_str:
                numbers = re.findall(r'\d+', date_str)
                
                if len(numbers) >= 3:
                    year = int(numbers[0])
                    month = int(numbers[1])
                    day = int(numbers[2])
                    
                    # 시간 파싱
                    if ':' in time_str:
                        time_parts = time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    else:
                        hour = 0
                        minute = 0
                    
                    return datetime(year, month, day, hour, minute)
            
            return now
                
        except Exception as e:
            print(f"  ⚠️  시간 파싱 오류: time={time_str}, date={date_str} - {e}")
            return now
    
    def parse_news_articles(self, html_content):
        """
        HTML에서 뉴스 기사 파싱
        
        Args:
            html_content: HTML 문자열
            
        Returns:
            list: 파싱된 뉴스 데이터 리스트
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        articles_data = []
        
        # ArticleWrapper 클래스를 가진 a 태그 찾기
        articles = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in x)
        
        for article in articles:
            try:
                # 링크
                link = article.get('href', '')
                
                # 제목
                title_elem = article.find('h3', class_=lambda x: x and 'ArticleTitle' in x)
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # 시간 정보
                time_wrap = article.find('div', class_=lambda x: x and 'TimeWrap' in x)
                if time_wrap:
                    time_badge = time_wrap.find('span', class_='time-badge')
                    time_str = time_badge.get_text(strip=True) if time_badge else ''
                    date_text = time_wrap.get_text(strip=True).replace(time_str, '').strip()
                else:
                    time_str = ''
                    date_text = ''
                
                # 시간 파싱
                pub_time = self.parse_time_with_date(time_str, date_text)
                
                # 내용 미리보기
                content_elem = article.find('p', class_=lambda x: x and 'ArticleDesc' in x)
                content = content_elem.get_text(strip=True) if content_elem else ''
                
                # 감정 분석
                text_for_sentiment = f"{title} {content}"
                sentiment = sentiment_analyzer.polarity_scores(text_for_sentiment)
                
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
                print(f"  ⚠️  기사 파싱 오류: {e}")
                continue
        
        return articles_data
    
    def collect_news(self, max_pages=50, start_date=None):
        """
        뉴스를 수집합니다.
        
        Args:
            max_pages: 수집할 최대 페이지 수
            start_date: 수집 시작 날짜
            
        Returns:
            DataFrame: 수집된 뉴스 데이터
        """
        if start_date is None:
            start_date = datetime(2025, 1, 1)
        
        print(f"\n코인니스 뉴스 수집 시작 (Selenium)...")
        print(f"  수집 기간: {start_date.date()} ~ 현재")
        print(f"  최대 페이지: {max_pages}")
        
        # WebDriver 설정
        self.setup_driver()
        
        try:
            collected_count = 0
            
            for page in range(1, max_pages + 1):
                print(f"\n페이지 {page}/{max_pages} 수집 중...")
                
                # 페이지 URL
                url = f"{self.base_url}/article?page={page}"
                
                try:
                    # 페이지 로드
                    self.driver.get(url)
                    
                    # 페이지 로딩 대기 (ArticleWrapper가 나타날 때까지)
                    wait = WebDriverWait(self.driver, 15)
                    wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ArticleWrapper-sc-42qvi5-0"))
                    )
                    
                    # 스크롤하여 동적 콘텐츠 로딩
                    self.scroll_page(scroll_pause_time=1.5)
                    
                    # 랜덤 지연 (1~3초)
                    time.sleep(random.uniform(1, 3))
                    
                    # HTML 가져오기
                    html_content = self.driver.page_source
                    
                    # 기사 파싱
                    articles = self.parse_news_articles(html_content)
                    
                    if not articles:
                        print(f"  ⚠️  페이지 {page}에서 기사를 찾을 수 없습니다.")
                        if page == 1:
                            print(f"  💡 첫 페이지에서 기사를 찾지 못했습니다. 중단합니다.")
                            break
                        continue
                    
                    # 날짜 필터링 및 저장
                    page_count = 0
                    stop_collecting = False
                    
                    for article in articles:
                        if article['timestamp'] < start_date:
                            stop_collecting = True
                            break
                        
                        self.news_data.append(article)
                        page_count += 1
                        collected_count += 1
                    
                    print(f"  ✓ 페이지 {page}에서 {page_count}개 기사 수집 (총 {collected_count}개)")
                    
                    # 날짜 범위를 벗어나면 중단
                    if stop_collecting:
                        print(f"  ✓ 목표 날짜 범위 도달. 수집 중단.")
                        break
                    
                except Exception as e:
                    print(f"  ✗ 페이지 {page} 처리 오류: {e}")
                    continue
            
            print(f"\n✓ 총 {len(self.news_data)}개의 뉴스 기사를 수집했습니다.")
            
            if self.news_data:
                df = pd.DataFrame(self.news_data)
                df = df.sort_values('timestamp', ascending=True)
                return df
            else:
                return pd.DataFrame()
                
        finally:
            # WebDriver 종료
            self.close_driver()


def main():
    """메인 함수"""
    print("=" * 60)
    print("코인니스 뉴스 데이터 수집 (Selenium)")
    print("=" * 60)
    
    # 수집 설정
    start_date = datetime(2025, 1, 1)
    max_pages = 100
    output_file = 'data/coinness_data.csv'
    
    # 수집기 초기화 (headless=True: 브라우저 숨김)
    collector = CoinnessSeleniumCollector(headless=True)
    
    # 뉴스 수집
    df = collector.collect_news(max_pages=max_pages, start_date=start_date)
    
    # 저장
    if not df.empty:
        # 데이터 디렉토리 생성
        os.makedirs('data', exist_ok=True)
        
        # CSV 저장
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 데이터 저장 완료: {output_file}")
        print(f"   총 {len(df)}개 뉴스 기사")
        print(f"   기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        
        # 통계 출력
        print(f"\n📊 수집 통계:")
        print(f"   평균 감정 점수: {df['sentiment_compound'].mean():.3f}")
        print(f"   긍정 비율: {(df['sentiment_compound'] > 0.05).sum() / len(df) * 100:.1f}%")
        print(f"   부정 비율: {(df['sentiment_compound'] < -0.05).sum() / len(df) * 100:.1f}%")
        print(f"   중립 비율: {((df['sentiment_compound'] >= -0.05) & (df['sentiment_compound'] <= 0.05)).sum() / len(df) * 100:.1f}%")
    else:
        print(f"\n⚠️  수집된 데이터가 없습니다.")


if __name__ == '__main__':
    main()

