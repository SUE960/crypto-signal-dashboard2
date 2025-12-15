"""
상관관계 분석 모듈

커뮤니티 활동과 거래량/가격 간의 상관관계를 분석합니다.
- 피어슨/스피어만 상관계수
- 시차 상관관계 (Lag Correlation)
- 그랜저 인과관계 (Granger Causality)
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests
import warnings

warnings.filterwarnings('ignore')


class CorrelationAnalyzer:
    """상관관계 분석 클래스"""
    
    def __init__(self, df):
        """
        Args:
            df: 전처리된 데이터프레임
        """
        self.df = df.copy()
        
    def pearson_correlation(self, columns=None):
        """
        피어슨 상관계수 계산
        
        Args:
            columns: 분석할 컬럼 리스트 (None이면 수치형 컬럼 전체)
            
        Returns:
            DataFrame: 상관계수 행렬
        """
        if columns is None:
            # 수치형 컬럼만 선택
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            # timestamp 관련 컬럼 제외
            columns = [c for c in columns if c not in ['hour', 'day_of_week', 'day', 'month']]
        
        corr_matrix = self.df[columns].corr(method='pearson')
        return corr_matrix
    
    def spearman_correlation(self, columns=None):
        """
        스피어만 상관계수 계산 (비선형 관계 측정)
        
        Args:
            columns: 분석할 컬럼 리스트
            
        Returns:
            DataFrame: 상관계수 행렬
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            columns = [c for c in columns if c not in ['hour', 'day_of_week', 'day', 'month']]
        
        corr_matrix = self.df[columns].corr(method='spearman')
        return corr_matrix
    
    def lag_correlation(self, col1, col2, max_lag=24):
        """
        시차 상관관계 계산
        
        Args:
            col1: 선행 변수 (예: message_count)
            col2: 후행 변수 (예: ETH_close)
            max_lag: 최대 시차 (시간)
            
        Returns:
            DataFrame: 시차별 상관계수
        """
        lags = []
        correlations = []
        p_values = []
        
        # 결측치 제거
        data = self.df[[col1, col2]].dropna()
        
        if len(data) < max_lag + 10:
            print(f"경고: 데이터가 충분하지 않습니다 (필요: {max_lag + 10}, 실제: {len(data)})")
            return pd.DataFrame()
        
        for lag in range(0, max_lag + 1):
            if lag == 0:
                # lag 0: 동시 상관관계
                corr, p_val = stats.pearsonr(data[col1], data[col2])
            else:
                # lag > 0: col1이 col2보다 lag 시간 앞서는 경우
                if len(data) > lag:
                    x = data[col1].iloc[:-lag].values
                    y = data[col2].iloc[lag:].values
                    
                    if len(x) > 0 and len(y) > 0:
                        corr, p_val = stats.pearsonr(x, y)
                    else:
                        corr, p_val = np.nan, np.nan
                else:
                    corr, p_val = np.nan, np.nan
            
            lags.append(lag)
            correlations.append(corr)
            p_values.append(p_val)
        
        result = pd.DataFrame({
            'lag': lags,
            'correlation': correlations,
            'p_value': p_values
        })
        
        # 유의한 상관관계 표시
        result['significant'] = result['p_value'] < 0.05
        
        return result
    
    def granger_causality_test(self, col1, col2, max_lag=12):
        """
        그랜저 인과관계 검정
        col1이 col2를 '야기'하는지 검정
        
        Args:
            col1: 원인 변수
            col2: 결과 변수
            max_lag: 최대 시차
            
        Returns:
            dict: 검정 결과
        """
        # 결측치 제거
        data = self.df[[col1, col2]].dropna()
        
        if len(data) < max_lag * 3:
            return {
                'error': f'데이터가 충분하지 않습니다 (필요: {max_lag * 3}, 실제: {len(data)})'
            }
        
        try:
            # 그랜저 인과관계 검정
            # H0: col1은 col2의 원인이 아니다
            # p-value < 0.05이면 H0 기각 -> col1이 col2의 원인이다
            test_result = grangercausalitytests(data[[col2, col1]], max_lag, verbose=False)
            
            # 결과 정리
            results = []
            for lag in range(1, max_lag + 1):
                ssr_ftest = test_result[lag][0]['ssr_ftest']
                results.append({
                    'lag': lag,
                    'f_statistic': ssr_ftest[0],
                    'p_value': ssr_ftest[1],
                    'significant': ssr_ftest[1] < 0.05
                })
            
            return pd.DataFrame(results)
        
        except Exception as e:
            return {'error': str(e)}
    
    def volatility_analysis(self, trigger_col, target_col, threshold=2.0):
        """
        트리거 이벤트 발생 시 타겟 변수의 변동성 분석
        
        Args:
            trigger_col: 트리거 컬럼 (예: message_count_zscore)
            target_col: 타겟 컬럼 (예: ETH_close)
            threshold: Z-score 임계값
            
        Returns:
            dict: 변동성 분석 결과
        """
        # 트리거 이벤트 식별 (Z-score > threshold)
        trigger_events = self.df[self.df[trigger_col].abs() > threshold].copy()
        
        if len(trigger_events) == 0:
            return {
                'error': f'{trigger_col}에서 임계값 {threshold}를 초과하는 이벤트가 없습니다.'
            }
        
        # 타겟 변수의 변화율 계산
        window = 6  # 이벤트 후 6시간 동안의 변화
        
        volatilities = []
        for idx in trigger_events.index:
            if idx + window < len(self.df):
                # 이벤트 발생 시점의 값
                base_value = self.df.loc[idx, target_col]
                
                # 이벤트 후 window 시간 동안의 최대/최소값
                future_values = self.df.loc[idx:idx+window, target_col]
                max_value = future_values.max()
                min_value = future_values.min()
                
                # 변동성 계산 (%)
                if base_value > 0:
                    max_change = ((max_value - base_value) / base_value) * 100
                    min_change = ((min_value - base_value) / base_value) * 100
                    volatility = max(abs(max_change), abs(min_change))
                    
                    volatilities.append(volatility)
        
        # 평균 이벤트 없을 때의 변동성 계산 (비교용)
        normal_periods = self.df[self.df[trigger_col].abs() <= 1.0].copy()
        normal_volatilities = []
        
        for idx in normal_periods.index[::24]:  # 24시간마다 샘플링
            if idx + window < len(self.df):
                base_value = self.df.loc[idx, target_col]
                future_values = self.df.loc[idx:idx+window, target_col]
                max_value = future_values.max()
                min_value = future_values.min()
                
                if base_value > 0:
                    max_change = ((max_value - base_value) / base_value) * 100
                    min_change = ((min_value - base_value) / base_value) * 100
                    volatility = max(abs(max_change), abs(min_change))
                    
                    normal_volatilities.append(volatility)
        
        result = {
            'trigger_events_count': len(trigger_events),
            'avg_volatility_during_events': np.mean(volatilities) if volatilities else 0,
            'avg_volatility_normal': np.mean(normal_volatilities) if normal_volatilities else 0,
            'volatility_ratio': (np.mean(volatilities) / np.mean(normal_volatilities)) 
                                if volatilities and normal_volatilities and np.mean(normal_volatilities) > 0 else 0,
            'max_volatility': np.max(volatilities) if volatilities else 0,
        }
        
        return result
    
    def get_top_correlations(self, target_col, n=10, method='pearson'):
        """
        특정 컬럼과 가장 상관관계가 높은 변수들 반환
        
        Args:
            target_col: 타겟 컬럼
            n: 상위 n개
            method: 'pearson' 또는 'spearman'
            
        Returns:
            Series: 상위 n개 상관관계
        """
        if method == 'pearson':
            corr_matrix = self.pearson_correlation()
        else:
            corr_matrix = self.spearman_correlation()
        
        if target_col not in corr_matrix.columns:
            return pd.Series()
        
        # 자기 자신 제외
        correlations = corr_matrix[target_col].drop(target_col, errors='ignore')
        
        # 절대값 기준 정렬
        top_corr = correlations.abs().sort_values(ascending=False).head(n)
        
        # 원래 값 반환
        return correlations[top_corr.index]


