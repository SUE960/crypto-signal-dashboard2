"""
코인니스(Coinness) 뉴스 데이터 수집 스크립트

암호화폐 뉴스 사이트에서 기사 데이터를 수집합니다.
"""

import os
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 감정 분석기 초기화
sentiment_analyzer = SentimentIntensityAnalyzer()

# User-Agent 리스트 (웹 스크래핑 방지 우회)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]


class CoinnessCollector:
    """코인니스 뉴스 수집기"""
    
    def __init__(self):
        """초기화"""
        self.session = requests.Session()
        self.base_url = 'https://coinness.com'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.retry_count = 3
        self.news_data = []
    
    def get_random_user_agent(self):
        """랜덤 User-Agent 반환"""
        return random.choice(USER_AGENTS)
    
    def fetch_page(self, url, page_num=1):
        """
        페이지를 가져옵니다.
        
        Args:
            url: 요청할 URL
            page_num: 페이지 번호
            
        Returns:
            BeautifulSoup 객체 또는 None
        """
        for attempt in range(self.retry_count):
            try:
                # User-Agent 랜덤 변경
                self.headers['User-Agent'] = self.get_random_user_agent()
                
                # 요청 전 지연 (1.5~3.5초)
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)
                
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    return BeautifulSoup(response.text, 'html.parser')
                elif response.status_code == 429:
                    # Rate limiting - 더 긴 지연
                    wait_time = random.uniform(10, 30)
                    print(f"  ⚠️  Rate limit 감지. {wait_time:.1f}초 대기 중...")
                    time.sleep(wait_time)
                else:
                    print(f"  ⚠️  페이지 {page_num} 요청 실패: {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ 페이지 {page_num} 요청 오류 (시도 {attempt + 1}/{self.retry_count}): {e}")
                
                if attempt < self.retry_count - 1:
                    wait_time = random.uniform(3, 8)
                    time.sleep(wait_time)
        
        return None
    
    def parse_news_article(self, article_elem):
        """
        뉴스 기사 요소를 파싱합니다.
        
        Args:
            article_elem: BeautifulSoup 기사 요소 (a 태그)
            
        Returns:
            dict: 파싱된 뉴스 데이터 또는 None
        """
        try:
            # 링크 (a 태그 자체가 링크)
            link = article_elem.get('href', '')
            
            # 제목 (h3 태그)
            title_elem = article_elem.find('h3', class_=lambda x: x and 'ArticleTitle' in x)
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # 시간 정보 (TimeWrap 안에 있음)
            time_wrap = article_elem.find('div', class_=lambda x: x and 'TimeWrap' in x)
            if time_wrap:
                # time-badge (시간)
                time_badge = time_wrap.find('span', class_='time-badge')
                time_str = time_badge.get_text(strip=True) if time_badge else ''
                
                # 날짜 (TimeWrap의 텍스트에서 추출)
                date_text = time_wrap.get_text(strip=True)
                # "13:302025년 11월 30일 일요일" 형태에서 날짜 추출
                date_parts = date_text.replace(time_str, '').strip()
            else:
                time_str = ''
                date_parts = ''
            
            # 시간 파싱
            pub_time = self.parse_time_with_date(time_str, date_parts)
            
            # 내용 미리보기 (p 태그)
            content_elem = article_elem.find('p', class_=lambda x: x and 'ArticleDesc' in x)
            content = content_elem.get_text(strip=True) if content_elem else ''
            
            # 감정 분석 (제목 + 내용)
            text_for_sentiment = f"{title} {content}"
            sentiment = sentiment_analyzer.polarity_scores(text_for_sentiment)
            
            return {
                'timestamp': pub_time,
                'title': title,
                'content': content,
                'link': link,
                'sentiment_compound': sentiment['compound'],
                'sentiment_positive': sentiment['pos'],
                'sentiment_negative': sentiment['neg'],
                'sentiment_neutral': sentiment['neu'],
            }
            
        except Exception as e:
            print(f"  ⚠️  기사 파싱 오류: {e}")
            return None
    
    def parse_time_with_date(self, time_str, date_str):
        """
        시간과 날짜 문자열을 datetime으로 변환합니다.
        
        Args:
            time_str: 시간 문자열 (예: "13:30")
            date_str: 날짜 문자열 (예: "2025년 11월 30일 일요일")
            
        Returns:
            datetime: 파싱된 시간
        """
        now = datetime.now()
        
        try:
            # 날짜 파싱 (예: "2025년 11월 30일 일요일")
            if '년' in date_str and '월' in date_str and '일' in date_str:
                # 날짜에서 숫자만 추출
                import re
                numbers = re.findall(r'\d+', date_str)
                
                if len(numbers) >= 3:
                    year = int(numbers[0])
                    month = int(numbers[1])
                    day = int(numbers[2])
                    
                    # 시간 파싱 (예: "13:30")
                    if ':' in time_str:
                        time_parts = time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    else:
                        hour = 0
                        minute = 0
                    
                    return datetime(year, month, day, hour, minute)
            
            # 파싱 실패 시 현재 시간 반환
            return now
                
        except Exception as e:
            print(f"  ⚠️  시간 파싱 오류: time={time_str}, date={date_str} - {e}")
            return now
    
    def collect_news(self, max_pages=50, start_date=None):
        """
        뉴스를 수집합니다.
        
        Args:
            max_pages: 수집할 최대 페이지 수
            start_date: 수집 시작 날짜 (이 날짜 이후의 뉴스만 수집)
            
        Returns:
            DataFrame: 수집된 뉴스 데이터
        """
        if start_date is None:
            start_date = datetime(2025, 1, 1)
        
        print(f"\n코인니스 뉴스 수집 시작...")
        print(f"  수집 기간: {start_date.date()} ~ 현재")
        print(f"  최대 페이지: {max_pages}")
        
        collected_count = 0
        
        for page in range(1, max_pages + 1):
            print(f"\n페이지 {page}/{max_pages} 수집 중...")
            
            # 페이지 URL 구성
            url = f"{self.base_url}/article?page={page}"
            
            # 페이지 가져오기
            soup = self.fetch_page(url, page)
            if not soup:
                print(f"  ✗ 페이지 {page} 로딩 실패")
                continue
            
            # 뉴스 기사 찾기 (코인니스 구조)
            # ArticleWrapper 클래스를 가진 a 태그들
            articles = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in x)
            
            if not articles:
                print(f"  ⚠️  페이지 {page}에서 기사를 찾을 수 없습니다.")
                # 첫 페이지에서도 찾지 못하면 중단
                if page == 1:
                    print(f"  💡 HTML 구조 확인이 필요할 수 있습니다.")
                    break
                continue
            
            page_count = 0
            stop_collecting = False
            
            for article in articles:
                news_data = self.parse_news_article(article)
                
                if news_data:
                    # 날짜 필터링
                    if news_data['timestamp'] < start_date:
                        stop_collecting = True
                        break
                    
                    self.news_data.append(news_data)
                    page_count += 1
                    collected_count += 1
            
            print(f"  ✓ 페이지 {page}에서 {page_count}개 기사 수집 (총 {collected_count}개)")
            
            # 날짜 범위를 벗어나면 중단
            if stop_collecting:
                print(f"  ✓ 목표 날짜 범위 도달. 수집 중단.")
                break
        
        print(f"\n✓ 총 {len(self.news_data)}개의 뉴스 기사를 수집했습니다.")
        
        if self.news_data:
            df = pd.DataFrame(self.news_data)
            # 시간순 정렬
            df = df.sort_values('timestamp', ascending=True)
            return df
        else:
            return pd.DataFrame()


def main():
    """메인 함수"""
    print("=" * 60)
    print("코인니스 뉴스 데이터 수집")
    print("=" * 60)
    
    # 수집 설정
    start_date = datetime(2025, 1, 1)
    max_pages = 100  # 최대 100페이지
    output_file = 'data/coinness_data.csv'
    
    # 수집기 초기화
    collector = CoinnessCollector()
    
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
        print(f"   코인니스 웹사이트 구조가 변경되었을 수 있습니다.")
        print(f"   HTML 구조를 확인하고 스크립트를 업데이트해주세요.")


if __name__ == '__main__':
    main()

