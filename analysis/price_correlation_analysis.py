"""
코인 가격과 다중 소스(텔레그램, 고래, 트위터)의 상관관계 분석

BTC/ETH 가격 데이터를 추가하여 종합 분석
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')


class PriceCorrelationAnalyzer:
    """가격과 다중 소스의 상관관계 분석"""
    
    def __init__(self):
        """데이터 경로 설정"""
        self.base_path = '/Volumes/T7/class/2025-FALL/big_data/data'
        
        print("=" * 80)
        print("코인 가격 & 다중 소스 상관관계 분석")
        print("=" * 80)
    
    def load_price_data(self):
        """BTC와 ETH 가격 데이터 로드"""
        print("\n가격 데이터 로딩 중...")
        
        # BTC 가격
        btc_df = pd.read_csv(f'{self.base_path}/price_history_btc_rows.csv')
        btc_df['timestamp'] = pd.to_datetime(btc_df['timestamp'], format='mixed', utc=True).dt.tz_localize(None)
        btc_df = btc_df.sort_values('timestamp')
        print(f"✓ BTC 가격 데이터: {len(btc_df)} rows")
        
        # ETH 가격
        eth_df = pd.read_csv(f'{self.base_path}/price_history_eth_rows.csv')
        eth_df['timestamp'] = pd.to_datetime(eth_df['timestamp'], format='mixed', utc=True).dt.tz_localize(None)
        eth_df = eth_df.sort_values('timestamp')
        print(f"✓ ETH 가격 데이터: {len(eth_df)} rows")
        
        return btc_df, eth_df
    
    def load_multi_source_data(self):
        """기존 병합된 다중 소스 데이터 로드"""
        print("\n다중 소스 데이터 로딩 중...")
        
        merged_df = pd.read_csv(f'{self.base_path}/multi_source_merged_data.csv')
        merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
        
        print(f"✓ 병합 데이터: {len(merged_df)} rows")
        print(f"  시간 범위: {merged_df['timestamp'].min()} ~ {merged_df['timestamp'].max()}")
        
        return merged_df
    
    def merge_price_data(self, merged_df, btc_df, eth_df):
        """가격 데이터를 병합 데이터에 추가"""
        print("\n가격 데이터 병합 중...")
        
        # BTC 가격을 시간별로 집계
        btc_hourly = btc_df.groupby(pd.Grouper(key='timestamp', freq='1H')).agg({
            'close_price': 'last',
            'high_price': 'max',
            'low_price': 'min',
            'volume': 'sum'
        }).reset_index()
        
        btc_hourly.columns = ['timestamp', 'btc_close', 'btc_high', 'btc_low', 'btc_volume']
        
        # ETH 가격을 시간별로 집계
        eth_hourly = eth_df.groupby(pd.Grouper(key='timestamp', freq='1H')).agg({
            'close_price': 'last',
            'high_price': 'max',
            'low_price': 'min',
            'volume': 'sum'
        }).reset_index()
        
        eth_hourly.columns = ['timestamp', 'eth_close', 'eth_high', 'eth_low', 'eth_volume']
        
        # 병합
        result = merged_df.merge(btc_hourly, on='timestamp', how='left')
        result = result.merge(eth_hourly, on='timestamp', how='left')
        
        # 결측치 forward fill (가격은 이전 값으로 채움)
        price_cols = ['btc_close', 'btc_high', 'btc_low', 'btc_volume',
                      'eth_close', 'eth_high', 'eth_low', 'eth_volume']
        result[price_cols] = result[price_cols].ffill()
        
        print(f"✓ 병합 완료: {len(result)} rows, {len(result.columns)} columns")
        
        # 가격 변화율 계산
        result['btc_price_change'] = result['btc_close'].pct_change() * 100
        result['eth_price_change'] = result['eth_close'].pct_change() * 100
        
        # 가격 변동성 (이동표준편차)
        result['btc_volatility'] = result['btc_close'].rolling(window=24).std()
        result['eth_volatility'] = result['eth_close'].rolling(window=24).std()
        
        return result
    
    def analyze_price_correlations(self, df):
        """가격과 다중 소스의 상관관계 분석"""
        print("\n" + "=" * 80)
        print("가격 상관관계 분석")
        print("=" * 80)
        
        # 분석할 변수 쌍
        analysis_pairs = [
            # 텔레그램 vs 가격
            ('telegram_message_count', 'btc_close', '텔레그램 메시지 수 vs BTC 가격'),
            ('telegram_message_count', 'eth_close', '텔레그램 메시지 수 vs ETH 가격'),
            ('telegram_avg_sentiment', 'btc_price_change', '텔레그램 감정 vs BTC 변화율'),
            ('telegram_avg_sentiment', 'eth_price_change', '텔레그램 감정 vs ETH 변화율'),
            
            # 고래 거래 vs 가격
            ('whale_tx_count', 'btc_close', '고래 거래 빈도 vs BTC 가격'),
            ('whale_tx_count', 'eth_close', '고래 거래 빈도 vs ETH 가격'),
            ('whale_volume_sum', 'btc_price_change', '고래 거래량 vs BTC 변화율'),
            ('whale_volume_sum', 'eth_price_change', '고래 거래량 vs ETH 변화율'),
            ('whale_tx_count', 'btc_volatility', '고래 거래 빈도 vs BTC 변동성'),
            ('whale_tx_count', 'eth_volatility', '고래 거래 빈도 vs ETH 변동성'),
            
            # 트위터 vs 가격
            ('twitter_engagement', 'btc_close', '트위터 인게이지먼트 vs BTC 가격'),
            ('twitter_engagement', 'eth_close', '트위터 인게이지먼트 vs ETH 가격'),
            ('twitter_sentiment', 'btc_price_change', '트위터 감정 vs BTC 변화율'),
            ('twitter_sentiment', 'eth_price_change', '트위터 감정 vs ETH 변화율'),
        ]
        
        results = []
        
        for var1, var2, description in analysis_pairs:
            if var1 in df.columns and var2 in df.columns:
                # 유효한 데이터만 선택
                valid_data = df[[var1, var2]].dropna()
                valid_data = valid_data[(valid_data[var1] != 0) | (valid_data[var2] != 0)]
                
                if len(valid_data) > 30:
                    try:
                        corr, p_value = pearsonr(valid_data[var1], valid_data[var2])
                        
                        results.append({
                            'variable_1': var1,
                            'variable_2': var2,
                            'description': description,
                            'correlation': corr,
                            'p_value': p_value,
                            'n_samples': len(valid_data),
                            'significance': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
                        })
                    except:
                        pass
        
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            results_df = results_df.sort_values('correlation', key=lambda x: x.abs(), ascending=False)
            
            print("\n주요 상관관계 발견:\n")
            for idx, row in results_df.head(20).iterrows():
                sig = row['significance']
                print(f"• {row['description']}")
                print(f"  상관계수: {row['correlation']:.4f} {sig}")
                print(f"  p-value: {row['p_value']:.6f} (n={row['n_samples']})")
                print()
        
        return results_df
    
    def analyze_lag_correlations(self, df, max_lag=24):
        """시차 상관관계 분석 (가격 선행/후행 지표)"""
        print("\n" + "=" * 80)
        print("시차 상관관계 분석")
        print("=" * 80)
        
        lag_analyses = [
            ('telegram_message_count', 'btc_price_change', '텔레그램 → BTC 변화율'),
            ('whale_tx_count', 'btc_price_change', '고래 거래 → BTC 변화율'),
            ('twitter_engagement', 'btc_price_change', '트위터 → BTC 변화율'),
            ('btc_price_change', 'whale_tx_count', 'BTC 변화율 → 고래 거래'),
        ]
        
        lag_results = {}
        
        for var1, var2, description in lag_analyses:
            if var1 not in df.columns or var2 not in df.columns:
                continue
            
            print(f"\n{description}:")
            
            lags = range(-max_lag, max_lag + 1)
            lag_corrs = []
            
            for lag in lags:
                if lag == 0:
                    shifted_var2 = df[var2]
                elif lag > 0:
                    shifted_var2 = df[var2].shift(-lag)
                else:
                    shifted_var2 = df[var2].shift(-lag)
                
                valid_data = pd.DataFrame({
                    'var1': df[var1],
                    'var2': shifted_var2
                }).dropna()
                
                if len(valid_data) > 30:
                    try:
                        corr, p_val = pearsonr(valid_data['var1'], valid_data['var2'])
                        lag_corrs.append({
                            'lag_hours': lag,
                            'correlation': corr,
                            'p_value': p_val
                        })
                    except:
                        pass
            
            if lag_corrs:
                lag_df = pd.DataFrame(lag_corrs)
                
                # 최대 양의 상관관계
                max_pos_idx = lag_df['correlation'].idxmax()
                max_pos = lag_df.loc[max_pos_idx]
                
                # 최대 음의 상관관계
                min_neg_idx = lag_df['correlation'].idxmin()
                min_neg = lag_df.loc[min_neg_idx]
                
                # 절대값 최대
                max_abs_idx = lag_df['correlation'].abs().idxmax()
                max_abs = lag_df.loc[max_abs_idx]
                
                print(f"  최대 양의 상관: lag={max_pos['lag_hours']}h, r={max_pos['correlation']:.4f}, p={max_pos['p_value']:.6f}")
                print(f"  최대 음의 상관: lag={min_neg['lag_hours']}h, r={min_neg['correlation']:.4f}, p={min_neg['p_value']:.6f}")
                print(f"  절대값 최대:   lag={max_abs['lag_hours']}h, r={max_abs['correlation']:.4f}, p={max_abs['p_value']:.6f}")
                
                lag_results[description] = lag_df
        
        return lag_results
    
    def price_spike_analysis(self, df):
        """가격 급등/급락과 다중 소스 활동의 관계"""
        print("\n" + "=" * 80)
        print("가격 급변과 다중 소스 활동 분석")
        print("=" * 80)
        
        # 가격 급등/급락 정의 (변화율 2% 이상)
        df['btc_spike'] = df['btc_price_change'].abs() > 2.0
        df['eth_spike'] = df['eth_price_change'].abs() > 2.0
        
        btc_spikes = df[df['btc_spike']].copy()
        eth_spikes = df[df['eth_spike']].copy()
        
        print(f"\nBTC 가격 급변 이벤트: {len(btc_spikes)}회")
        print(f"ETH 가격 급변 이벤트: {len(eth_spikes)}회")
        
        # 가격 급변 시 다중 소스 활동 비교
        if not btc_spikes.empty:
            print("\n[BTC 가격 급변 시]")
            print(f"  텔레그램 메시지: 평균 {btc_spikes['telegram_message_count'].mean():.2f} (전체 평균: {df['telegram_message_count'].mean():.2f})")
            print(f"  고래 거래 빈도: 평균 {btc_spikes['whale_tx_count'].mean():.2f} (전체 평균: {df['whale_tx_count'].mean():.2f})")
            print(f"  트위터 인게이지먼트: 평균 {btc_spikes['twitter_engagement'].mean():.2f} (전체 평균: {df['twitter_engagement'].mean():.2f})")
        
        # 다중 소스 스파이크와 가격 변동 관계
        if 'telegram_whale_spike' in df.columns:
            critical_events = df[df['telegram_whale_spike'] == True].copy()
            
            if not critical_events.empty:
                print(f"\n[텔레그램+고래 동시 급증 시 가격 변화]")
                print(f"  BTC 평균 변화율: {critical_events['btc_price_change'].mean():.2f}%")
                print(f"  ETH 평균 변화율: {critical_events['eth_price_change'].mean():.2f}%")
                print(f"  BTC 변동성: {critical_events['btc_volatility'].mean():.2f}")
                print(f"  ETH 변동성: {critical_events['eth_volatility'].mean():.2f}")
        
        return df
    
    def save_results(self, df, corr_results, lag_results):
        """결과 저장"""
        print("\n" + "=" * 80)
        print("결과 저장")
        print("=" * 80)
        
        # 가격 포함 병합 데이터
        output_path = f'{self.base_path}/multi_source_with_price.csv'
        df.to_csv(output_path, index=False)
        print(f"✓ 가격 포함 병합 데이터: {output_path}")
        
        # 가격 상관관계
        if not corr_results.empty:
            corr_path = f'{self.base_path}/price_correlation_results.csv'
            corr_results.to_csv(corr_path, index=False)
            print(f"✓ 가격 상관관계 결과: {corr_path}")
        
        # 시차 상관관계
        for name, lag_df in lag_results.items():
            safe_name = name.replace(' ', '_').replace('→', 'to')
            lag_path = f'{self.base_path}/price_lag_{safe_name}.csv'
            lag_df.to_csv(lag_path, index=False)
            print(f"✓ 시차 상관관계 ({name}): {lag_path}")


if __name__ == '__main__':
    analyzer = PriceCorrelationAnalyzer()
    
    # 데이터 로드
    btc_df, eth_df = analyzer.load_price_data()
    merged_df = analyzer.load_multi_source_data()
    
    # 가격 데이터 병합
    full_df = analyzer.merge_price_data(merged_df, btc_df, eth_df)
    
    # 상관관계 분석
    corr_results = analyzer.analyze_price_correlations(full_df)
    
    # 시차 상관관계 분석
    lag_results = analyzer.analyze_lag_correlations(full_df, max_lag=24)
    
    # 가격 급변 분석
    full_df = analyzer.price_spike_analysis(full_df)
    
    # 결과 저장
    analyzer.save_results(full_df, corr_results, lag_results)
    
    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)

