"""
코인니스 뉴스 수집 (무한 스크롤 방식)

무한 스크롤로 구현된 코인니스에서 데이터를 수집합니다.
"""

import os
import sys
import time
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

sentiment_analyzer = SentimentIntensityAnalyzer()


def find_chromedriver():
    """ChromeDriver 찾기"""
    paths = [
        '/opt/homebrew/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
    ]
    for path in paths:
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
            
            pub_time = parse_time_with_date(time_str, date_text)
            
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
        except:
            continue
    
    return articles_data


def collect_with_infinite_scroll(chromedriver_path, start_date, max_articles=20000):
    """
    무한 스크롤로 뉴스 수집
    
    Args:
        chromedriver_path: ChromeDriver 경로
        start_date: 수집 시작 날짜
        max_articles: 최대 수집 기사 수 (안전장치)
    """
    print(f"ChromeDriver: {chromedriver_path}")
    print(f"수집 목표: {start_date.date()} ~ 현재")
    print(f"최대 기사 수: {max_articles:,}개\n")
    
    # Chrome 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,3000')  # 높은 창
    chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    )
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_articles = []
    seen_articles = set()  # 중복 체크
    
    try:
        print("📱 코인니스 접속 중...")
        driver.get('https://coinness.com/article')
        
        # 초기 로딩 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ArticleWrapper-sc-42qvi5-0"))
        )
        time.sleep(2)
        
        print("✓ 페이지 로딩 완료\n")
        print("🔄 '더보기' 버튼 클릭 시작...\n")
        
        no_new_articles_count = 0
        click_count = 0
        button_not_found_count = 0
        
        while True:
            click_count += 1
            
            # 현재 HTML 파싱
            html = driver.page_source
            articles = parse_articles(html)
            
            # 새로운 기사만 추가
            new_count = 0
            stop_collecting = False
            
            for article in articles:
                article_key = (article['title'], article['timestamp'])
                
                # 날짜 체크
                if article['timestamp'] < start_date:
                    stop_collecting = True
                    break
                
                # 중복 체크
                if article_key not in seen_articles:
                    seen_articles.add(article_key)
                    all_articles.append(article)
                    new_count += 1
            
            total_collected = len(all_articles)
            total_duplicates = len(seen_articles) - total_collected
            
            print(f"클릭 {click_count:3d}: 신규 {new_count:3d}개 | "
                  f"총 {total_collected:5d}개 / {max_articles:,}개 | 중복 {total_duplicates:5d}개", end='')
            
            # 종료 조건
            if stop_collecting:
                print(f" → ✓ 목표 날짜 도달!")
                break
            
            if total_collected >= max_articles:
                print(f" → ✓ 목표 기사 수({max_articles:,}개) 달성! 자동 중단합니다.")
                break
            
            if new_count == 0:
                no_new_articles_count += 1
                print(f" → ⚠️  신규 없음 ({no_new_articles_count}/5)")
                
                if no_new_articles_count >= 5:
                    print(f"\n⚠️  5번 연속 신규 기사 없음. 종료.")
                    break
            else:
                no_new_articles_count = 0
                print()
            
            # "더보기" 버튼 찾기 및 클릭
            try:
                # 버튼 찾기 (여러 방법 시도)
                more_button = None
                
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
                
                if more_button and more_button.is_displayed():
                    # 버튼이 보이는 위치로 스크롤
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
                    time.sleep(0.5)
                    
                    # 클릭
                    more_button.click()
                    button_not_found_count = 0
                    
                    # 로딩 대기
                    time.sleep(2 + (click_count % 3))
                    
                    # 10번마다 휴식
                    if click_count % 10 == 0:
                        print(f"   💤 휴식 (5초)...")
                        time.sleep(5)
                else:
                    button_not_found_count += 1
                    print(f" → ⚠️  '더보기' 버튼 없음 ({button_not_found_count}/3)")
                    
                    if button_not_found_count >= 3:
                        print(f"\n⚠️  '더보기' 버튼을 찾을 수 없음. 종료.")
                        break
                    
                    time.sleep(2)
                    
            except Exception as e:
                button_not_found_count += 1
                print(f" → ❌ 버튼 클릭 오류: {e}")
                
                if button_not_found_count >= 3:
                    print(f"\n⚠️  버튼 클릭 실패 3회. 종료.")
                    break
                
                time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"수집 완료!")
        print(f"총 클릭: {click_count}회")
        print(f"총 기사: {len(all_articles):,}개")
        print(f"중복 제외: {len(seen_articles) - len(all_articles):,}개")
        print('='*70)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  사용자에 의해 중단되었습니다 (Ctrl+C)")
        print(f"지금까지 수집한 {len(all_articles):,}개 기사를 저장합니다...")
        try:
            driver.quit()
        except:
            pass
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass
    
    return all_articles


def main():
    """메인 함수"""
    print("=" * 70)
    print("코인니스 뉴스 수집 ('더보기' 버튼 클릭)")
    print("=" * 70)
    print()
    
    # ChromeDriver 찾기
    chromedriver_path = find_chromedriver()
    if not chromedriver_path:
        print("❌ ChromeDriver를 찾을 수 없습니다!")
        print("\n설치:")
        print("  brew install --cask chromedriver")
        print("  xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver")
        return
    
    # 수집
    start_date = datetime(2025, 1, 1)
    articles = collect_with_infinite_scroll(
        chromedriver_path=chromedriver_path,
        start_date=start_date,
        max_articles=5000  # 최대 5,000개 (목표 달성 시 자동 중단)
    )
    
    # 저장
    if articles:
        df = pd.DataFrame(articles)
        df = df.sort_values('timestamp', ascending=True)
        
        os.makedirs('data', exist_ok=True)
        output_file = 'data/coinness_data2.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ 저장: {output_file}")
        print(f"   총 {len(df):,}개 기사")
        print(f"   기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        
        # 월별 통계
        print(f"\n📅 월별 기사 수:")
        monthly = df.groupby(df['timestamp'].dt.to_period('M')).size().sort_index()
        for month, count in monthly.items():
            print(f"   {month}: {count:,}개")
        
        # 감정 분석
        print(f"\n💭 감정 분석:")
        print(f"   평균: {df['sentiment_compound'].mean():.3f}")
        pos = (df['sentiment_compound'] > 0.05).sum()
        neg = (df['sentiment_compound'] < -0.05).sum()
        print(f"   긍정: {pos:,}개 ({pos/len(df)*100:.1f}%)")
        print(f"   부정: {neg:,}개 ({neg/len(df)*100:.1f}%)")
    else:
        print("\n⚠️  수집된 데이터 없음")


if __name__ == '__main__':
    main()

