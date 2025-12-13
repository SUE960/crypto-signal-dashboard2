"""
데이터 전처리 스크립트

모든 데이터를 통합하고 분석을 위한 파생 변수를 생성합니다.
"""

import pandas as pd
import numpy as np
import sys
import os

# 상위 디렉토리를 path에 추가
sys.path.append('/Volumes/T7/class/2025-FALL/big_data')

from utils.data_loader import DataLoader


class DataPreprocessor:
    """데이터 전처리 클래스"""
    
    def __init__(self):
        self.loader = DataLoader()
        
    def aggregate_telegram_by_hour(self, telegram_df):
        """
        텔레그램 데이터를 채널별로 집계하여 시간당 총합 계산
        
        Args:
            telegram_df: 텔레그램 데이터프레임
            
        Returns:
            DataFrame: 시간별 집계 데이터
        """
        if telegram_df.empty:
            return pd.DataFrame()
        
        # 시간 단위로 내림
        telegram_df['hour'] = telegram_df['timestamp'].dt.floor('H')
        
        # 시간별로 모든 채널 집계
        hourly = telegram_df.groupby('hour').agg({
            'message_count': 'sum',
            'avg_views': 'mean',
            'total_forwards': 'sum',
            'total_reactions': 'sum',
            'avg_sentiment': 'mean',
            'avg_positive': 'mean',
            'avg_negative': 'mean',
            'avg_neutral': 'mean'
        }).reset_index()
        
        hourly = hourly.rename(columns={'hour': 'timestamp'})
        
        return hourly
    
    def merge_all_data(self, whale_tx, eth_price, btc_price, telegram):
        """
        모든 데이터를 시간 기준으로 병합
        
        Args:
            whale_tx: 고래 거래 데이터
            eth_price: ETH 가격 데이터
            btc_price: BTC 가격 데이터
            telegram: 텔레그램 데이터
            
        Returns:
            DataFrame: 병합된 데이터
        """
        # 1. 고래 거래 데이터를 기준으로 시작
        merged = whale_tx.copy()
        
        # 2. ETH 가격 데이터 병합
        eth_cols = ['timestamp', 'ETH_open', 'ETH_high', 'ETH_low', 'ETH_close', 'ETH_volume', 'ETH_trade_count']
        eth_data = eth_price[eth_cols].copy()
        merged = merged.merge(eth_data, on='timestamp', how='left')
        
        # 3. BTC 가격 데이터 병합
        btc_cols = ['timestamp', 'BTC_open', 'BTC_high', 'BTC_low', 'BTC_close', 'BTC_volume', 'BTC_trade_count']
        btc_data = btc_price[btc_cols].copy()
        merged = merged.merge(btc_data, on='timestamp', how='left')
        
        # 4. 텔레그램 데이터 병합
        if not telegram.empty:
            telegram_agg = self.aggregate_telegram_by_hour(telegram)
            merged = merged.merge(telegram_agg, on='timestamp', how='left')
            
            # 텔레그램 데이터가 없는 시간은 0으로 채우기
            telegram_cols = ['message_count', 'avg_views', 'total_forwards', 'total_reactions',
                           'avg_sentiment', 'avg_positive', 'avg_negative', 'avg_neutral']
            for col in telegram_cols:
                if col in merged.columns:
                    merged[col] = merged[col].fillna(0)
        
        # 5. 가격 데이터 결측치 처리 (forward fill)
        price_cols = [col for col in merged.columns if 'ETH_' in col or 'BTC_' in col]
        for col in price_cols:
            merged[col] = merged[col].fillna(method='ffill')
        
        return merged
    
    def create_derived_features(self, df):
        """
        파생 변수 생성
        
        Args:
            df: 통합 데이터프레임
            
        Returns:
            DataFrame: 파생 변수가 추가된 데이터프레임
        """
        # 1. 가격 변화율 (%)
        df['ETH_price_change_pct'] = df['ETH_close'].pct_change() * 100
        df['BTC_price_change_pct'] = df['BTC_close'].pct_change() * 100
        
        # 2. 거래량 변화율 (%)
        df['ETH_volume_change_pct'] = df['ETH_volume'].pct_change() * 100
        df['BTC_volume_change_pct'] = df['BTC_volume'].pct_change() * 100
        
        # 3. 고래 거래 빈도 변화율
        df['tx_frequency_change_pct'] = df['tx_frequency'].pct_change() * 100
        df['tx_amount_change_pct'] = df['tx_amount'].pct_change() * 100
        
        # 4. 텔레그램 활동 변화율
        if 'message_count' in df.columns:
            df['message_count_change_pct'] = df['message_count'].pct_change() * 100
            df['avg_views_change_pct'] = df['avg_views'].pct_change() * 100
            df['total_reactions_change_pct'] = df['total_reactions'].pct_change() * 100
        
        # 5. 이동평균 (24시간)
        df['ETH_price_ma24'] = df['ETH_close'].rolling(window=24, min_periods=1).mean()
        df['tx_frequency_ma24'] = df['tx_frequency'].rolling(window=24, min_periods=1).mean()
        
        if 'message_count' in df.columns:
            df['message_count_ma24'] = df['message_count'].rolling(window=24, min_periods=1).mean()
        
        # 6. 이동 표준편차 (24시간) - 변동성 측정
        df['ETH_price_std24'] = df['ETH_close'].rolling(window=24, min_periods=1).std()
        df['tx_frequency_std24'] = df['tx_frequency'].rolling(window=24, min_periods=1).std()
        
        if 'message_count' in df.columns:
            df['message_count_std24'] = df['message_count'].rolling(window=24, min_periods=1).std()
        
        # 7. Z-score (이상치 탐지용)
        df['ETH_price_zscore'] = (df['ETH_close'] - df['ETH_price_ma24']) / (df['ETH_price_std24'] + 1e-10)
        df['tx_frequency_zscore'] = (df['tx_frequency'] - df['tx_frequency_ma24']) / (df['tx_frequency_std24'] + 1e-10)
        
        if 'message_count' in df.columns:
            df['message_count_zscore'] = (df['message_count'] - df['message_count_ma24']) / (df['message_count_std24'] + 1e-10)
        
        # 8. 시간 특성
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        
        # 9. 볼린저 밴드 (ETH 가격)
        df['ETH_bb_upper'] = df['ETH_price_ma24'] + (2 * df['ETH_price_std24'])
        df['ETH_bb_lower'] = df['ETH_price_ma24'] - (2 * df['ETH_price_std24'])
        
        # 10. 무한대/NaN 값 처리
        df = df.replace([np.inf, -np.inf], np.nan)
        
        return df
    
    def save_processed_data(self, df, output_path):
        """
        전처리된 데이터 저장
        
        Args:
            df: 전처리된 데이터프레임
            output_path: 출력 파일 경로
        """
        df.to_csv(output_path, index=False)
        print(f"전처리된 데이터가 {output_path}에 저장되었습니다.")
        print(f"총 {len(df)} 행, {len(df.columns)} 컬럼")
    
    def run(self, output_path='/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv'):
        """
        전체 전처리 파이프라인 실행
        
        Args:
            output_path: 출력 파일 경로
        """
        print("=== 데이터 전처리 시작 ===\n")
        
        # 1. 데이터 로드
        print("1. 데이터 로드 중...")
        data = self.loader.load_all_data()
        
        for name, df in data.items():
            if not df.empty:
                print(f"  - {name}: {len(df)} 행")
            else:
                print(f"  - {name}: 데이터 없음")
        print()
        
        # 2. 데이터 병합
        print("2. 데이터 병합 중...")
        merged_df = self.merge_all_data(
            data['whale_transactions'],
            data['eth_price'],
            data['btc_price'],
            data['telegram']
        )
        print(f"  병합 완료: {len(merged_df)} 행\n")
        
        # 3. 파생 변수 생성
        print("3. 파생 변수 생성 중...")
        processed_df = self.create_derived_features(merged_df)
        print(f"  파생 변수 생성 완료: {len(processed_df.columns)} 컬럼\n")
        
        # 4. 데이터 저장
        print("4. 데이터 저장 중...")
        self.save_processed_data(processed_df, output_path)
        
        # 5. 요약 통계
        print("\n=== 전처리 완료 ===")
        print(f"기간: {processed_df['timestamp'].min()} ~ {processed_df['timestamp'].max()}")
        print(f"총 시간: {len(processed_df)} 시간")
        
        # 결측치 확인
        null_counts = processed_df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        if len(null_cols) > 0:
            print(f"\n결측치가 있는 컬럼 ({len(null_cols)}개):")
            print(null_cols)
        else:
            print("\n결측치 없음!")
        
        return processed_df


if __name__ == '__main__':
    preprocessor = DataPreprocessor()
    processed_data = preprocessor.run()
    
    print("\n처음 5행:")
    print(processed_data.head())
    
    print("\n컬럼 목록:")
    print(processed_data.columns.tolist())