def generate_correlation_report(df, output_path=None):
    """
    상관관계 분석 리포트 생성
    
    Args:
        df: 전처리된 데이터프레임
        output_path: 리포트 저장 경로 (None이면 출력만)
    """
    analyzer = CorrelationAnalyzer(df)
    
    print("=== 상관관계 분석 리포트 ===\n")
    
    # 1. ETH 가격과의 상관관계
    print("1. ETH 가격과 상관관계가 높은 변수 (Top 10)")
    print("-" * 60)
    top_eth_corr = analyzer.get_top_correlations('ETH_close', n=10)
    for var, corr in top_eth_corr.items():
        print(f"  {var:40s}: {corr:7.4f}")
    print()
    
    # 2. 텔레그램 메시지 수와 ETH 가격의 시차 상관관계
    if 'message_count' in df.columns:
        print("2. 텔레그램 메시지 수 -> ETH 가격 시차 상관관계")
        print("-" * 60)
        lag_corr = analyzer.lag_correlation('message_count', 'ETH_close', max_lag=12)
        if not lag_corr.empty:
            significant_lags = lag_corr[lag_corr['significant']]
            if len(significant_lags) > 0:
                print("  유의한 시차:")
                for _, row in significant_lags.iterrows():
                    print(f"    Lag {row['lag']:2.0f}시간: r={row['correlation']:7.4f}, p={row['p_value']:.4f}")
            else:
                print("  유의한 시차가 없습니다.")
        print()
        
        # 3. 그랜저 인과관계 검정
        print("3. 그랜저 인과관계 검정: 메시지 수 -> ETH 가격")
        print("-" * 60)
        granger_result = analyzer.granger_causality_test('message_count', 'ETH_close', max_lag=8)
        if isinstance(granger_result, pd.DataFrame):
            significant = granger_result[granger_result['significant']]
            if len(significant) > 0:
                print("  인과관계가 있는 시차:")
                for _, row in significant.iterrows():
                    print(f"    Lag {row['lag']:2.0f}: F={row['f_statistic']:.2f}, p={row['p_value']:.4f}")
            else:
                print("  유의한 인과관계가 없습니다.")
        else:
            print(f"  오류: {granger_result.get('error', '알 수 없는 오류')}")
        print()
        
        # 4. 변동성 분석
        print("4. 커뮤니티 활동 급증 시 가격 변동성")
        print("-" * 60)
        vol_result = analyzer.volatility_analysis('message_count_zscore', 'ETH_close', threshold=2.0)
        if 'error' not in vol_result:
            print(f"  트리거 이벤트 수: {vol_result['trigger_events_count']}")
            print(f"  이벤트 발생 시 평균 변동성: {vol_result['avg_volatility_during_events']:.2f}%")
            print(f"  평상시 평균 변동성: {vol_result['avg_volatility_normal']:.2f}%")
            print(f"  변동성 비율: {vol_result['volatility_ratio']:.2f}x")
            print(f"  최대 변동성: {vol_result['max_volatility']:.2f}%")
        else:
            print(f"  {vol_result['error']}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    # 테스트용
    import sys
    sys.path.append('/Volumes/T7/class/2025-FALL/big_data')
    
    # 전처리된 데이터 로드
    df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 리포트 생성
    generate_correlation_report(df)






