"""
알람 시스템

스파이크 감지 시 알람을 생성하고 이력을 관리합니다.
"""

import pandas as pd
import os
from datetime import datetime
import json


class AlertSystem:
    """알람 시스템 클래스"""
    
    def __init__(self, alert_history_path='/Volumes/T7/class/2025-FALL/big_data/data/alert_history.csv'):
        """
        Args:
            alert_history_path: 알람 이력 파일 경로
        """
        self.alert_history_path = alert_history_path
        self.load_history()
    
    def load_history(self):
        """알람 이력 로드"""
        if os.path.exists(self.alert_history_path):
            self.history = pd.read_csv(self.alert_history_path)
            self.history['timestamp'] = pd.to_datetime(self.history['timestamp'])
            self.history['alert_time'] = pd.to_datetime(self.history['alert_time'])
        else:
            self.history = pd.DataFrame(columns=[
                'timestamp', 'alert_time', 'alert_level', 'alert_type',
                'alert_message', 'spike_magnitude', 'resolved'
            ])
    
    def save_history(self):
        """알람 이력 저장"""
        os.makedirs(os.path.dirname(self.alert_history_path), exist_ok=True)
        self.history.to_csv(self.alert_history_path, index=False)
    
    def add_alert(self, timestamp, alert_level, alert_type, message, spike_magnitude=0):
        """
        새 알람 추가
        
        Args:
            timestamp: 이벤트 발생 시각
            alert_level: 알람 레벨 ('low', 'medium', 'high', 'critical')
            alert_type: 알람 유형
            message: 알람 메시지
            spike_magnitude: 스파이크 크기
        """
        new_alert = pd.DataFrame([{
            'timestamp': timestamp,
            'alert_time': datetime.now(),
            'alert_level': alert_level,
            'alert_type': alert_type,
            'alert_message': message,
            'spike_magnitude': spike_magnitude,
            'resolved': False
        }])
        
        self.history = pd.concat([self.history, new_alert], ignore_index=True)
        self.save_history()
    
    def add_alerts_from_spikes(self, spike_data, alert_type):
        """
        스파이크 데이터에서 알람 생성
        
        Args:
            spike_data: 스파이크 데이터프레임
            alert_type: 알람 유형
        """
        if spike_data.empty:
            return
        
        for _, row in spike_data.iterrows():
            # 알람 레벨 결정 (spike_magnitude 기준)
            magnitude = row.get('spike_magnitude', 0)
            if magnitude > 5:
                level = 'critical'
            elif magnitude > 3:
                level = 'high'
            elif magnitude > 2:
                level = 'medium'
            else:
                level = 'low'
            
            message = row.get('alert_message', f"{alert_type} detected")
            
            self.add_alert(
                timestamp=row['timestamp'],
                alert_level=level,
                alert_type=alert_type,
                message=message,
                spike_magnitude=magnitude
            )
    
    def get_recent_alerts(self, hours=24, level=None):
        """
        최근 알람 조회
        
        Args:
            hours: 조회할 시간 범위
            level: 특정 레벨만 조회 (None이면 전체)
            
        Returns:
            DataFrame: 알람 리스트
        """
        if self.history.empty:
            return pd.DataFrame()
        
        cutoff_time = datetime.now() - pd.Timedelta(hours=hours)
        recent = self.history[self.history['alert_time'] >= cutoff_time].copy()
        
        if level:
            recent = recent[recent['alert_level'] == level]
        
        return recent.sort_values('alert_time', ascending=False)
    
    def get_unresolved_alerts(self):
        """미해결 알람 조회"""
        if self.history.empty:
            return pd.DataFrame()
        
        return self.history[self.history['resolved'] == False].sort_values(
            'alert_time', ascending=False
        )
    
    def resolve_alert(self, alert_index):
        """
        알람 해결 처리
        
        Args:
            alert_index: 알람 인덱스
        """
        if alert_index in self.history.index:
            self.history.loc[alert_index, 'resolved'] = True
            self.save_history()
    
    def get_alert_stats(self):
        """
        알람 통계
        
        Returns:
            dict: 통계 정보
        """
        if self.history.empty:
            return {
                'total_alerts': 0,
                'unresolved': 0,
                'by_level': {},
                'by_type': {}
            }
        
        stats = {
            'total_alerts': len(self.history),
            'unresolved': len(self.history[self.history['resolved'] == False]),
            'by_level': self.history['alert_level'].value_counts().to_dict(),
            'by_type': self.history['alert_type'].value_counts().to_dict()
        }
        
        return stats
    
    def clear_old_alerts(self, days=30):
        """
        오래된 알람 삭제
        
        Args:
            days: 보관 기간 (일)
        """
        if self.history.empty:
            return
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        self.history = self.history[self.history['alert_time'] >= cutoff_date]
        self.save_history()
        
        print(f"{days}일 이전의 알람을 삭제했습니다.")


class AlertConfig:
    """알람 설정 관리"""
    
    def __init__(self, config_path='/Volumes/T7/class/2025-FALL/big_data/data/alert_config.json'):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config_path = config_path
        self.load_config()
    
    def load_config(self):
        """설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # 기본 설정
            self.config = {
                'enabled': True,
                'zscore_threshold': 2.5,
                'ma_threshold_pct': 50,
                'roc_threshold_pct': 30,
                'multi_threshold': 0.7,
                'monitor_columns': ['message_count', 'ETH_close', 'tx_frequency'],
                'alert_conditions': {
                    'community_surge_and_volume': {
                        'enabled': True,
                        'condition': 'message_count_zscore > 3 AND tx_frequency_zscore > 2'
                    },
                    'sentiment_drop_and_price_drop': {
                        'enabled': True,
                        'condition': 'avg_sentiment < -0.5 AND ETH_price_change_pct < -5'
                    }
                }
            }
            self.save_config()
    
    def save_config(self):
        """설정 저장"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_config(self, key, value):
        """
        설정 업데이트
        
        Args:
            key: 설정 키
            value: 설정 값
        """
        self.config[key] = value
        self.save_config()
    
    def get_config(self, key=None):
        """
        설정 조회
        
        Args:
            key: 조회할 키 (None이면 전체)
            
        Returns:
            설정 값
        """
        if key:
            return self.config.get(key)
        return self.config


if __name__ == '__main__':
    # 테스트
    alert_system = AlertSystem()
    
    # 테스트 알람 추가
    alert_system.add_alert(
        timestamp=datetime.now(),
        alert_level='high',
        alert_type='community_surge',
        message='텔레그램 메시지 수가 급증했습니다',
        spike_magnitude=3.5
    )
    
    print("=== 알람 시스템 테스트 ===\n")
    
    # 최근 알람
    recent = alert_system.get_recent_alerts(hours=24)
    print(f"최근 24시간 알람: {len(recent)}개")
    if not recent.empty:
        print(recent[['timestamp', 'alert_level', 'alert_message']].head())
    
    # 통계
    stats = alert_system.get_alert_stats()
    print(f"\n알람 통계:")
    print(f"  총 알람: {stats['total_alerts']}")
    print(f"  미해결: {stats['unresolved']}")
    print(f"  레벨별: {stats['by_level']}")





