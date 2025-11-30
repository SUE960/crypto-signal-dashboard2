"""
실시간 Spike 알람 모니터링 시스템

텔레그램, 고래 거래, 트위터 인플루언서 데이터를 
실시간으로 모니터링하고 Critical 알람 발생 시 즉시 알림
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class RealTimeSpikeMonitor:
    """실시간 Spike 모니터링 시스템"""
    
    def __init__(self, merged_data_path, config_path=None):
        """
        Args:
            merged_data_path: 병합된 데이터 CSV 경로
            config_path: 설정 파일 경로 (JSON)
        """
        print("실시간 모니터 초기화 중...")
        
        # 데이터 로드
        self.merged_df = pd.read_csv(merged_data_path)
        self.merged_df['timestamp'] = pd.to_datetime(self.merged_df['timestamp'])
        
        # 설정 로드
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # 기본 설정
            self.config = {
                'spike_threshold': 2.0,
                'window_hours': 24,
                'check_interval_seconds': 60,
                'alert_cooldown_hours': 1,
                'critical_priority_threshold': 10,
                'telegram_weight': 0.3,
                'whale_weight': 0.5,
                'twitter_weight': 0.2
            }
        
        # 알람 히스토리
        self.alert_history = []
        self.last_alert_time = {}
        
        print(f"✓ 데이터 로드 완료: {len(self.merged_df)} rows")
        print(f"✓ 설정: {self.config}")
    
    def calculate_zscore(self, series, window=24):
        """
        Z-score 계산
        
        Args:
            series: 시계열 데이터
            window: 이동평균 윈도우
            
        Returns:
            Series: Z-score
        """
        mean = series.rolling(window=window, min_periods=1).mean()
        std = series.rolling(window=window, min_periods=1).std()
        zscore = (series - mean) / (std + 1e-10)
        return zscore
    
    def check_spike(self, recent_data):
        """
        스파이크 감지
        
        Args:
            recent_data: 최근 데이터 DataFrame
            
        Returns:
            dict: 스파이크 정보
        """
        if recent_data.empty:
            return None
        
        latest = recent_data.iloc[-1]
        
        spike_info = {
            'timestamp': latest['timestamp'],
            'telegram_spike': False,
            'whale_spike': False,
            'twitter_spike': False,
            'telegram_zscore': 0,
            'whale_zscore': 0,
            'twitter_zscore': 0,
            'priority_score': 0,
            'alert_level': 'LOW',
            'reasons': []
        }
        
        threshold = self.config['spike_threshold']
        
        # 텔레그램 스파이크 체크
        if 'telegram_message_count_zscore' in recent_data.columns:
            telegram_z = latest.get('telegram_message_count_zscore', 0)
            if telegram_z > threshold:
                spike_info['telegram_spike'] = True
                spike_info['telegram_zscore'] = telegram_z
                spike_info['priority_score'] += 2
                spike_info['reasons'].append(f"텔레그램 메시지 급증 (z={telegram_z:.2f})")
        
        # 고래 거래 스파이크 체크
        if 'whale_tx_count_zscore' in recent_data.columns:
            whale_z = latest.get('whale_tx_count_zscore', 0)
            if whale_z > threshold:
                spike_info['whale_spike'] = True
                spike_info['whale_zscore'] = whale_z
                spike_info['priority_score'] += 3
                spike_info['reasons'].append(f"고래 거래 급증 (z={whale_z:.2f})")
        
        # 트위터 스파이크 체크
        if 'twitter_engagement_zscore' in recent_data.columns:
            twitter_z = latest.get('twitter_engagement_zscore', 0)
            if twitter_z > threshold:
                spike_info['twitter_spike'] = True
                spike_info['twitter_zscore'] = twitter_z
                spike_info['priority_score'] += 2
                spike_info['reasons'].append(f"트위터 인플루언서 활동 급증 (z={twitter_z:.2f})")
        
        # 복합 스파이크 체크
        if spike_info['telegram_spike'] and spike_info['whale_spike']:
            spike_info['priority_score'] += 5
            spike_info['reasons'].append("⚠️ 텔레그램+고래 동시 급증")
        
        if spike_info['twitter_spike'] and spike_info['whale_spike']:
            spike_info['priority_score'] += 4
            spike_info['reasons'].append("⚠️ 트위터+고래 동시 급증")
        
        if spike_info['telegram_spike'] and spike_info['whale_spike'] and spike_info['twitter_spike']:
            spike_info['priority_score'] += 10
            spike_info['reasons'].append("🚨 3개 소스 모두 급증 (CRITICAL)")
        
        # 알람 레벨 결정
        if spike_info['priority_score'] >= 10:
            spike_info['alert_level'] = 'CRITICAL'
        elif spike_info['priority_score'] >= 5:
            spike_info['alert_level'] = 'HIGH'
        elif spike_info['priority_score'] >= 2:
            spike_info['alert_level'] = 'MEDIUM'
        
        # 데이터 추가
        spike_info['telegram_msgs'] = latest.get('telegram_message_count', 0)
        spike_info['whale_txs'] = latest.get('whale_tx_count', 0)
        spike_info['twitter_engagement'] = latest.get('twitter_engagement', 0)
        
        return spike_info if spike_info['priority_score'] > 0 else None
    
    def should_send_alert(self, spike_info):
        """
        알람을 보내야 하는지 판단 (중복 방지)
        
        Args:
            spike_info: 스파이크 정보
            
        Returns:
            bool: True면 알람 전송
        """
        alert_key = spike_info['alert_level']
        
        # 쿨다운 체크
        if alert_key in self.last_alert_time:
            time_since_last = datetime.now() - self.last_alert_time[alert_key]
            cooldown = timedelta(hours=self.config['alert_cooldown_hours'])
            
            if time_since_last < cooldown:
                return False
        
        return True
    
    def send_alert(self, spike_info):
        """
        알람 전송 (콘솔 출력 + 로그 저장)
        
        Args:
            spike_info: 스파이크 정보
        """
        # 콘솔 출력
        print("\n" + "=" * 100)
        print(f"🚨 [{spike_info['alert_level']}] SPIKE ALERT 🚨")
        print("=" * 100)
        print(f"시간: {spike_info['timestamp']}")
        print(f"우선순위 점수: {spike_info['priority_score']}")
        print(f"\n사유:")
        for reason in spike_info['reasons']:
            print(f"  - {reason}")
        print(f"\n데이터:")
        print(f"  - 텔레그램 메시지: {spike_info['telegram_msgs']:.0f} (z={spike_info['telegram_zscore']:.2f})")
        print(f"  - 고래 거래: {spike_info['whale_txs']:.0f} (z={spike_info['whale_zscore']:.2f})")
        print(f"  - 트위터 인게이지먼트: {spike_info['twitter_engagement']:.0f} (z={spike_info['twitter_zscore']:.2f})")
        print("=" * 100 + "\n")
        
        # 알람 히스토리에 추가
        self.alert_history.append({
            'timestamp': spike_info['timestamp'],
            'alert_time': datetime.now(),
            'level': spike_info['alert_level'],
            'priority': spike_info['priority_score'],
            'reasons': '; '.join(spike_info['reasons'])
        })
        
        # 마지막 알람 시간 업데이트
        self.last_alert_time[spike_info['alert_level']] = datetime.now()
    
    def monitor_once(self):
        """
        한 번의 모니터링 실행
        
        Returns:
            dict: 스파이크 정보 (있으면)
        """
        # 최근 데이터 가져오기 (윈도우 크기만큼)
        window_hours = self.config['window_hours']
        cutoff_time = self.merged_df['timestamp'].max() - timedelta(hours=window_hours)
        recent_data = self.merged_df[self.merged_df['timestamp'] >= cutoff_time].copy()
        
        if recent_data.empty:
            return None
        
        # Z-score 계산 (없으면)
        for col in ['telegram_message_count', 'whale_tx_count', 'twitter_engagement']:
            if col in recent_data.columns:
                zscore_col = f'{col}_zscore'
                if zscore_col not in recent_data.columns:
                    recent_data[zscore_col] = self.calculate_zscore(
                        recent_data[col], 
                        window=min(window_hours, len(recent_data))
                    )
        
        # 스파이크 감지
        spike_info = self.check_spike(recent_data)
        
        if spike_info:
            # CRITICAL 또는 HIGH만 알람
            if spike_info['priority_score'] >= self.config['critical_priority_threshold']:
                if self.should_send_alert(spike_info):
                    self.send_alert(spike_info)
        
        return spike_info
    
    def start_monitoring(self, duration_minutes=None):
        """
        실시간 모니터링 시작
        
        Args:
            duration_minutes: 모니터링 지속 시간 (None이면 무한)
        """
        print("\n" + "=" * 100)
        print("실시간 Spike 모니터링 시작")
        print("=" * 100)
        print(f"체크 간격: {self.config['check_interval_seconds']}초")
        print(f"스파이크 임계값: {self.config['spike_threshold']}σ")
        print(f"알람 쿨다운: {self.config['alert_cooldown_hours']}시간")
        
        if duration_minutes:
            print(f"지속 시간: {duration_minutes}분")
        else:
            print("지속 시간: 무한 (Ctrl+C로 중단)")
        
        print("=" * 100 + "\n")
        
        start_time = datetime.now()
        check_count = 0
        
        try:
            while True:
                check_count += 1
                current_time = datetime.now()
                
                print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 체크 #{check_count}...", end=' ')
                
                spike_info = self.monitor_once()
                
                if spike_info:
                    print(f"✓ 스파이크 감지! (우선순위: {spike_info['priority_score']}, 레벨: {spike_info['alert_level']})")
                else:
                    print("✓ 정상")
                
                # 지속 시간 체크
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        print("\n모니터링 지속 시간 종료")
                        break
                
                # 대기
                time.sleep(self.config['check_interval_seconds'])
        
        except KeyboardInterrupt:
            print("\n\n사용자에 의해 모니터링 중단")
        
        # 요약
        print("\n" + "=" * 100)
        print("모니터링 요약")
        print("=" * 100)
        print(f"총 체크 횟수: {check_count}")
        print(f"총 알람 발생: {len(self.alert_history)}회")
        
        if self.alert_history:
            print(f"\n알람 히스토리:")
            for alert in self.alert_history:
                print(f"  [{alert['alert_time'].strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"{alert['level']} - {alert['reasons']}")
        
        print("=" * 100)
    
    def save_alert_history(self, output_path):
        """
        알람 히스토리 저장
        
        Args:
            output_path: 출력 파일 경로
        """
        if self.alert_history:
            alerts_df = pd.DataFrame(self.alert_history)
            alerts_df.to_csv(output_path, index=False)
            print(f"✓ 알람 히스토리 저장: {output_path}")
        else:
            print("⚠ 저장할 알람 히스토리가 없습니다.")


def create_monitoring_config(output_path='/Volumes/T7/class/2025-FALL/big_data/data/monitor_config.json'):
    """
    모니터링 설정 파일 생성
    
    Args:
        output_path: 출력 파일 경로
    """
    config = {
        "spike_threshold": 2.0,
        "window_hours": 24,
        "check_interval_seconds": 60,
        "alert_cooldown_hours": 1,
        "critical_priority_threshold": 10,
        "telegram_weight": 0.3,
        "whale_weight": 0.5,
        "twitter_weight": 0.2,
        "description": {
            "spike_threshold": "스파이크 판단 Z-score 임계값",
            "window_hours": "이동평균 계산 윈도우 (시간)",
            "check_interval_seconds": "모니터링 체크 간격 (초)",
            "alert_cooldown_hours": "동일 레벨 알람 재전송 방지 시간 (시간)",
            "critical_priority_threshold": "CRITICAL 알람 최소 우선순위 점수",
            "telegram_weight": "텔레그램 가중치",
            "whale_weight": "고래 거래 가중치",
            "twitter_weight": "트위터 가중치"
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 모니터링 설정 파일 생성: {output_path}")


if __name__ == '__main__':
    import sys
    
    # 설정 파일 생성
    CONFIG_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/monitor_config.json'
    if not Path(CONFIG_PATH).exists():
        create_monitoring_config(CONFIG_PATH)
    
    # 모니터 초기화
    MERGED_DATA_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/multi_source_merged_data.csv'
    monitor = RealTimeSpikeMonitor(MERGED_DATA_PATH, CONFIG_PATH)
    
    # 테스트 모드 vs 실시간 모드
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n📊 테스트 모드: 한 번만 체크")
        spike_info = monitor.monitor_once()
        if spike_info:
            print("\n✓ 스파이크 감지됨")
        else:
            print("\n✓ 스파이크 없음")
    else:
        # 실시간 모니터링 시작 (10분간 테스트)
        monitor.start_monitoring(duration_minutes=10)
        
        # 알람 히스토리 저장
        monitor.save_alert_history(
            '/Volumes/T7/class/2025-FALL/big_data/data/realtime_alert_history.csv'
        )


