"""
종합 점수 계산 시스템

텔레그램, 뉴스, 트위터 데이터를 통합하여 종합 시장 신호 점수 계산
"""

import pandas as pd
import numpy as np
from datetime import timedelta


class CompositeScoreCalculator:
    """종합 점수 계산기"""
    
    def __init__(self, weights=None):
        """
        Args:
            weights: 각 데이터 소스의 가중치 딕셔너리
                    기본값: {'telegram': 0.3, 'news': 0.4, 'twitter': 0.3}
        """
        self.weights = weights or {
            'telegram': 0.3,
            'news': 0.4,
            'twitter': 0.3
        }
    
    def normalize_score(self, value, min_val, max_val):
        """0-1 사이로 정규화"""
        # Series 처리
        if isinstance(max_val, pd.Series):
            result = (value - min_val) / (max_val - min_val + 1e-10)  # 0으로 나누기 방지
            return result.fillna(0.5).clip(0, 1)
        
        # 스칼라 처리
        if max_val == min_val:
            return 0.5
        return np.clip((value - min_val) / (max_val - min_val), 0, 1)
    
    def calculate_telegram_score(self, df, window_hours=24):
        """
        텔레그램 신호 점수 계산
        
        Args:
            df: 전처리된 데이터프레임
            window_hours: 평가 윈도우 (시간)
            
        Returns:
            Series: 텔레그램 점수 (0-100)
        """
        if 'message_count' not in df.columns:
            return pd.Series(50, index=df.index)  # 중립
        
        # 1. 메시지 수 정규화
        msg_rolling = df['message_count'].rolling(window=window_hours, min_periods=1).mean()
        msg_score = self.normalize_score(
            df['message_count'], 
            msg_rolling - msg_rolling.std(), 
            msg_rolling + msg_rolling.std()
        )
        
        # 2. 감정 점수 (있으면)
        if 'avg_sentiment' in df.columns:
            sentiment_score = (df['avg_sentiment'] + 1) / 2  # -1~1 -> 0~1
        else:
            sentiment_score = 0.5
        
        # 3. 변화율
        msg_change = df['message_count'].pct_change().fillna(0)
        change_score = np.clip((msg_change + 1) / 2, 0, 1)
        
        # 종합 (0-100)
        telegram_score = (msg_score * 0.4 + sentiment_score * 0.4 + change_score * 0.2) * 100
        
        return telegram_score.fillna(50)
    
    def calculate_news_score(self, df_news, df_main):
        """
        뉴스 신호 점수 계산
        
        Args:
            df_news: 코인니스 뉴스 데이터
            df_main: 메인 데이터프레임 (시간 인덱스)
            
        Returns:
            Series: 뉴스 점수 (0-100)
        """
        if df_news.empty:
            return pd.Series(50, index=df_main.index)
        
        # 시간당 뉴스 수 집계
        df_news['hour'] = df_news['timestamp'].dt.floor('H')
        news_count = df_news.groupby('hour').size().reset_index(name='news_count')
        
        # 메인 데이터와 병합
        df_temp = df_main[['timestamp']].copy()
        df_temp['hour'] = df_temp['timestamp'].dt.floor('H')
        df_temp = df_temp.merge(news_count, on='hour', how='left')
        df_temp['news_count'] = df_temp['news_count'].fillna(0)
        
        # 정규화
        rolling_mean = df_temp['news_count'].rolling(window=24, min_periods=1).mean()
        rolling_std = df_temp['news_count'].rolling(window=24, min_periods=1).std()
        
        news_score = self.normalize_score(
            df_temp['news_count'],
            rolling_mean - rolling_std,
            rolling_mean + rolling_std
        )
        
        return (news_score * 100).fillna(50)
    
    def calculate_twitter_score(self, df_twitter, df_main):
        """
        트위터 신호 점수 계산
        
        Args:
            df_twitter: 트위터 데이터
            df_main: 메인 데이터프레임
            
        Returns:
            Series: 트위터 점수 (0-100)
        """
        if df_twitter.empty or 'post_date' not in df_twitter.columns:
            return pd.Series(50, index=df_main.index)
        
        # 시간당 트윗 수 집계
        df_twitter['hour'] = df_twitter['post_date'].dt.floor('H')
        twitter_agg = df_twitter.groupby('hour').agg({
            'likes': 'sum',
            'sentiment_score': 'mean'
        }).reset_index()
        
        # 메인 데이터와 병합
        df_temp = df_main[['timestamp']].copy()
        df_temp['hour'] = df_temp['timestamp'].dt.floor('H')
        df_temp = df_temp.merge(twitter_agg, on='hour', how='left')
        df_temp['likes'] = df_temp['likes'].fillna(0)
        df_temp['sentiment_score'] = df_temp['sentiment_score'].fillna(0)
        
        # 정규화
        likes_rolling = df_temp['likes'].rolling(window=24, min_periods=1).mean()
        likes_score = self.normalize_score(
            df_temp['likes'],
            likes_rolling - likes_rolling.std(),
            likes_rolling + likes_rolling.std()
        )
        
        sentiment_score = (df_temp['sentiment_score'] + 1) / 2  # -1~1 -> 0~1
        
        twitter_score = (likes_score * 0.5 + sentiment_score * 0.5) * 100
        
        return twitter_score.fillna(50)
    
    def calculate_composite_score(self, df, df_news=None, df_twitter=None):
        """
        종합 점수 계산
        
        Args:
            df: 메인 전처리 데이터
            df_news: 코인니스 뉴스 데이터
            df_twitter: 트위터 데이터
            
        Returns:
            DataFrame: 종합 점수가 추가된 데이터
        """
        df_result = df.copy()
        
        # None을 빈 DataFrame으로 변환
        if df_news is None or (isinstance(df_news, pd.DataFrame) and df_news.empty):
            df_news = pd.DataFrame()
        if df_twitter is None or (isinstance(df_twitter, pd.DataFrame) and df_twitter.empty):
            df_twitter = pd.DataFrame()
        
        # 각 소스별 점수 계산
        telegram_score = self.calculate_telegram_score(df_result)
        news_score = self.calculate_news_score(df_news, df_result)
        twitter_score = self.calculate_twitter_score(df_twitter, df_result)
        
        # 종합 점수 (가중 평균)
        composite_score = (
            telegram_score * self.weights['telegram'] +
            news_score * self.weights['news'] +
            twitter_score * self.weights['twitter']
        )
        
        # 신호 레벨 결정
        def get_signal_level(score):
            if score >= 75:
                return 'strong_bullish'
            elif score >= 60:
                return 'bullish'
            elif score >= 40:
                return 'neutral'
            elif score >= 25:
                return 'bearish'
            else:
                return 'strong_bearish'
        
        # 결과 추가
        df_result['telegram_score'] = telegram_score
        df_result['news_score'] = news_score
        df_result['twitter_score'] = twitter_score
        df_result['composite_score'] = composite_score
        df_result['signal_level'] = composite_score.apply(get_signal_level)
        
        return df_result
    
    def get_signal_summary(self, df, recent_hours=24):
        """
        최근 신호 요약
        
        Args:
            df: 종합 점수가 계산된 데이터
            recent_hours: 최근 몇 시간
            
        Returns:
            dict: 신호 요약
        """
        if df.empty or 'composite_score' not in df.columns:
            return {
                'current_score': 50,
                'current_level': 'neutral',
                'trend': 'neutral',
                'avg_24h': 50
            }
        
        recent_df = df.tail(recent_hours)
        
        current_score = df['composite_score'].iloc[-1]
        
        # signal_level이 없으면 계산
        if 'signal_level' not in df.columns:
            if current_score >= 75:
                current_level = 'strong_bullish'
            elif current_score >= 60:
                current_level = 'bullish'
            elif current_score >= 40:
                current_level = 'neutral'
            elif current_score >= 25:
                current_level = 'bearish'
            else:
                current_level = 'strong_bearish'
        else:
            current_level = df['signal_level'].iloc[-1]
        
        avg_24h = recent_df['composite_score'].mean()
        
        # 트렌드 계산 (최근 24시간)
        if len(recent_df) > 1:
            trend_slope = (recent_df['composite_score'].iloc[-1] - 
                          recent_df['composite_score'].iloc[0])
            if trend_slope > 5:
                trend = 'bullish'
            elif trend_slope < -5:
                trend = 'bearish'
            else:
                trend = 'neutral'
        else:
            trend = 'neutral'
        
        # 기여도 계산 (안전하게)
        telegram_contrib = df['telegram_score'].iloc[-1] * self.weights['telegram'] if 'telegram_score' in df.columns else 0
        news_contrib = df['news_score'].iloc[-1] * self.weights['news'] if 'news_score' in df.columns else 0
        twitter_contrib = df['twitter_score'].iloc[-1] * self.weights['twitter'] if 'twitter_score' in df.columns else 0
        
        return {
            'current_score': current_score,
            'current_level': current_level,
            'trend': trend,
            'avg_24h': avg_24h,
            'telegram_contribution': telegram_contrib,
            'news_contribution': news_contrib,
            'twitter_contribution': twitter_contrib
        }


if __name__ == '__main__':
    # 테스트
    print("=== 종합 점수 계산 시스템 ===")
    print("가중치: 텔레그램 30%, 뉴스 40%, 트위터 30%")

