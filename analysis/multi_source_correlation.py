"""
텔레그램, 고래 거래, 트위터 인플루언서 데이터 통합 상관관계 분석

이 모듈은 세 가지 데이터 소스를 통합하여:
1. 시간별 데이터 동기화
2. 교차 상관관계 분석
3. 통합 스파이크 감지
4. 알람 생성 및 우선순위 설정
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')


class MultiSourceCorrelationAnalyzer:
    """다중 소스 상관관계 분석 클래스"""
    
    def __init__(self, telegram_path, whale_path, twitter_path):
        """
        Args:
            telegram_path: 텔레그램 데이터 CSV 경로
            whale_path: 고래 거래 데이터 CSV 경로
            twitter_path: 트위터 인플루언서 데이터 CSV 경로
        """
        print("데이터 로딩 중...")
        
        # 텔레그램 데이터 로드
        self.telegram_df = pd.read_csv(telegram_path)
        self.telegram_df['timestamp'] = pd.to_datetime(self.telegram_df['timestamp'], utc=True).dt.tz_localize(None)
        print(f"✓ 텔레그램 데이터: {len(self.telegram_df)} rows")
        
        # 고래 거래 데이터 로드
        self.whale_df = pd.read_csv(whale_path)
        # 잘못된 타임스탬프 필터링 (errors='coerce'로 변환 실패 시 NaT로 처리)
        self.whale_df['timestamp'] = pd.to_datetime(self.whale_df['block_timestamp'], errors='coerce')
        # NaT 제거 및 타임존 제거
        self.whale_df = self.whale_df.dropna(subset=['timestamp'])
        if self.whale_df['timestamp'].dt.tz is not None:
            self.whale_df['timestamp'] = self.whale_df['timestamp'].dt.tz_localize(None)
        print(f"✓ 고래 거래 데이터: {len(self.whale_df)} rows (유효한 타임스탬프만)")
        
        # 트위터 인플루언서 데이터 로드
        self.twitter_df = pd.read_csv(twitter_path)
        # 잘못된 타임스탬프 필터링
        self.twitter_df['timestamp'] = pd.to_datetime(self.twitter_df['post_date'], errors='coerce')
        # NaT 제거 및 타임존 제거
        self.twitter_df = self.twitter_df.dropna(subset=['timestamp'])
        if self.twitter_df['timestamp'].dt.tz is not None:
            self.twitter_df['timestamp'] = self.twitter_df['timestamp'].dt.tz_localize(None)
        print(f"✓ 트위터 인플루언서 데이터: {len(self.twitter_df)} rows (유효한 타임스탬프만)")
        
        self.merged_df = None
        
    def preprocess_telegram_data(self, freq='1H'):
        """
        텔레그램 데이터 전처리 및 시간별 집계
        
        Args:
            freq: 집계 주기 (기본: 1시간)
            
        Returns:
            DataFrame: 시간별 집계 데이터
        """
        df = self.telegram_df.copy()
        
        # 시간별 집계
        df_grouped = df.groupby(pd.Grouper(key='timestamp', freq=freq)).agg({
            'message_count': 'sum',
            'avg_views': 'mean',
            'total_forwards': 'sum',
            'total_reactions': 'sum',
            'avg_sentiment': 'mean',
            'avg_positive': 'mean',
            'avg_negative': 'mean',
            'avg_neutral': 'mean',
            'avg_msg_length': 'mean'
        }).reset_index()
        
        # 결측치 처리
        df_grouped = df_grouped.fillna(0)
        
        # 컬럼 이름 변경 (접두사 추가)
        df_grouped.columns = ['timestamp'] + [f'telegram_{col}' for col in df_grouped.columns[1:]]
        
        return df_grouped
    
    def preprocess_whale_data(self, freq='1H'):
        """
        고래 거래 데이터 전처리 및 시간별 집계
        
        Args:
            freq: 집계 주기 (기본: 1시간)
            
        Returns:
            DataFrame: 시간별 집계 데이터
        """
        df = self.whale_df.copy()
        
        # amount 컬럼을 숫자로 변환
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # 시간별 집계
        df_grouped = df.groupby(pd.Grouper(key='timestamp', freq=freq)).agg({
            'tx_hash': 'count',  # 거래 빈도
            'amount': ['sum', 'mean', 'max', 'std'],  # 거래량 통계
            'coin_symbol': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'ETH'  # 주요 코인
        }).reset_index()
        
        # 컬럼 이름 평탄화
        df_grouped.columns = ['timestamp', 'whale_tx_count', 'whale_volume_sum', 
                              'whale_volume_mean', 'whale_volume_max', 
                              'whale_volume_std', 'whale_main_coin']
        
        # 결측치 처리
        df_grouped[['whale_volume_sum', 'whale_volume_mean', 'whale_volume_max', 'whale_volume_std']] = \
            df_grouped[['whale_volume_sum', 'whale_volume_mean', 'whale_volume_max', 'whale_volume_std']].fillna(0)
        
        return df_grouped
    
    def preprocess_twitter_data(self, freq='1H'):
        """
        트위터 인플루언서 데이터 전처리 및 시간별 집계
        
        Args:
            freq: 집계 주기 (기본: 1시간)
            
        Returns:
            DataFrame: 시간별 집계 데이터
        """
        df = self.twitter_df.copy()
        
        # 숫자 컬럼 변환
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['shares'] = pd.to_numeric(df['shares'], errors='coerce').fillna(0)
        df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0)
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce').fillna(0)
        
        # 인게이지먼트 점수 계산 (가중치 적용)
        df['engagement_score'] = df['likes'] * 1 + df['shares'] * 3 + df['comments'] * 2
        
        # 시간별 집계
        df_grouped = df.groupby(pd.Grouper(key='timestamp', freq=freq)).agg({
            'post_url': 'count',  # 포스트 수
            'likes': 'sum',
            'shares': 'sum',
            'comments': 'sum',
            'engagement_score': 'sum',
            'sentiment_score': 'mean',
            'spc_coin_label': lambda x: (x != 0).sum()  # 코인 언급 수
        }).reset_index()
        
        # 컬럼 이름 변경
        df_grouped.columns = ['timestamp', 'twitter_post_count', 'twitter_likes', 
                              'twitter_shares', 'twitter_comments', 
                              'twitter_engagement', 'twitter_sentiment',
                              'twitter_coin_mentions']
        
        # 결측치 처리
        df_grouped = df_grouped.fillna(0)
        
        return df_grouped
    
    def merge_all_data(self, freq='1H'):
        """
        모든 데이터 소스를 시간별로 병합
        
        Args:
            freq: 집계 주기 (기본: 1시간)
            
        Returns:
            DataFrame: 병합된 데이터
        """
        print(f"\n데이터 병합 중 (주기: {freq})...")
        
        # 각 데이터 전처리
        telegram_processed = self.preprocess_telegram_data(freq)
        whale_processed = self.preprocess_whale_data(freq)
        twitter_processed = self.preprocess_twitter_data(freq)
        
        # 시간 기준으로 병합 (outer join으로 모든 시간대 포함)
        merged = telegram_processed.merge(whale_processed, on='timestamp', how='outer')
        merged = merged.merge(twitter_processed, on='timestamp', how='outer')
        
        # 결측치를 0으로 채우기
        merged = merged.fillna(0)
        
        # 시간순 정렬
        merged = merged.sort_values('timestamp').reset_index(drop=True)
        
        self.merged_df = merged
        
        print(f"✓ 병합 완료: {len(merged)} rows, {len(merged.columns)} columns")
        print(f"  시간 범위: {merged['timestamp'].min()} ~ {merged['timestamp'].max()}")
        
        return merged
    
    def calculate_correlations(self, method='pearson'):
        """
        모든 변수 간 상관관계 계산
        
        Args:
            method: 'pearson' 또는 'spearman'
            
        Returns:
            DataFrame: 상관계수 매트릭스
        """
        if self.merged_df is None:
            raise ValueError("먼저 merge_all_data()를 실행하세요.")
        
        # 수치형 컬럼만 선택 (timestamp 제외)
        numeric_cols = self.merged_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 상관계수 계산
        if method == 'pearson':
            corr_matrix = self.merged_df[numeric_cols].corr(method='pearson')
        else:
            corr_matrix = self.merged_df[numeric_cols].corr(method='spearman')
        
        return corr_matrix
    
    def find_significant_correlations(self, threshold=0.3, p_value_threshold=0.05):
        """
        통계적으로 유의미한 상관관계 찾기
        
        Args:
            threshold: 상관계수 임계값 (절대값)
            p_value_threshold: p-value 임계값
            
        Returns:
            DataFrame: 유의미한 상관관계 리스트
        """
        if self.merged_df is None:
            raise ValueError("먼저 merge_all_data()를 실행하세요.")
        
        numeric_cols = self.merged_df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = []
        
        # 모든 컬럼 쌍에 대해 상관관계 검정
        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i+1:]:
                # 0이 아닌 값이 충분히 있는지 확인
                valid_data = self.merged_df[[col1, col2]].dropna()
                valid_data = valid_data[(valid_data[col1] != 0) | (valid_data[col2] != 0)]
                
                if len(valid_data) > 10:  # 최소 데이터 포인트
                    try:
                        # Pearson 상관계수 및 p-value
                        corr, p_value = pearsonr(valid_data[col1], valid_data[col2])
                        
                        # 임계값 체크
                        if abs(corr) >= threshold and p_value < p_value_threshold:
                            results.append({
                                'variable_1': col1,
                                'variable_2': col2,
                                'correlation': corr,
                                'p_value': p_value,
                                'n_samples': len(valid_data),
                                'significance': 'high' if p_value < 0.01 else 'medium'
                            })
                    except:
                        pass
        
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            # 상관계수 절대값으로 정렬
            results_df = results_df.sort_values('correlation', key=lambda x: x.abs(), ascending=False)
        
        return results_df
    
    def analyze_cross_source_patterns(self):
        """
        소스 간 교차 패턴 분석
        특정 관심 있는 패턴:
        1. 텔레그램 활동 증가 → 고래 거래 증가
        2. 트위터 인플루언서 활동 → 고래 거래
        3. 세 소스 모두 동시 급증
        
        Returns:
            dict: 패턴 분석 결과
        """
        if self.merged_df is None:
            raise ValueError("먼저 merge_all_data()를 실행하세요.")
        
        df = self.merged_df.copy()
        
        patterns = {}
        
        # 패턴 1: 텔레그램 → 고래 거래
        if 'telegram_message_count' in df.columns and 'whale_tx_count' in df.columns:
            # 시차 상관관계 (lag correlation)
            lags = range(0, 24)  # 0~23시간 시차
            lag_corrs = []
            
            for lag in lags:
                if lag == 0:
                    shifted_whale = df['whale_tx_count']
                else:
                    shifted_whale = df['whale_tx_count'].shift(-lag)
                
                valid_data = pd.DataFrame({
                    'telegram': df['telegram_message_count'],
                    'whale': shifted_whale
                }).dropna()
                
                if len(valid_data) > 10:
                    corr, p_val = pearsonr(valid_data['telegram'], valid_data['whale'])
                    lag_corrs.append({'lag_hours': lag, 'correlation': corr, 'p_value': p_val})
            
            patterns['telegram_to_whale'] = pd.DataFrame(lag_corrs)
        
        # 패턴 2: 트위터 → 고래 거래
        if 'twitter_engagement' in df.columns and 'whale_tx_count' in df.columns:
            lags = range(0, 24)
            lag_corrs = []
            
            for lag in lags:
                if lag == 0:
                    shifted_whale = df['whale_tx_count']
                else:
                    shifted_whale = df['whale_tx_count'].shift(-lag)
                
                valid_data = pd.DataFrame({
                    'twitter': df['twitter_engagement'],
                    'whale': shifted_whale
                }).dropna()
                
                if len(valid_data) > 10:
                    corr, p_val = pearsonr(valid_data['twitter'], valid_data['whale'])
                    lag_corrs.append({'lag_hours': lag, 'correlation': corr, 'p_value': p_val})
            
            patterns['twitter_to_whale'] = pd.DataFrame(lag_corrs)
        
        # 패턴 3: 동시 급증 이벤트 감지
        # Z-score로 정규화하여 급증 판단
        spike_threshold = 2.0
        
        for col in ['telegram_message_count', 'whale_tx_count', 'twitter_engagement']:
            if col in df.columns:
                mean = df[col].rolling(window=24, min_periods=1).mean()
                std = df[col].rolling(window=24, min_periods=1).std()
                df[f'{col}_zscore'] = (df[col] - mean) / (std + 1e-10)
        
        # 동시 급증 조건
        if all(f'{col}_zscore' in df.columns for col in ['telegram_message_count', 'whale_tx_count', 'twitter_engagement']):
            df['triple_spike'] = (
                (df['telegram_message_count_zscore'] > spike_threshold) &
                (df['whale_tx_count_zscore'] > spike_threshold) &
                (df['twitter_engagement_zscore'] > spike_threshold)
            )
            
            triple_spike_events = df[df['triple_spike']].copy()
            patterns['triple_spike_events'] = triple_spike_events
            
        # 이중 급증 (텔레그램 + 고래)
        if 'telegram_message_count_zscore' in df.columns and 'whale_tx_count_zscore' in df.columns:
            df['telegram_whale_spike'] = (
                (df['telegram_message_count_zscore'] > spike_threshold) &
                (df['whale_tx_count_zscore'] > spike_threshold)
            )
            
            telegram_whale_events = df[df['telegram_whale_spike']].copy()
            patterns['telegram_whale_spike_events'] = telegram_whale_events
        
        # 이중 급증 (트위터 + 고래)
        if 'twitter_engagement_zscore' in df.columns and 'whale_tx_count_zscore' in df.columns:
            df['twitter_whale_spike'] = (
                (df['twitter_engagement_zscore'] > spike_threshold) &
                (df['whale_tx_count_zscore'] > spike_threshold)
            )
            
            twitter_whale_events = df[df['twitter_whale_spike']].copy()
            patterns['twitter_whale_spike_events'] = twitter_whale_events
        
        self.merged_df = df  # 업데이트된 데이터 저장
        
        return patterns
    
    def generate_alert_priority(self, row):
        """
        행 데이터를 기반으로 알람 우선순위 계산
        
        Args:
            row: DataFrame의 한 행
            
        Returns:
            dict: 알람 정보
        """
        priority_score = 0
        alert_reasons = []
        
        # 텔레그램 스파이크
        if 'telegram_message_count_zscore' in row and row['telegram_message_count_zscore'] > 2.0:
            priority_score += 2
            alert_reasons.append(f"텔레그램 메시지 급증 (z={row['telegram_message_count_zscore']:.2f})")
        
        # 고래 거래 스파이크
        if 'whale_tx_count_zscore' in row and row['whale_tx_count_zscore'] > 2.0:
            priority_score += 3  # 고래 거래가 더 중요
            alert_reasons.append(f"고래 거래 급증 (z={row['whale_tx_count_zscore']:.2f})")
        
        # 트위터 인게이지먼트 스파이크
        if 'twitter_engagement_zscore' in row and row['twitter_engagement_zscore'] > 2.0:
            priority_score += 2
            alert_reasons.append(f"트위터 인플루언서 활동 급증 (z={row['twitter_engagement_zscore']:.2f})")
        
        # 복합 스파이크 보너스
        if 'telegram_whale_spike' in row and row['telegram_whale_spike']:
            priority_score += 5
            alert_reasons.append("⚠️ 텔레그램+고래 동시 급증")
        
        if 'twitter_whale_spike' in row and row['twitter_whale_spike']:
            priority_score += 4
            alert_reasons.append("⚠️ 트위터+고래 동시 급증")
        
        if 'triple_spike' in row and row['triple_spike']:
            priority_score += 10
            alert_reasons.append("🚨 3개 소스 모두 급증 (CRITICAL)")
        
        # 우선순위 레벨 결정
        if priority_score >= 10:
            level = 'CRITICAL'
        elif priority_score >= 5:
            level = 'HIGH'
        elif priority_score >= 2:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'priority_score': priority_score,
            'alert_level': level,
            'reasons': '; '.join(alert_reasons)
        }
    
    def generate_all_alerts(self, min_priority_score=2):
        """
        모든 알람 생성
        
        Args:
            min_priority_score: 최소 우선순위 점수
            
        Returns:
            DataFrame: 알람 데이터
        """
        if self.merged_df is None:
            raise ValueError("먼저 merge_all_data()를 실행하세요.")
        
        alerts = []
        
        for idx, row in self.merged_df.iterrows():
            alert_info = self.generate_alert_priority(row)
            
            if alert_info['priority_score'] >= min_priority_score:
                alerts.append({
                    'timestamp': row['timestamp'],
                    'priority_score': alert_info['priority_score'],
                    'alert_level': alert_info['alert_level'],
                    'reasons': alert_info['reasons'],
                    'telegram_msgs': row.get('telegram_message_count', 0),
                    'whale_txs': row.get('whale_tx_count', 0),
                    'twitter_engagement': row.get('twitter_engagement', 0),
                    'telegram_sentiment': row.get('telegram_avg_sentiment', 0),
                    'twitter_sentiment': row.get('twitter_sentiment', 0),
                })
        
        alerts_df = pd.DataFrame(alerts)
        
        if not alerts_df.empty:
            # 우선순위 점수로 정렬
            alerts_df = alerts_df.sort_values(['priority_score', 'timestamp'], ascending=[False, False])
        
        return alerts_df
    
    def save_results(self, output_dir='/Volumes/T7/class/2025-FALL/big_data/data'):
        """
        분석 결과 저장
        
        Args:
            output_dir: 출력 디렉토리
        """
        import os
        
        # 병합 데이터 저장
        if self.merged_df is not None:
            output_path = os.path.join(output_dir, 'multi_source_merged_data.csv')
            self.merged_df.to_csv(output_path, index=False)
            print(f"✓ 병합 데이터 저장: {output_path}")
        
        # 상관관계 매트릭스 저장
        corr_matrix = self.calculate_correlations()
        corr_path = os.path.join(output_dir, 'multi_source_correlation_matrix.csv')
        corr_matrix.to_csv(corr_path)
        print(f"✓ 상관관계 매트릭스 저장: {corr_path}")
        
        # 유의미한 상관관계 저장
        sig_corr = self.find_significant_correlations()
        if not sig_corr.empty:
            sig_path = os.path.join(output_dir, 'multi_source_significant_correlations.csv')
            sig_corr.to_csv(sig_path, index=False)
            print(f"✓ 유의미한 상관관계 저장: {sig_path}")
        
        # 알람 생성 및 저장
        alerts = self.generate_all_alerts(min_priority_score=2)
        if not alerts.empty:
            alerts_path = os.path.join(output_dir, 'multi_source_alerts.csv')
            alerts.to_csv(alerts_path, index=False)
            print(f"✓ 알람 데이터 저장: {alerts_path}")
        
        # 패턴 분석 결과 저장
        patterns = self.analyze_cross_source_patterns()
        
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, pd.DataFrame) and not pattern_data.empty:
                pattern_path = os.path.join(output_dir, f'pattern_{pattern_name}.csv')
                pattern_data.to_csv(pattern_path, index=False)
                print(f"✓ 패턴 분석 저장: {pattern_path}")


if __name__ == '__main__':
    # 데이터 경로
    TELEGRAM_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/telegram_data.csv'
    WHALE_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/whale_transactions_rows.csv'
    TWITTER_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/twitter_influencer_labeled_rows.csv'
    
    print("=" * 80)
    print("다중 소스 상관관계 분석 시작")
    print("=" * 80)
    
    # 분석기 초기화
    analyzer = MultiSourceCorrelationAnalyzer(TELEGRAM_PATH, WHALE_PATH, TWITTER_PATH)
    
    # 데이터 병합
    merged_df = analyzer.merge_all_data(freq='1H')
    
    print("\n" + "=" * 80)
    print("상관관계 분석")
    print("=" * 80)
    
    # 유의미한 상관관계 찾기
    sig_corr = analyzer.find_significant_correlations(threshold=0.3, p_value_threshold=0.05)
    
    if not sig_corr.empty:
        print(f"\n✓ {len(sig_corr)}개의 유의미한 상관관계 발견:")
        print(sig_corr.head(20).to_string())
    else:
        print("\n⚠ 유의미한 상관관계를 찾지 못했습니다.")
    
    print("\n" + "=" * 80)
    print("교차 패턴 분석")
    print("=" * 80)
    
    # 패턴 분석
    patterns = analyzer.analyze_cross_source_patterns()
    
    for pattern_name, pattern_data in patterns.items():
        if isinstance(pattern_data, pd.DataFrame) and not pattern_data.empty:
            print(f"\n[{pattern_name}]")
            if 'lag_hours' in pattern_data.columns:
                # 시차 상관관계
                max_corr = pattern_data.loc[pattern_data['correlation'].abs().idxmax()]
                print(f"  최대 상관관계: lag={max_corr['lag_hours']}h, corr={max_corr['correlation']:.3f}, p={max_corr['p_value']:.4f}")
            else:
                # 이벤트 수
                print(f"  감지된 이벤트: {len(pattern_data)}개")
                if len(pattern_data) > 0:
                    print(f"  첫 이벤트: {pattern_data['timestamp'].iloc[0]}")
                    print(f"  마지막 이벤트: {pattern_data['timestamp'].iloc[-1]}")
    
    print("\n" + "=" * 80)
    print("알람 생성")
    print("=" * 80)
    
    # 알람 생성
    alerts = analyzer.generate_all_alerts(min_priority_score=2)
    
    if not alerts.empty:
        print(f"\n✓ {len(alerts)}개의 알람 생성:")
        
        # 레벨별 카운트
        level_counts = alerts['alert_level'].value_counts()
        print(f"\n레벨별 분포:")
        for level, count in level_counts.items():
            print(f"  {level}: {count}개")
        
        print(f"\n상위 10개 알람:")
        print(alerts.head(10)[['timestamp', 'alert_level', 'priority_score', 'reasons']].to_string())
    else:
        print("\n⚠ 생성된 알람이 없습니다.")
    
    print("\n" + "=" * 80)
    print("결과 저장")
    print("=" * 80)
    
    # 결과 저장
    analyzer.save_results()
    
    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)

