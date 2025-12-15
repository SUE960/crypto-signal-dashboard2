"""
코인니스 아티클 페이지 무한 스크롤 크롤링

https://coinness.com/article 페이지에서 무한 스크롤을 사용하여
모든 아티클을 수집합니다.
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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


def parse_time_with_date(time_str, date_str):
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


def parse_articles(html):
    """HTML에서 기사 파싱"""
    soup = BeautifulSoup(html, 'html.parser')
    articles_data = []
    
    # ArticleWrapper 클래스를 가진 a 태그 찾기
    articles = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in str(x))
    
    for article in articles:
        try:
            # 링크 추출
            link = article.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://coinness.com{link}"
            
            # 제목 추출
            title_elem = article.find('h3', class_=lambda x: x and 'ArticleTitle' in str(x))
            if not title_elem:
                # 대체 방법: h3 태그 직접 찾기
                title_elem = article.find('h3')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            
            # 시간 추출
            time_wrap = article.find('div', class_=lambda x: x and 'TimeWrap' in str(x))
            if time_wrap:
                time_badge = time_wrap.find('span', class_='time-badge')
                time_str = time_badge.get_text(strip=True) if time_badge else ''
                date_text = time_wrap.get_text(strip=True).replace(time_str, '').strip()
            else:
                # 대체 방법: 시간 관련 텍스트 찾기
                time_elem = article.find(string=re.compile(r'\d{4}년|\d{1,2}월|\d{1,2}일'))
                if time_elem:
                    date_text = time_elem.strip()
                    time_str = ''
                else:
                    time_str = ''
                    date_text = ''
            
            pub_time = parse_time_with_date(time_str, date_text)
            
            # 내용 추출
            content_elem = article.find('p', class_=lambda x: x and 'ArticleDesc' in str(x))
            if not content_elem:
                content_elem = article.find('p')
            content = content_elem.get_text(strip=True) if content_elem else ''
            
            # 감정 분석
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
            print(f"  ⚠️  기사 파싱 오류: {e}")
            continue
    
    return articles_data


def scroll_to_bottom(driver, pause_time=2):
    """페이지를 맨 아래까지 스크롤"""
    # 현재 스크롤 위치 저장
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 새 콘텐츠 로딩 대기
        time.sleep(pause_time)
        
        # 새로운 스크롤 높이 계산
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # 높이가 변하지 않으면 더 이상 로드할 콘텐츠 없음
        if new_height == last_height:
            break
        
        last_height = new_height


def collect_with_infinite_scroll(chromedriver_path, start_date=None, max_articles=50000, max_scrolls=500):
    """
    무한 스크롤로 뉴스 수집
    
    Args:
        chromedriver_path: ChromeDriver 경로
        start_date: 수집 시작 날짜 (이 날짜 이전의 뉴스는 수집 중단)
        max_articles: 최대 수집 기사 수
        max_scrolls: 최대 스크롤 횟수 (안전장치)
    """
    print(f"ChromeDriver: {chromedriver_path}")
    if start_date:
        print(f"수집 목표: {start_date.date()} ~ 현재")
    else:
        print(f"수집 목표: 전체")
    print(f"최대 기사 수: {max_articles:,}개")
    print(f"최대 스크롤 횟수: {max_scrolls:,}회\n")
    
    # Chrome 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,3000')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    )
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_articles = []
    seen_links = set()  # 중복 체크 (링크 기준)
    seen_titles = set()  # 중복 체크 (제목 기준)
    
    try:
        print("📱 코인니스 아티클 페이지 접속 중...")
        driver.get('https://coinness.com/article')
        
        # 초기 로딩 대기
        print("  페이지 로딩 대기 중...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print("  ⚠️  타임아웃, 계속 진행...")
        
        time.sleep(3)  # 초기 콘텐츠 로딩 대기
        
        print("✓ 페이지 로딩 완료\n")
        print("🔄 무한 스크롤 시작...\n")
        
        scroll_count = 0
        no_new_articles_count = 0
        last_article_count = 0
        
        while scroll_count < max_scrolls:
            scroll_count += 1
            
            # 현재 HTML 파싱
            html = driver.page_source
            articles = parse_articles(html)
            
            # 새로운 기사만 추가
            new_count = 0
            stop_collecting = False
            
            for article in articles:
                # 링크와 제목으로 중복 체크
                link_key = article['link']
                title_key = article['title']
                
                # 날짜 체크 (start_date가 지정된 경우)
                if start_date and article['timestamp'] < start_date:
                    stop_collecting = True
                    break
                
                # 중복 체크
                if link_key not in seen_links and title_key not in seen_titles:
                    seen_links.add(link_key)
                    seen_titles.add(title_key)
                    all_articles.append(article)
                    new_count += 1
            
            total_collected = len(all_articles)
            
            # 진행 상황 출력
            if scroll_count % 5 == 0 or new_count > 0:
                print(f"스크롤 {scroll_count:3d}: 신규 {new_count:3d}개 | "
                      f"총 {total_collected:5d}개", end='')
                
                if stop_collecting:
                    print(f" → ✓ 목표 날짜 도달!")
                    break
                
                if total_collected >= max_articles:
                    print(f" → ✓ 최대 기사 수 도달!")
                    break
                
                if new_count == 0:
                    no_new_articles_count += 1
                    print(f" → ⚠️  신규 없음 ({no_new_articles_count}/10)")
                    
                    if no_new_articles_count >= 10:
                        print(f"\n⚠️  10번 연속 신규 기사 없음. 종료.")
                        break
                else:
                    no_new_articles_count = 0
                    print()
            
            # 종료 조건
            if stop_collecting:
                break
            
            if total_collected >= max_articles:
                break
            
            # 스크롤 다운 및 "더보기" 버튼 클릭 시도
            # 먼저 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            
            # "더보기" 버튼 찾기 및 클릭
            more_button = None
            try:
                # 방법 1: 클래스 이름으로 찾기
                try:
                    more_button = driver.find_element(By.CLASS_NAME, "ButtonWrapper-sc-w6h248-0")
                except:
                    pass
                
                # 방법 2: 버튼 텍스트로 찾기
                if not more_button:
                    try:
                        more_button = driver.find_element(By.XPATH, "//button[contains(text(), '더보기')]")
                    except:
                        pass
                
                # 방법 3: CSS 선택자
                if not more_button:
                    try:
                        more_button = driver.find_element(By.CSS_SELECTOR, "button.ButtonWrapper-sc-w6h248-0")
                    except:
                        pass
                
                # 방법 4: data-testid 또는 다른 속성으로 찾기
                if not more_button:
                    try:
                        more_button = driver.find_element(By.CSS_SELECTOR, "button[class*='Button'], button[class*='More']")
                    except:
                        pass
                
                if more_button and more_button.is_displayed():
                    # 버튼이 보이는 위치로 스크롤
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", more_button)
                    time.sleep(0.5)
                    
                    # 클릭
                    more_button.click()
                    time.sleep(2)
                else:
                    # 버튼이 없으면 일반 스크롤
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.END)
                    time.sleep(2)
            except Exception as e:
                # 버튼 클릭 실패 시 일반 스크롤
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.END)
                time.sleep(2)
            
            # 10번마다 더 긴 휴식
            if scroll_count % 10 == 0:
                print(f"   💤 휴식 (3초)...")
                time.sleep(3)
                
                # 현재 높이 확인
                current_height = driver.execute_script("return document.body.scrollHeight")
                print(f"   현재 페이지 높이: {current_height:,}px")
        
        print(f"\n{'='*70}")
        print(f"수집 완료!")
        print(f"총 스크롤: {scroll_count}회")
        print(f"총 기사: {len(all_articles):,}개")
        print(f"중복 제외: {len(seen_links) - len(all_articles):,}개")
        print('='*70)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
    
    return all_articles


def main():
    """메인 함수"""
    print("=" * 70)
    print("코인니스 아티클 페이지 무한 스크롤 크롤링")
    print("=" * 70)
    print()
    
    # ChromeDriver 찾기
    chromedriver_path = find_chromedriver()
    if not chromedriver_path:
        print("❌ ChromeDriver를 찾을 수 없습니다!")
        print("\n설치 방법:")
        print("  bash scripts/install_chromedriver.sh")
        print("\n또는:")
        print("  brew install --cask chromedriver")
        print("  xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver")
        return
    
    # 수집 설정
    # 최근 일주일치만 수집하려면:
    # start_date = datetime.now() - timedelta(days=7)
    # 전체 수집하려면:
    start_date = None  # None이면 전체 수집
    
    print(f"수집 시작 날짜: {start_date.date() if start_date else '전체'}\n")
    
    # 수집 실행
    articles = collect_with_infinite_scroll(
        chromedriver_path=chromedriver_path,
        start_date=start_date,
        max_articles=50000,  # 최대 50,000개
        max_scrolls=1000     # 최대 1,000번 스크롤
    )
    
    # 저장
    if articles:
        df = pd.DataFrame(articles)
        
        # 중복 제거 (링크 기준)
        df = df.drop_duplicates(subset=['link'], keep='first')
        
        # 타임스탬프 기준 정렬
        df = df.sort_values('timestamp', ascending=False)
        
        # 데이터 디렉토리 생성
        os.makedirs('data', exist_ok=True)
        
        # 파일명 생성
        if start_date:
            output_file = f'data/coinness_article_{start_date.strftime("%Y%m%d")}_to_{datetime.now().strftime("%Y%m%d")}.csv'
        else:
            output_file = 'data/coinness_article_all.csv'
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 저장 완료: {output_file}")
        print(f"   총 {len(df):,}개 기사")
        if not df.empty:
            print(f"   기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        
        # 월별 통계
        if not df.empty:
            print(f"\n📅 월별 기사 수:")
            monthly = df.groupby(df['timestamp'].dt.to_period('M')).size().sort_index(ascending=False)
            for month, count in monthly.head(12).items():  # 최근 12개월만
                print(f"   {month}: {count:,}개")
        
        # 감정 분석
        if not df.empty:
            print(f"\n💭 감정 분석:")
            print(f"   평균: {df['sentiment_compound'].mean():.3f}")
            pos = (df['sentiment_compound'] > 0.05).sum()
            neg = (df['sentiment_compound'] < -0.05).sum()
            neu = len(df) - pos - neg
            print(f"   긍정: {pos:,}개 ({pos/len(df)*100:.1f}%)")
            print(f"   부정: {neg:,}개 ({neg/len(df)*100:.1f}%)")
            print(f"   중립: {neu:,}개 ({neu/len(df)*100:.1f}%)")
    else:
        print("\n⚠️  수집된 데이터 없음")


if __name__ == '__main__':
    main()

