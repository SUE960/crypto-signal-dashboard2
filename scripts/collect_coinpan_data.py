"""
코인판(Coinpan) 데이터 수집 스크립트

코인판 커뮤니티에서 게시글 데이터를 수집합니다.
- 게시글 수 (시간당)
- 댓글 수
- 조회수
- 추천/비추천 수
- 감정 분석
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import random

# 감정 분석기 초기화
sentiment_analyzer = SentimentIntensityAnalyzer()


class CoinpanScraper:
    """코인판 데이터 수집기 (Rate Limiting 우회)"""
    
    def __init__(self):
        """초기화"""
        self.base_url = "https://www.coinpan.com"
        
        # User-Agent 로테이션 (다양한 브라우저로 위장)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # 세션 사용 (쿠키 유지)
        self.session = requests.Session()
        
    def _get_headers(self):
        """랜덤 헤더 생성"""
        return {
            'User-Agent': random.choice(self.user_agents),
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
        
    def get_board_posts(self, board='free', pages=50):
        """
        게시판의 게시글 목록 가져오기 (Rate Limiting 우회)
        
        Args:
            board: 게시판 이름 (free, coin, humor 등)
            pages: 가져올 페이지 수
            
        Returns:
            list: 게시글 정보 리스트
        """
        posts = []
        retry_count = 0
        max_retries = 3
        
        print(f"코인판 {board} 게시판에서 {pages}페이지 수집 중...")
        
        for page in range(1, pages + 1):
            success = False
            
            for attempt in range(max_retries):
                try:
                    # 랜덤 지연 시간 (1~3초)
                    delay = random.uniform(1.5, 3.5)
                    time.sleep(delay)
                    
                    # URL 구성
                    url = f"{self.base_url}/{board}?page={page}"
                    
                    # 랜덤 헤더 사용
                    headers = self._get_headers()
                    
                    # 요청
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    # 성공
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # 게시글 목록 파싱 (코인판 실제 구조)
                        # <tbody> 안의 <tr> 중 공지가 아닌 것들
                        tbody = soup.find('tbody')
                        if tbody:
                            # bg1, bg2 클래스를 가진 tr (일반 게시글)
                            articles = tbody.find_all('tr', class_=['bg1', 'bg2'])
                        else:
                            articles = []
                        
                        for article in articles:
                            try:
                                post_data = self._parse_post(article, board)
                                if post_data:
                                    posts.append(post_data)
                            except Exception as e:
                                continue
                        
                        print(f"  ✓ 페이지 {page}/{pages} 완료 (총 {len(posts)}개 게시글)")
                        success = True
                        break
                    
                    # Rate Limiting (429)
                    elif response.status_code == 429:
                        wait_time = (attempt + 1) * 10  # 10초, 20초, 30초
                        print(f"  ⚠ Rate Limit 감지. {wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    
                    # 기타 에러
                    else:
                        print(f"  ✗ 페이지 {page} 요청 실패: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue
                        break
                        
                except Exception as e:
                    print(f"  ✗ 페이지 {page} 처리 중 오류: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    break
            
            if not success:
                retry_count += 1
                # 연속 실패가 5번 이상이면 중단
                if retry_count >= 5:
                    print(f"\n연속 실패 {retry_count}회. 수집을 중단합니다.")
                    break
            else:
                retry_count = 0  # 성공하면 리셋
        
        print(f"총 {len(posts)}개 게시글 수집 완료\n")
        return posts
    
    def _parse_post(self, article, board):
        """
        개별 게시글 파싱 (코인판 실제 HTML 구조)
        
        Args:
            article: BeautifulSoup 객체 (<tr> 태그)
            board: 게시판 이름
            
        Returns:
            dict: 게시글 정보
        """
        try:
            # 제목: <td class="title"> 안의 <a> 태그
            title_td = article.find('td', class_='title')
            if not title_td:
                return None
            
            title_link = title_td.find('a')
            title = title_link.text.strip() if title_link else "제목없음"
            
            # 댓글 수: 제목 옆의 #comment 링크
            comment_link = title_td.find('a', href=re.compile(r'#comment'))
            if comment_link:
                comment_num = comment_link.find('span', class_='number')
                comments = int(comment_num.text.strip()) if comment_num else 0
            else:
                comments = 0
            
            # 작성 시간: <td class="time"> 안의 <span class="number">
            time_td = article.find('td', class_='time')
            if time_td:
                # regdateHour (오늘) 또는 날짜
                time_hour = time_td.find('span', class_='regdateHour')
                if time_hour:
                    time_str = time_hour.text.strip()  # "13:24"
                else:
                    time_num = time_td.find('span', class_='number')
                    time_str = time_num.text.strip() if time_num else ""
            else:
                time_str = ""
            
            # 조회수: <td class="readed"> 안의 <span class="number">
            view_td = article.find('td', class_='readed')
            if view_td:
                view_num = view_td.find('span', class_='number')
                views = int(view_num.text.strip()) if view_num else 0
            else:
                views = 0
            
            # 추천: <td class="voted"> 안의 <span class="number"> (예: "0 - 0")
            voted_td = article.find('td', class_='voted')
            if voted_td:
                voted_num = voted_td.find('span', class_='number')
                if voted_num:
                    voted_text = voted_num.text.strip()  # "0 - 0"
                    # 첫 번째 숫자만 추출 (추천 수)
                    likes_match = re.search(r'(\d+)\s*-', voted_text)
                    likes = int(likes_match.group(1)) if likes_match else 0
                else:
                    likes = 0
            else:
                likes = 0
            
            # 시간 파싱
            post_time = self._parse_time(time_str)
            
            # 감정 분석
            sentiment_score = sentiment_analyzer.polarity_scores(title)
            
            return {
                'timestamp': post_time,
                'board': board,
                'title': title,
                'views': views,
                'comments': comments,
                'likes': likes,
                'sentiment_compound': sentiment_score['compound'],
                'sentiment_positive': sentiment_score['pos'],
                'sentiment_negative': sentiment_score['neg'],
                'sentiment_neutral': sentiment_score['neu']
            }
            
        except Exception as e:
            # 디버깅용
            # print(f"    파싱 오류: {e}")
            return None
    
    def _parse_time(self, time_str):
        """
        시간 문자열을 datetime으로 변환 (코인판 형식)
        
        Args:
            time_str: 시간 문자열 (예: "13:24", "2025.07.01")
            
        Returns:
            datetime: 변환된 시간
        """
        now = datetime.now()
        
        try:
            # "HH:MM" 형태 (오늘)
            if ':' in time_str and len(time_str) <= 5:
                hour, minute = map(int, time_str.split(':'))
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # "YYYY.MM.DD" 형태
            elif '.' in time_str:
                parts = time_str.split('.')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    # 시간은 12:00으로 가정
                    return datetime(year, month, day, 12, 0, 0)
                elif len(parts) == 2:  # MM.DD
                    month, day = map(int, parts)
                    return datetime(now.year, month, day, 12, 0, 0)
            
            # "X분전" 형태
            elif '분전' in time_str or '분 전' in time_str:
                minutes = int(re.search(r'\d+', time_str).group())
                return now - timedelta(minutes=minutes)
            
            # "X시간전" 형태
            elif '시간전' in time_str or '시간 전' in time_str:
                hours = int(re.search(r'\d+', time_str).group())
                return now - timedelta(hours=hours)
            
            # "YYYY-MM-DD" 형태
            elif '-' in time_str:
                if len(time_str.split('-')) == 2:  # MM-DD
                    month, day = map(int, time_str.split('-'))
                    return datetime(now.year, month, day, 12, 0, 0)
                else:  # YYYY-MM-DD
                    return datetime.strptime(time_str, '%Y-%m-%d')
            
            # 파싱 실패 시 현재 시간
            else:
                return now
                
        except Exception as e:
            return now
    
    def aggregate_hourly(self, posts_df):
        """
        게시글 데이터를 시간당 집계
        
        Args:
            posts_df: 게시글 데이터프레임
            
        Returns:
            DataFrame: 시간당 집계 데이터
        """
        if posts_df.empty:
            return pd.DataFrame()
        
        # 시간 단위로 내림
        posts_df['hour'] = posts_df['timestamp'].dt.floor('H')
        
        # 시간별 집계
        hourly_data = posts_df.groupby('hour').agg({
            'title': 'count',  # 게시글 수
            'views': 'sum',  # 총 조회수
            'comments': 'sum',  # 총 댓글 수
            'likes': 'sum',  # 총 추천 수
            'sentiment_compound': 'mean',  # 평균 감정 점수
            'sentiment_positive': 'mean',
            'sentiment_negative': 'mean',
            'sentiment_neutral': 'mean'
        }).reset_index()
        
        # 컬럼명 변경
        hourly_data.columns = [
            'timestamp', 'message_count', 'total_views', 'total_comments',
            'total_reactions', 'avg_sentiment', 'avg_positive',
            'avg_negative', 'avg_neutral'
        ]
        
        # 추가 계산
        hourly_data['avg_views'] = hourly_data['total_views'] / hourly_data['message_count']
        hourly_data['total_forwards'] = 0  # 코인판은 전달 기능이 없으므로 0
        
        # 컬럼 순서 조정 (텔레그램 데이터와 동일하게)
        hourly_data = hourly_data[[
            'timestamp', 'message_count', 'avg_views', 'total_forwards',
            'total_reactions', 'avg_sentiment', 'avg_positive',
            'avg_negative', 'avg_neutral'
        ]]
        
        return hourly_data
    
    def run(self, boards=['free', 'coin'], pages_per_board=50, output_file=None):
        """
        데이터 수집 실행
        
        Args:
            boards: 수집할 게시판 리스트
            pages_per_board: 게시판당 수집할 페이지 수
            output_file: 출력 파일 경로
        """
        print("=== 코인판 데이터 수집 시작 ===\n")
        
        all_posts = []
        
        # 각 게시판에서 데이터 수집
        for board in boards:
            posts = self.get_board_posts(board, pages=pages_per_board)
            all_posts.extend(posts)
        
        if not all_posts:
            print("수집된 데이터가 없습니다.")
            return
        
        # DataFrame 생성
        posts_df = pd.DataFrame(all_posts)
        
        print(f"총 {len(posts_df)}개의 게시글 수집 완료")
        print(f"기간: {posts_df['timestamp'].min()} ~ {posts_df['timestamp'].max()}\n")
        
        # 시간당 집계
        print("시간당 집계 중...")
        hourly_data = self.aggregate_hourly(posts_df)
        
        if hourly_data.empty:
            print("집계 데이터가 없습니다.")
            return
        
        # 저장
        if output_file is None:
            output_file = '/Volumes/T7/class/2025-FALL/big_data/data/telegram_data.csv'
        
        hourly_data.to_csv(output_file, index=False)
        print(f"\n데이터가 {output_file}에 저장되었습니다.")
        print(f"총 {len(hourly_data)} 시간의 집계 데이터")
        
        # 통계 출력
        print("\n=== 수집 통계 ===")
        print(f"총 게시글 수: {posts_df['title'].count()}")
        print(f"총 조회수: {posts_df['views'].sum():,}")
        print(f"총 댓글 수: {posts_df['comments'].sum():,}")
        print(f"총 추천 수: {posts_df['likes'].sum():,}")
        print(f"평균 감정 점수: {posts_df['sentiment_compound'].mean():.3f}")
        
        return hourly_data


def main():
    """메인 함수"""
    print("코인판 데이터 수집 스크립트\n")
    
    # 스크래퍼 초기화
    scraper = CoinpanScraper()
    
    # 데이터 수집 실행
    # 자유게시판과 코인게시판에서 각각 50페이지씩 수집
    scraper.run(
        boards=['free', 'coin'],
        pages_per_board=50,
        output_file='/Volumes/T7/class/2025-FALL/big_data/data/telegram_data.csv'
    )
    
    print("\n데이터 수집이 완료되었습니다!")
    print("\n다음 단계:")
    print("1. python scripts/preprocess_data.py  # 데이터 재전처리")
    print("2. streamlit run app.py  # 대시보드 실행")


if __name__ == '__main__':
    main()

