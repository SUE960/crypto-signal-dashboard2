"""
스파이크 감지 알고리즘

데이터에서 이상치(스파이크)를 감지하고 알람을 생성합니다.
- Z-score 기반 이상치 탐지
- 이동평균 기반 급등/급락 감지
- 다중 지표 통합 스파이크 점수 계산
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SpikeDetector:
    """스파이크 감지 클래스"""
    
    def __init__(self, df, window=24):
        """
        Args:
            df: 전처리된 데이터프레임
            window: 이동평균 윈도우 크기 (기본: 24시간)
        """
        self.df = df.copy()
        self.window = window
        
    def detect_zscore_spike(self, column, threshold=2.5):
        """
        Z-score 기반 스파이크 감지
        
        Args:
            column: 감지할 컬럼명
            threshold: Z-score 임계값 (기본: 2.5σ)
            
        Returns:
            DataFrame: 스파이크가 감지된 행들
        """
        # Z-score 계산
        zscore_col = f'{column}_zscore'
        
        if zscore_col not in self.df.columns:
            # Z-score가 없으면 직접 계산
            mean = self.df[column].rolling(window=self.window, min_periods=1).mean()
            std = self.df[column].rolling(window=self.window, min_periods=1).std()
            self.df[zscore_col] = (self.df[column] - mean) / (std + 1e-10)
        
        # 임계값을 초과하는 스파이크 감지
        spikes = self.df[self.df[zscore_col].abs() > threshold].copy()
        
        # 스파이크 정보 추가
        spikes['spike_type'] = spikes[zscore_col].apply(
            lambda x: 'positive_spike' if x > 0 else 'negative_spike'
        )
        spikes['spike_magnitude'] = spikes[zscore_col].abs()
        spikes['spike_column'] = column
        
        return spikes[['timestamp', 'spike_column', 'spike_type', 'spike_magnitude', column, zscore_col]]
    
    def detect_moving_average_spike(self, column, threshold_pct=50):
        """
        이동평균 대비 급등/급락 감지
        
        Args:
            column: 감지할 컬럼명
            threshold_pct: 이동평균 대비 변화율 임계값 (%)
            
        Returns:
            DataFrame: 스파이크가 감지된 행들
        """
        ma_col = f'{column}_ma{self.window}'
        
        # 이동평균 계산 (없으면)
        if ma_col not in self.df.columns:
            self.df[ma_col] = self.df[column].rolling(window=self.window, min_periods=1).mean()
        
        # 이동평균 대비 변화율 계산
        self.df['pct_from_ma'] = ((self.df[column] - self.df[ma_col]) / (self.df[ma_col] + 1e-10)) * 100
        
        # 임계값을 초과하는 스파이크 감지
        spikes = self.df[self.df['pct_from_ma'].abs() > threshold_pct].copy()
        
        # 스파이크 정보 추가
        spikes['spike_type'] = spikes['pct_from_ma'].apply(
            lambda x: 'surge' if x > 0 else 'drop'
        )
        spikes['spike_magnitude'] = spikes['pct_from_ma'].abs()
        spikes['spike_column'] = column
        
        return spikes[['timestamp', 'spike_column', 'spike_type', 'spike_magnitude', column, ma_col, 'pct_from_ma']]
    
    def detect_rate_of_change_spike(self, column, window=3, threshold_pct=30):
        """
        변화율 기반 급증 감지 (단기간 급등)
        
        Args:
            column: 감지할 컬럼명
            window: 변화율 계산 윈도우 (시간)
            threshold_pct: 변화율 임계값 (%)
            
        Returns:
            DataFrame: 스파이크가 감지된 행들
        """
        # window 시간 전 대비 변화율
        self.df[f'{column}_roc'] = self.df[column].pct_change(periods=window) * 100
        
        # 임계값 초과 감지
        spikes = self.df[self.df[f'{column}_roc'].abs() > threshold_pct].copy()
        
        # 스파이크 정보
        spikes['spike_type'] = spikes[f'{column}_roc'].apply(
            lambda x: 'rapid_increase' if x > 0 else 'rapid_decrease'
        )
        spikes['spike_magnitude'] = spikes[f'{column}_roc'].abs()
        spikes['spike_column'] = column
        
        return spikes[['timestamp', 'spike_column', 'spike_type', 'spike_magnitude', column, f'{column}_roc']]
    
    def detect_multi_indicator_spike(self, columns, weights=None, threshold=0.7):
        """
        다중 지표 통합 스파이크 감지
        여러 지표가 동시에 이상 신호를 보일 때 감지
        
        Args:
            columns: 감지할 컬럼 리스트
            weights: 각 컬럼의 가중치 (None이면 균등)
            threshold: 통합 점수 임계값 (0~1)
            
        Returns:
            DataFrame: 스파이크가 감지된 행들
        """
        if weights is None:
            weights = {col: 1.0 / len(columns) for col in columns}
        
        # 각 컬럼의 Z-score 정규화 (0~1)
        spike_scores = pd.DataFrame(index=self.df.index)
        spike_scores['timestamp'] = self.df['timestamp']
        
        for col in columns:
            zscore_col = f'{col}_zscore'
            if zscore_col in self.df.columns:
                # Z-score를 0~1로 정규화 (sigmoid 함수)
                normalized = 1 / (1 + np.exp(-self.df[zscore_col]))
                # 중립(0.5)에서 벗어난 정도를 점수로 사용
                spike_scores[f'{col}_score'] = (normalized - 0.5).abs() * 2
            else:
                spike_scores[f'{col}_score'] = 0
        
        # 가중 평균 계산
        spike_scores['combined_score'] = 0
        for col in columns:
            spike_scores['combined_score'] += spike_scores[f'{col}_score'] * weights.get(col, 0)
        
        # 임계값 초과 감지
        spikes = spike_scores[spike_scores['combined_score'] > threshold].copy()
        
        # 원본 데이터 병합
        if not spikes.empty:
            spikes = spikes.merge(self.df, on='timestamp', how='left')
            spikes['spike_type'] = 'multi_indicator'
            spikes['spike_magnitude'] = spikes['combined_score']
        
        return spikes
    
    def detect_correlation_spike(self, col1, col2, threshold=2.5):
        """
        상관관계 스파이크 감지
        두 변수가 동시에 급등/급락할 때 감지
        
        Args:
            col1: 첫 번째 컬럼
            col2: 두 번째 컬럼
            threshold: Z-score 임계값
            
        Returns:
            DataFrame: 두 변수가 동시에 스파이크를 보이는 시점
        """
        zscore1 = f'{col1}_zscore'
        zscore2 = f'{col2}_zscore'
        
        # 두 변수 모두 임계값 초과
        condition = (self.df[zscore1].abs() > threshold) & (self.df[zscore2].abs() > threshold)
        spikes = self.df[condition].copy()
        
        if not spikes.empty:
            spikes['spike_type'] = 'correlated_spike'
            spikes['spike_magnitude'] = (spikes[zscore1].abs() + spikes[zscore2].abs()) / 2
            spikes['spike_columns'] = f'{col1} & {col2}'
        
        return spikes
    
    def detect_telegram_whale_combined_spike(self, telegram_col='message_count', whale_col='tx_frequency', threshold=2.0):
        """
        텔레그램과 고래 거래의 동시 스파이크 감지 (Critical 알람용)
        
        Args:
            telegram_col: 텔레그램 활동 컬럼 (기본: message_count)
            whale_col: 고래 거래 컬럼 (기본: tx_frequency)
            threshold: Z-score 임계값 (더 낮게 설정하여 민감하게 감지)
            
        Returns:
            DataFrame: 텔레그램 & 고래 거래가 동시에 스파이크를 보이는 시점
        """
        telegram_zscore = f'{telegram_col}_zscore'
        whale_zscore = f'{whale_col}_zscore'
        
        # 둘 다 존재하는지 확인
        if telegram_col not in self.df.columns or whale_col not in self.df.columns:
            return pd.DataFrame()
        
        # Z-score 컬럼이 없으면 계산
        if telegram_zscore not in self.df.columns:
            mean = self.df[telegram_col].rolling(window=self.window, min_periods=1).mean()
            std = self.df[telegram_col].rolling(window=self.window, min_periods=1).std()
            self.df[telegram_zscore] = (self.df[telegram_col] - mean) / (std + 1e-10)
        
        if whale_zscore not in self.df.columns:
            mean = self.df[whale_col].rolling(window=self.window, min_periods=1).mean()
            std = self.df[whale_col].rolling(window=self.window, min_periods=1).std()
            self.df[whale_zscore] = (self.df[whale_col] - mean) / (std + 1e-10)
        
        # 둘 다 양의 방향으로 임계값 초과 (동시 급증)
        condition = (self.df[telegram_zscore] > threshold) & (self.df[whale_zscore] > threshold)
        spikes = self.df[condition].copy()
        
        if not spikes.empty:
            spikes['spike_type'] = 'critical_telegram_whale_spike'
            spikes['spike_magnitude'] = (spikes[telegram_zscore] + spikes[whale_zscore]) / 2
            spikes['spike_columns'] = f'{telegram_col} & {whale_col}'
            spikes['alert_level'] = 'critical'
            
            # 추가 메타데이터
            spikes['telegram_zscore_value'] = spikes[telegram_zscore]
            spikes['whale_zscore_value'] = spikes[whale_zscore]
            spikes['telegram_value'] = spikes[telegram_col]
            spikes['whale_value'] = spikes[whale_col]
        
        return spikes
    
    def generate_alert(self, spike_data, alert_level='high'):
        """
        스파이크 데이터를 알람 형식으로 변환
        
        Args:
            spike_data: 감지된 스파이크 데이터프레임
            alert_level: 알람 레벨 ('low', 'medium', 'high')
            
        Returns:
            DataFrame: 알람 데이터
        """
        if spike_data.empty:
            return pd.DataFrame()
        
        alerts = spike_data.copy()
        alerts['alert_level'] = alert_level
        alerts['alert_time'] = datetime.now()
        
        # 알람 메시지 생성
        def create_message(row):
            if 'spike_column' in row:
                return f"{row['spike_type']} detected in {row['spike_column']} " \
                       f"(magnitude: {row['spike_magnitude']:.2f})"
            elif 'spike_columns' in row:
                return f"{row['spike_type']} detected in {row['spike_columns']} " \
                       f"(magnitude: {row['spike_magnitude']:.2f})"
            else:
                return f"{row.get('spike_type', 'Unknown spike')} detected"
        
        alerts['alert_message'] = alerts.apply(create_message, axis=1)
        
        return alerts


class RealTimeSpikeMonitor:
    """실시간 스파이크 모니터링"""
    
    def __init__(self, df, config=None):
        """
        Args:
            df: 데이터프레임
            config: 감지 설정 딕셔너리
        """
        self.df = df
        self.detector = SpikeDetector(df)
        
        # 기본 설정
        self.config = config or {
            'zscore_threshold': 2.5,
            'ma_threshold_pct': 50,
            'roc_threshold_pct': 30,
            'multi_threshold': 0.7,
            'monitor_columns': ['message_count', 'ETH_close', 'tx_frequency']
        }
        
        self.alert_history = []
    
    def check_all_spikes(self):
        """
        모든 스파이크 감지 메서드를 실행하고 결과 반환
        
        Returns:
            dict: 각 감지 유형별 스파이크 데이터
        """
        results = {}
        
        for col in self.config['monitor_columns']:
            if col in self.df.columns:
                # Z-score 스파이크
                zscore_spikes = self.detector.detect_zscore_spike(
                    col, self.config['zscore_threshold']
                )
                if not zscore_spikes.empty:
                    results[f'{col}_zscore'] = zscore_spikes
                
                # 이동평균 스파이크
                ma_spikes = self.detector.detect_moving_average_spike(
                    col, self.config['ma_threshold_pct']
                )
                if not ma_spikes.empty:
                    results[f'{col}_ma'] = ma_spikes
                
                # 변화율 스파이크
                roc_spikes = self.detector.detect_rate_of_change_spike(
                    col, window=3, threshold_pct=self.config['roc_threshold_pct']
                )
                if not roc_spikes.empty:
                    results[f'{col}_roc'] = roc_spikes
        
        # 다중 지표 스파이크
        multi_spikes = self.detector.detect_multi_indicator_spike(
            self.config['monitor_columns'],
            threshold=self.config['multi_threshold']
        )
        if not multi_spikes.empty:
            results['multi_indicator'] = multi_spikes
        
        # 상관관계 스파이크 (예: 메시지 수 & ETH 가격)
        if 'message_count' in self.df.columns and 'ETH_close' in self.df.columns:
            corr_spikes = self.detector.detect_correlation_spike(
                'message_count', 'ETH_close', self.config['zscore_threshold']
            )
            if not corr_spikes.empty:
                results['correlation'] = corr_spikes
        
        # === 텔레그램 & 고래 거래 동시 스파이크 (CRITICAL) ===
        if 'message_count' in self.df.columns and 'tx_frequency' in self.df.columns:
            telegram_whale_spikes = self.detector.detect_telegram_whale_combined_spike(
                'message_count', 'tx_frequency', threshold=2.0
            )
            if not telegram_whale_spikes.empty:
                results['telegram_whale_critical'] = telegram_whale_spikes
        
        return results
    
    def get_recent_alerts(self, hours=24):
        """
        최근 N시간 동안의 알람 가져오기
        
        Args:
            hours: 조회할 시간
            
        Returns:
            DataFrame: 최근 알람들
        """
        if self.df.empty or 'timestamp' not in self.df.columns:
            return pd.DataFrame()
        
        cutoff_time = self.df['timestamp'].max() - timedelta(hours=hours)
        recent_df = self.df[self.df['timestamp'] >= cutoff_time]
        
        # 최근 데이터에 대해 스파이크 감지
        temp_detector = SpikeDetector(recent_df)
        all_alerts = []
        
        for col in self.config['monitor_columns']:
            if col in recent_df.columns:
                spikes = temp_detector.detect_zscore_spike(col, self.config['zscore_threshold'])
                if not spikes.empty:
                    alerts = temp_detector.generate_alert(spikes, alert_level='high')
                    all_alerts.append(alerts)
        
        if all_alerts:
            return pd.concat(all_alerts, ignore_index=True).sort_values('timestamp', ascending=False)
        else:
            return pd.DataFrame()


if __name__ == '__main__':
    # 테스트
    import sys
    sys.path.append('/Volumes/T7/class/2025-FALL/big_data')
    
    # 전처리된 데이터 로드
    df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print("=== 스파이크 감지 테스트 ===\n")
    
    # 모니터 초기화
    monitor = RealTimeSpikeMonitor(df)
    
    # 모든 스파이크 감지
    results = monitor.check_all_spikes()
    
    print(f"감지된 스파이크 유형: {len(results)}개\n")
    
    for spike_type, spike_data in results.items():
        print(f"{spike_type}: {len(spike_data)}개 스파이크 감지")
        if len(spike_data) > 0:
            print(f"  첫 번째: {spike_data.iloc[0]['timestamp']}")
            print(f"  마지막: {spike_data.iloc[-1]['timestamp']}")
        print()
    
    # 최근 24시간 알람
    print("\n=== 최근 24시간 알람 ===")
    recent_alerts = monitor.get_recent_alerts(hours=24)
    if not recent_alerts.empty:
        print(f"총 {len(recent_alerts)}개의 알람")
        print(recent_alerts[['timestamp', 'alert_message', 'alert_level']].head(10))
    else:
        print("최근 알람이 없습니다.")

