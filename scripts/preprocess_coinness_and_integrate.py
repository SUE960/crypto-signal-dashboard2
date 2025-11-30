"""
코인뉴스(Coinness) 데이터 전처리 및 통합 분석

뉴스 데이터를 시간별로 집계하고 감정 분석 후
기존 다중 소스 데이터(텔레그램, 고래, 트위터, 가격)와 통합
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class CoinnessPreprocessor:
    """코인뉴스 데이터 전처리 클래스"""
    
    def __init__(self, news_path):
        """
        Args:
            news_path: 코인뉴스 CSV 경로
        """
        print("=" * 80)
        print("코인뉴스 데이터 전처리 시작")
        print("=" * 80)
        
        self.news_df = pd.read_csv(news_path)
        print(f"\n✓ 원본 데이터 로드: {len(self.news_df)} rows")
        
    def preprocess_news(self):
        """뉴스 데이터 전처리"""
        print("\n데이터 전처리 중...")
        
        df = self.news_df.copy()
        
        # 타임스탬프 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 중복 제거 (동일 시간 + 동일 제목)
        original_len = len(df)
        df = df.drop_duplicates(subset=['timestamp', 'title'], keep='first')
        print(f"  - 중복 제거: {original_len} → {len(df)} ({original_len - len(df)}개 제거)")
        
        # 결측치 처리
        df['content'] = df['content'].fillna('')
        df['title'] = df['title'].fillna('')
        
        # 감정 점수 결측치 처리 (0으로)
        sentiment_cols = ['sentiment_compound', 'sentiment_positive', 
                         'sentiment_negative', 'sentiment_neutral']
        for col in sentiment_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # 텍스트 길이 계산
        df['title_length'] = df['title'].str.len()
        df['content_length'] = df['content'].str.len()
        
        # 키워드 추출 (간단한 버전)
        df['has_bitcoin'] = df['title'].str.contains('비트코인|BTC|bitcoin', case=False, na=False)
        df['has_ethereum'] = df['title'].str.contains('이더리움|ETH|ethereum', case=False, na=False)
        df['has_altcoin'] = df['title'].str.contains('알트코인|altcoin|리플|XRP|도지|DOGE|에이다|ADA', case=False, na=False)
        df['has_regulation'] = df['title'].str.contains('규제|법|정부|SEC|금융당국', case=False, na=False)
        df['has_whale'] = df['title'].str.contains('고래|대규모|매집', case=False, na=False)
        df['has_bullish'] = df['title'].str.contains('급등|상승|폭등|강세|불장|랠리', case=False, na=False)
        df['has_bearish'] = df['title'].str.contains('급락|하락|폭락|약세|약세장', case=False, na=False)
        
        print(f"✓ 전처리 완료")
        print(f"  - 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        print(f"  - 비트코인 언급: {df['has_bitcoin'].sum()}건")
        print(f"  - 이더리움 언급: {df['has_ethereum'].sum()}건")
        print(f"  - 강세 뉴스: {df['has_bullish'].sum()}건")
        print(f"  - 약세 뉴스: {df['has_bearish'].sum()}건")
        
        self.news_df = df
        return df
    
    def aggregate_hourly(self):
        """시간별로 뉴스 데이터 집계"""
        print("\n시간별 집계 중...")
        
        df = self.news_df.copy()
        
        # 시간 단위로 반올림
        df['hour'] = df['timestamp'].dt.floor('H')
        
        # 시간별 집계
        hourly = df.groupby('hour').agg({
            'title': 'count',  # 뉴스 개수
            'sentiment_compound': 'mean',  # 평균 감정 점수
            'sentiment_positive': 'mean',
            'sentiment_negative': 'mean',
            'sentiment_neutral': 'mean',
            'title_length': 'mean',
            'content_length': 'mean',
            'has_bitcoin': 'sum',
            'has_ethereum': 'sum',
            'has_altcoin': 'sum',
            'has_regulation': 'sum',
            'has_whale': 'sum',
            'has_bullish': 'sum',
            'has_bearish': 'sum',
        }).reset_index()
        
        # 컬럼명 변경
        hourly.columns = [
            'timestamp',
            'news_count',
            'news_sentiment_avg',
            'news_positive_avg',
            'news_negative_avg',
            'news_neutral_avg',
            'news_title_length',
            'news_content_length',
            'news_bitcoin_mentions',
            'news_ethereum_mentions',
            'news_altcoin_mentions',
            'news_regulation_mentions',
            'news_whale_mentions',
            'news_bullish_count',
            'news_bearish_count',
        ]
        
        # 감정 비율 계산
        hourly['news_bullish_ratio'] = hourly['news_bullish_count'] / (hourly['news_count'] + 1e-10)
        hourly['news_bearish_ratio'] = hourly['news_bearish_count'] / (hourly['news_count'] + 1e-10)
        
        print(f"✓ 집계 완료: {len(hourly)} 시간")
        print(f"  - 시간당 평균 뉴스: {hourly['news_count'].mean():.2f}건")
        print(f"  - 평균 감정 점수: {hourly['news_sentiment_avg'].mean():.4f}")
        
        self.hourly_df = hourly
        return hourly
    
    def save_preprocessed(self, output_path):
        """전처리된 데이터 저장"""
        # 원본 (전처리됨)
        news_output = output_path.replace('.csv', '_preprocessed.csv')
        self.news_df.to_csv(news_output, index=False)
        print(f"\n✓ 전처리된 뉴스 데이터 저장: {news_output}")
        
        # 시간별 집계
        hourly_output = output_path.replace('.csv', '_hourly.csv')
        self.hourly_df.to_csv(hourly_output, index=False)
        print(f"✓ 시간별 집계 데이터 저장: {hourly_output}")
        
        return news_output, hourly_output


class MultiSourceWithNewsIntegrator:
    """뉴스 데이터를 기존 다중 소스에 통합"""
    
    def __init__(self):
        """데이터 경로 설정"""
        self.base_path = '/Volumes/T7/class/2025-FALL/big_data/data'
        
        print("\n" + "=" * 80)
        print("다중 소스 + 뉴스 데이터 통합")
        print("=" * 80)
    
    def load_existing_data(self):
        """기존 통합 데이터 (가격 포함) 로드"""
        print("\n기존 데이터 로딩 중...")
        
        # 가격 포함 다중 소스 데이터
        df = pd.read_csv(f'{self.base_path}/multi_source_with_price.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"✓ 기존 통합 데이터: {len(df)} rows")
        print(f"  컬럼 수: {len(df.columns)}")
        
        return df
    
    def merge_with_news(self, existing_df, news_hourly_df):
        """뉴스 데이터 병합"""
        print("\n뉴스 데이터 병합 중...")
        
        # 타임스탬프 형식 통일
        news_hourly_df['timestamp'] = pd.to_datetime(news_hourly_df['timestamp'])
        
        # 병합 (left join - 기존 데이터 기준)
        merged = existing_df.merge(news_hourly_df, on='timestamp', how='left')
        
        # 뉴스가 없는 시간대는 0으로 채움
        news_cols = [col for col in merged.columns if col.startswith('news_')]
        merged[news_cols] = merged[news_cols].fillna(0)
        
        print(f"✓ 병합 완료: {len(merged)} rows, {len(merged.columns)} columns")
        print(f"  뉴스 데이터가 있는 시간: {(merged['news_count'] > 0).sum()} ({(merged['news_count'] > 0).sum() / len(merged) * 100:.1f}%)")
        
        return merged
    
    def calculate_combined_metrics(self, df):
        """통합 지표 계산"""
        print("\n통합 지표 계산 중...")
        
        # 1. 종합 감정 지수 (가중 평균)
        # 텔레그램, 트위터, 뉴스의 감정을 가중 평균
        sentiment_cols = []
        weights = []
        
        if 'telegram_avg_sentiment' in df.columns:
            sentiment_cols.append('telegram_avg_sentiment')
            weights.append(0.2)
        
        if 'twitter_sentiment' in df.columns:
            sentiment_cols.append('twitter_sentiment')
            weights.append(0.3)
        
        if 'news_sentiment_avg' in df.columns:
            sentiment_cols.append('news_sentiment_avg')
            weights.append(0.5)  # 뉴스 감정에 가장 높은 가중치
        
        if sentiment_cols:
            # 각 감정 점수를 정규화 (-1 ~ 1)
            df['combined_sentiment'] = 0
            total_weight = sum(weights)
            
            for col, weight in zip(sentiment_cols, weights):
                # 결측치는 0으로
                normalized = df[col].fillna(0)
                df['combined_sentiment'] += normalized * (weight / total_weight)
        
        # 2. 종합 활동 지수
        # 모든 소스의 활동을 Z-score로 정규화 후 합산
        activity_cols = [
            ('telegram_message_count', 0.2),
            ('whale_tx_count', 0.3),
            ('twitter_engagement', 0.2),
            ('news_count', 0.3)
        ]
        
        df['combined_activity'] = 0
        
        for col, weight in activity_cols:
            if col in df.columns:
                # Z-score 정규화
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    zscore = (df[col] - mean) / std
                    df['combined_activity'] += zscore * weight
        
        # 3. 시장 온도 지수 (0~100)
        # 강세 뉴스, 감정, 가격 변화, 활동을 종합
        market_components = []
        
        if 'news_bullish_ratio' in df.columns:
            market_components.append(df['news_bullish_ratio'] * 40)  # 40% 가중치
        
        if 'combined_sentiment' in df.columns:
            # -1~1을 0~30으로 변환
            market_components.append((df['combined_sentiment'] + 1) * 15)  # 30% 가중치
        
        if 'btc_price_change' in df.columns:
            # -10~10%를 0~30으로 변환 (클리핑)
            price_norm = df['btc_price_change'].clip(-10, 10)
            market_components.append((price_norm + 10) * 1.5)  # 30% 가중치
        
        if market_components:
            df['market_temperature'] = sum(market_components)
            df['market_temperature'] = df['market_temperature'].clip(0, 100)
        
        print(f"✓ 통합 지표 생성:")
        if 'combined_sentiment' in df.columns:
            print(f"  - 종합 감정: {df['combined_sentiment'].mean():.4f} (범위: {df['combined_sentiment'].min():.2f} ~ {df['combined_sentiment'].max():.2f})")
        if 'combined_activity' in df.columns:
            print(f"  - 종합 활동: {df['combined_activity'].mean():.4f}")
        if 'market_temperature' in df.columns:
            print(f"  - 시장 온도: {df['market_temperature'].mean():.2f} (0~100)")
        
        return df
    
    def generate_alerts_with_news(self, df):
        """뉴스 기반 추가 알람 생성"""
        print("\n뉴스 기반 알람 생성 중...")
        
        alerts = []
        
        for idx, row in df.iterrows():
            alert_reasons = []
            priority = 0
            
            # 뉴스 급증 (시간당 10건 이상)
            if row.get('news_count', 0) >= 10:
                priority += 2
                alert_reasons.append(f"뉴스 급증 ({row['news_count']:.0f}건)")
            
            # 강세 뉴스 집중 (70% 이상)
            if row.get('news_bullish_ratio', 0) >= 0.7 and row.get('news_count', 0) >= 3:
                priority += 3
                alert_reasons.append(f"강세 뉴스 집중 ({row['news_bullish_ratio']*100:.0f}%)")
            
            # 약세 뉴스 집중 (70% 이상)
            if row.get('news_bearish_ratio', 0) >= 0.7 and row.get('news_count', 0) >= 3:
                priority += 3
                alert_reasons.append(f"약세 뉴스 집중 ({row['news_bearish_ratio']*100:.0f}%)")
            
            # 규제 뉴스 (3건 이상)
            if row.get('news_regulation_mentions', 0) >= 3:
                priority += 4
                alert_reasons.append(f"규제 관련 뉴스 ({row['news_regulation_mentions']:.0f}건)")
            
            # 뉴스 + 고래 거래 동시 급증
            news_spike = row.get('news_count', 0) >= 8
            whale_spike = row.get('whale_tx_count', 0) > df['whale_tx_count'].quantile(0.95)
            
            if news_spike and whale_spike:
                priority += 5
                alert_reasons.append("⚠️ 뉴스+고래 동시 급증")
            
            # 뉴스 + 가격 급변
            if row.get('news_count', 0) >= 8 and abs(row.get('btc_price_change', 0)) >= 2:
                priority += 4
                alert_reasons.append(f"뉴스+가격급변 (BTC {row['btc_price_change']:.1f}%)")
            
            if priority >= 4:  # 중요도 4 이상만 알람
                level = 'CRITICAL' if priority >= 10 else 'HIGH' if priority >= 6 else 'MEDIUM'
                
                alerts.append({
                    'timestamp': row['timestamp'],
                    'alert_level': level,
                    'priority_score': priority,
                    'reasons': '; '.join(alert_reasons),
                    'news_count': row.get('news_count', 0),
                    'news_sentiment': row.get('news_sentiment_avg', 0),
                    'news_bullish_ratio': row.get('news_bullish_ratio', 0),
                    'btc_price': row.get('btc_close', 0),
                    'btc_change': row.get('btc_price_change', 0),
                })
        
        alerts_df = pd.DataFrame(alerts)
        
        if not alerts_df.empty:
            print(f"✓ {len(alerts_df)}개 알람 생성")
            level_counts = alerts_df['alert_level'].value_counts()
            for level, count in level_counts.items():
                print(f"  - {level}: {count}개")
        else:
            print("⚠ 생성된 알람 없음")
        
        return alerts_df
    
    def save_integrated_data(self, df, alerts_df):
        """통합 데이터 저장"""
        print("\n" + "=" * 80)
        print("결과 저장")
        print("=" * 80)
        
        # 최종 통합 데이터
        output_path = f'{self.base_path}/final_integrated_data.csv'
        df.to_csv(output_path, index=False)
        print(f"✓ 최종 통합 데이터: {output_path}")
        print(f"  - {len(df)} rows × {len(df.columns)} columns")
        
        # 뉴스 기반 알람
        if not alerts_df.empty:
            alerts_path = f'{self.base_path}/news_based_alerts.csv'
            alerts_df.to_csv(alerts_path, index=False)
            print(f"✓ 뉴스 기반 알람: {alerts_path}")
            print(f"  - {len(alerts_df)} alerts")
        
        # 대시보드용 요약 통계
        summary = {
            'total_rows': len(df),
            'date_range': f"{df['timestamp'].min()} ~ {df['timestamp'].max()}",
            'total_news': df['news_count'].sum(),
            'avg_news_per_hour': df['news_count'].mean(),
            'avg_sentiment': df.get('combined_sentiment', pd.Series([0])).mean(),
            'avg_market_temp': df.get('market_temperature', pd.Series([0])).mean(),
            'total_alerts': len(alerts_df) if not alerts_df.empty else 0,
        }
        
        summary_path = f'{self.base_path}/dashboard_summary.json'
        import json
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ 대시보드 요약: {summary_path}")
        
        return output_path


if __name__ == '__main__':
    # 1. 뉴스 데이터 전처리
    print("\n[STEP 1] 코인뉴스 데이터 전처리")
    print("=" * 80)
    
    news_path = '/Volumes/T7/class/2025-FALL/big_data/data/coinness_data2.csv'
    preprocessor = CoinnessPreprocessor(news_path)
    
    # 전처리
    preprocessor.preprocess_news()
    
    # 시간별 집계
    news_hourly = preprocessor.aggregate_hourly()
    
    # 저장
    preprocessor.save_preprocessed(news_path)
    
    # 2. 기존 데이터와 통합
    print("\n\n[STEP 2] 다중 소스 데이터와 통합")
    print("=" * 80)
    
    integrator = MultiSourceWithNewsIntegrator()
    
    # 기존 데이터 로드
    existing_df = integrator.load_existing_data()
    
    # 뉴스 데이터 병합
    integrated_df = integrator.merge_with_news(existing_df, news_hourly)
    
    # 통합 지표 계산
    integrated_df = integrator.calculate_combined_metrics(integrated_df)
    
    # 뉴스 기반 알람 생성
    news_alerts = integrator.generate_alerts_with_news(integrated_df)
    
    # 저장
    final_path = integrator.save_integrated_data(integrated_df, news_alerts)
    
    print("\n" + "=" * 80)
    print("전처리 및 통합 완료! 🎉")
    print("=" * 80)
    print(f"\n대시보드에서 사용할 파일:")
    print(f"  1. 최종 통합 데이터: final_integrated_data.csv")
    print(f"  2. 뉴스 기반 알람: news_based_alerts.csv")
    print(f"  3. 대시보드 요약: dashboard_summary.json")
    print(f"\n이제 Streamlit 대시보드를 업데이트하세요!")

