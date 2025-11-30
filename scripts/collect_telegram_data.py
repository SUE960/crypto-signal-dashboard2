"""
텔레그램 채널 데이터 수집 스크립트

이 스크립트는 지정된 텔레그램 공개 채널에서 메시지 데이터를 수집합니다.
- 메시지 수 (시간당)
- 조회수 (views)
- 반응/이모티콘 수
- 전달 횟수 (forwards)
- 감정 분석 점수
"""

import os
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from telethon import TelegramClient
from telethon.tl.types import Message
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import pytz

# .env 파일 로드
load_dotenv()

# Telegram API 설정
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
CHANNELS = os.getenv('TELEGRAM_CHANNELS', '@Ethereum,@Bitcoin').split(',')

# 감정 분석기 초기화
sentiment_analyzer = SentimentIntensityAnalyzer()


class TelegramDataCollector:
    """텔레그램 데이터 수집기"""
    
    def __init__(self, api_id, api_hash, phone):
        """
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            phone: 전화번호
        """
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.phone = phone
        
    async def collect_channel_data(self, channel_username, start_date, end_date):
        """
        특정 채널의 데이터를 수집합니다.
        
        Args:
            channel_username: 채널 사용자명 (예: @Ethereum)
            start_date: 수집 시작 날짜
            end_date: 수집 종료 날짜
            
        Returns:
            DataFrame: 수집된 데이터
        """
        print(f"\n채널 {channel_username} 데이터 수집 중...")
        
        # 채널 엔티티 가져오기
        try:
            channel = await self.client.get_entity(channel_username)
            print(f"  ✓ 채널 찾음: {channel.title if hasattr(channel, 'title') else channel_username}")
        except Exception as e:
            print(f"  ✗ 채널 {channel_username}을 찾을 수 없습니다: {e}")
            print(f"  💡 채널명이 정확한지 확인하세요. 또는 채널이 비공개일 수 있습니다.")
            return pd.DataFrame()
        
        messages_data = []
        message_count = 0
        
        print(f"  메시지 수집 시작... (기간: {start_date.date()} ~ {end_date.date()})")
        
        # 메시지 가져오기
        try:
            async for message in self.client.iter_messages(
                channel,
                limit=None  # 제한 없음 (전체 수집)
            ):
                message_count += 1
                
                # 진행 상황 표시
                if message_count % 100 == 0:
                    print(f"    처리 중: {message_count}개 메시지... (수집: {len(messages_data)}개)")
                
                # 날짜 범위 확인 (timezone aware)
                msg_date = message.date
                
                # 너무 오래된 메시지는 건너뛰기
                if msg_date < start_date:
                    break  # 더 이상 수집 안 함
                
                # 미래 메시지는 건너뛰기 (일반적으로 없지만)
                if msg_date > end_date:
                    continue
                    
                # 메시지 처리 (텍스트가 있든 없든 모두 수집)
                if isinstance(message, Message):
                    # 텍스트 메시지가 있으면 감정 분석
                    if message.message:
                        sentiment_score = sentiment_analyzer.polarity_scores(message.message)
                        message_text = message.message
                    else:
                        # 텍스트 없는 메시지 (사진, 동영상 등)
                        sentiment_score = {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1.0}
                        message_text = ""
                    
                    # 반응 수 계산
                    reaction_count = 0
                    if hasattr(message, 'reactions') and message.reactions:
                        reaction_count = sum([r.count for r in message.reactions.results])
                    
                    messages_data.append({
                        'timestamp': msg_date,
                        'channel': channel_username,
                        'message_id': message.id,
                        'views': message.views if message.views else 0,
                        'forwards': message.forwards if message.forwards else 0,
                        'reactions': reaction_count,
                        'sentiment_compound': sentiment_score['compound'],
                        'sentiment_positive': sentiment_score['pos'],
                        'sentiment_negative': sentiment_score['neg'],
                        'sentiment_neutral': sentiment_score['neu'],
                        'message_length': len(message_text)
                    })
        
        except Exception as e:
            print(f"  ✗ 메시지 수집 중 오류: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"  ✓ 채널 {channel_username}에서 {len(messages_data)}개의 메시지를 수집했습니다.")
        
        # 채널별로 중간 저장 (데이터 손실 방지)
        if messages_data:
            temp_df = pd.DataFrame(messages_data)
            temp_file = f'data/temp_{channel_username.replace("@", "")}_data.csv'
            temp_df.to_csv(temp_file, index=False, encoding='utf-8-sig')
            print(f"  💾 중간 저장: {temp_file}")
        
        return pd.DataFrame(messages_data)
    
    async def aggregate_hourly(self, df):
        """
        메시지 데이터를 시간당 집계합니다.
        
        Args:
            df: 메시지 데이터프레임
            
        Returns:
            DataFrame: 시간당 집계 데이터
        """
        if df.empty:
            return df
        
        # 시간 단위로 내림
        df['hour'] = df['timestamp'].dt.floor('H')
        
        # 채널별, 시간별 집계
        hourly_data = df.groupby(['channel', 'hour']).agg({
            'message_id': 'count',  # 메시지 수
            'views': 'mean',  # 평균 조회수
            'forwards': 'sum',  # 총 전달 횟수
            'reactions': 'sum',  # 총 반응 수
            'sentiment_compound': 'mean',  # 평균 감정 점수
            'sentiment_positive': 'mean',
            'sentiment_negative': 'mean',
            'sentiment_neutral': 'mean',
            'message_length': 'mean'
        }).reset_index()
        
        # 컬럼명 변경
        hourly_data.columns = [
            'channel', 'timestamp', 'message_count', 'avg_views',
            'total_forwards', 'total_reactions', 'avg_sentiment',
            'avg_positive', 'avg_negative', 'avg_neutral', 'avg_msg_length'
        ]
        
        return hourly_data
    
    async def collect_all_channels(self, channels, start_date, end_date):
        """
        모든 채널의 데이터를 수집합니다.
        
        Args:
            channels: 채널 리스트
            start_date: 수집 시작 날짜
            end_date: 수집 종료 날짜
            
        Returns:
            DataFrame: 모든 채널의 집계 데이터
        """
        all_data = []
        
        for channel in channels:
            channel = channel.strip()
            # 채널 데이터 수집
            channel_df = await self.collect_channel_data(channel, start_date, end_date)
            if not channel_df.empty:
                all_data.append(channel_df)
        
        if not all_data:
            print("수집된 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 모든 채널 데이터 합치기
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 시간당 집계
        hourly_df = await self.aggregate_hourly(combined_df)
        
        return hourly_df
    
    async def run(self, channels, start_date, end_date, output_file):
        """
        데이터 수집 실행
        
        Args:
            channels: 채널 리스트
            start_date: 수집 시작 날짜
            end_date: 수집 종료 날짜
            output_file: 출력 파일 경로
        """
        await self.client.start(phone=self.phone)
        print("Telegram 클라이언트에 연결되었습니다.")
        
        # 데이터 수집
        hourly_data = await self.collect_all_channels(channels, start_date, end_date)
        
        if not hourly_data.empty:
            # CSV로 저장
            hourly_data.to_csv(output_file, index=False)
            print(f"\n데이터가 {output_file}에 저장되었습니다.")
            print(f"총 {len(hourly_data)} 행의 시간당 집계 데이터가 저장되었습니다.")
            
            # 통계 출력
            print("\n=== 수집 통계 ===")
            print(f"채널별 데이터 수:")
            print(hourly_data.groupby('channel')['message_count'].sum())
        else:
            print("수집된 데이터가 없습니다.")
        
        await self.client.disconnect()


async def main():
    """메인 함수"""
    # API 키 확인
    if not API_ID or not API_HASH or not PHONE:
        print("오류: .env 파일에 Telegram API 설정이 필요합니다.")
        print("1. https://my.telegram.org/auth 에서 API ID와 Hash를 발급받으세요.")
        print("2. .env.example을 .env로 복사하고 설정을 입력하세요.")
        return
    
    # 날짜 범위 설정 (2025년 1월 1일 ~ 현재)
    start_date = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime.now(pytz.UTC)
    
    print("📅 2025년 전체 데이터를 수집합니다. (시간이 걸릴 수 있습니다)")
    
    print("=== 텔레그램 데이터 수집 시작 ===")
    print(f"수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print(f"수집 채널: {', '.join(CHANNELS)}")
    print()
    
    # 데이터 수집기 초기화
    collector = TelegramDataCollector(API_ID, API_HASH, PHONE)
    
    # 출력 파일 경로
    output_file = '/Volumes/T7/class/2025-FALL/big_data/data/telegram_data.csv'
    
    # 데이터 수집 실행
    await collector.run(CHANNELS, start_date, end_date, output_file)
    
    print("\n데이터 수집이 완료되었습니다!")


if __name__ == '__main__':
    asyncio.run(main())

