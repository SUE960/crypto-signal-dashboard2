"""
데이터 로딩 유틸리티 - Streamlit Cloud 배포용

모든 데이터 파일을 로드하고 기본 전처리를 수행합니다.
파일이 없으면 빈 DataFrame을 반환하여 앱이 중단되지 않도록 합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


class DataLoader:
    """데이터 로더 클래스"""
    
    def __init__(self, data_dir=None):
        """
        Args:
            data_dir: 데이터 디렉토리 경로 (기본값: 프로젝트 루트의 data/)
        """
        if data_dir is None:
            # 상대 경로로 data 폴더 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            data_dir = os.path.join(project_root, 'data')
        self.data_dir = data_dir
        
    def load_whale_transactions(self):
        """
        고래 지갑 거래 데이터 로드 (시간별 집계)
        
        Returns:
            DataFrame: 시간별 거래 데이터 (없으면 빈 DataFrame)
        """
        file_path = os.path.join(self.data_dir, 'whale_transactions_rows_ETH_rev1.csv')
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 없습니다.")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            df = df.dropna(subset=['Time'])
            
            if df['Time'].dt.tz is not None:
                df['Time'] = df['Time'].dt.tz_localize(None)
            
            df = df.rename(columns={
                'Time': 'timestamp',
                'frequency': 'tx_frequency',
                'sum_amount': 'tx_amount',
                'sum_amount_usd': 'tx_amount_usd'
            })
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
        except Exception as e:
            print(f"경고: 고래 거래 데이터 로드 실패 - {e}")
            return pd.DataFrame()
    
    def load_price_data(self, coin='ETH'):
        """
        가격 데이터 로드
        
        Args:
            coin: 'ETH' 또는 'BTC'
            
        Returns:
            DataFrame: 가격 데이터 (없으면 빈 DataFrame)
        """
        file_path = os.path.join(self.data_dir, f'price_history_{coin.lower()}_rows.csv')
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 없습니다.")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            
            if df['timestamp'].dt.tz is None:
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
            else:
                df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
            
            rename_dict = {col: f'{coin}_{col}' for col in df.columns if col != 'timestamp'}
            df = df.rename(columns=rename_dict)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"경고: {coin} 가격 데이터 로드 실패 - {e}")
            return pd.DataFrame()
    
    def load_telegram_data(self):
        """
        텔레그램 데이터 로드
        
        Returns:
            DataFrame: 텔레그램 데이터 (없으면 빈 DataFrame)
        """
        file_path = os.path.join(self.data_dir, 'telegram_data.csv')
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 없습니다.")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)
            
            df = df.rename(columns={'date': 'timestamp'})
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"경고: 텔레그램 데이터 로드 실패 - {e}")
            return pd.DataFrame()
    
    def load_twitter_data(self):
        """
        트위터 인플루언서 데이터 로드
        
        Returns:
            DataFrame: 트위터 데이터 (없으면 빈 DataFrame)
        """
        file_path = os.path.join(self.data_dir, 'twitter_influencer_labeled_rows.csv')
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 없습니다.")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df['post_date'] = pd.to_datetime(df['post_date'], errors='coerce')
            df = df.dropna(subset=['post_date'])
            
            if df['post_date'].dt.tz is not None:
                df['post_date'] = df['post_date'].dt.tz_localize(None)
            
            df = df.rename(columns={'post_date': 'timestamp'})
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"경고: 트위터 데이터 로드 실패 - {e}")
            return pd.DataFrame()
    
    def load_coinness_data(self):
        """
        코인니스 뉴스 데이터 로드
        
        Returns:
            DataFrame: 코인니스 뉴스 데이터 (없으면 빈 DataFrame)
        """
        file_path = os.path.join(self.data_dir, 'coinness_data.csv')
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 없습니다.")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
            
            if df['timestamp'].dt.tz is not None:
                df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"경고: 코인니스 데이터 로드 실패 - {e}")
            return pd.DataFrame()
    
    def load_all_data(self):
        """
        모든 데이터를 로드하고 반환
        
        Returns:
            dict: 각 데이터프레임을 담은 딕셔너리
        """
        data = {
            'whale_transactions': self.load_whale_transactions(),
            'eth_price': self.load_price_data('ETH'),
            'btc_price': self.load_price_data('BTC'),
            'telegram': self.load_telegram_data(),
            'twitter': self.load_twitter_data(),
            'coinness': self.load_coinness_data()
        }
        
        return data


if __name__ == '__main__':
    # 테스트
    loader = DataLoader()
    data = loader.load_all_data()
    
    print("=== 데이터 로드 결과 ===")
    for name, df in data.items():
        print(f"{name}: {len(df)} 행")
