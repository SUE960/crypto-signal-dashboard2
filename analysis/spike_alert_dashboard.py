"""
Spike 알람 대시보드 및 시각화

텔레그램, 고래 거래, 트위터 인플루언서 데이터의 
통합 스파이크 알람을 시각화하고 실시간 모니터링 제공
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


class SpikeAlertDashboard:
    """Spike 알람 대시보드 클래스"""
    
    def __init__(self, merged_data_path, alerts_path):
        """
        Args:
            merged_data_path: 병합된 데이터 CSV 경로
            alerts_path: 알람 데이터 CSV 경로
        """
        print("데이터 로딩 중...")
        self.merged_df = pd.read_csv(merged_data_path)
        self.merged_df['timestamp'] = pd.to_datetime(self.merged_df['timestamp'])
        
        self.alerts_df = pd.read_csv(alerts_path)
        self.alerts_df['timestamp'] = pd.to_datetime(self.alerts_df['timestamp'])
        
        print(f"✓ 병합 데이터: {len(self.merged_df)} rows")
        print(f"✓ 알람 데이터: {len(self.alerts_df)} rows")
    
    def plot_correlation_heatmap(self, output_path=None):
        """
        상관관계 히트맵 생성
        
        Args:
            output_path: 출력 파일 경로 (None이면 표시만)
        """
        # 주요 컬럼만 선택
        key_cols = [
            'telegram_message_count', 'telegram_avg_sentiment',
            'whale_tx_count', 'whale_volume_sum',
            'twitter_post_count', 'twitter_engagement', 'twitter_sentiment'
        ]
        
        # 존재하는 컬럼만 필터링
        available_cols = [col for col in key_cols if col in self.merged_df.columns]
        
        if len(available_cols) < 2:
            print("⚠ 상관관계 분석에 필요한 컬럼이 부족합니다.")
            return
        
        # 상관관계 계산
        corr_data = self.merged_df[available_cols].corr()
        
        # 히트맵 생성
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        
        sns.heatmap(corr_data, mask=mask, annot=True, fmt='.3f', 
                    cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        
        plt.title('다중 소스 상관관계 히트맵', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ 히트맵 저장: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_time_series_with_spikes(self, output_path=None, recent_days=90):
        """
        시계열 데이터와 스파이크 표시
        
        Args:
            output_path: 출력 파일 경로
            recent_days: 최근 N일 데이터만 표시
        """
        # 최근 데이터 필터링
        cutoff_date = self.merged_df['timestamp'].max() - timedelta(days=recent_days)
        recent_data = self.merged_df[self.merged_df['timestamp'] >= cutoff_date].copy()
        recent_alerts = self.alerts_df[self.alerts_df['timestamp'] >= cutoff_date].copy()
        
        if recent_data.empty:
            print("⚠ 표시할 데이터가 없습니다.")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
        
        # 1. 텔레그램 메시지 수
        if 'telegram_message_count' in recent_data.columns:
            ax1 = axes[0]
            ax1.plot(recent_data['timestamp'], recent_data['telegram_message_count'], 
                    label='텔레그램 메시지', color='#3498db', linewidth=1.5)
            
            # 스파이크 표시
            telegram_spikes = recent_alerts[
                recent_alerts['reasons'].str.contains('텔레그램', na=False)
            ]
            if not telegram_spikes.empty:
                ax1.scatter(telegram_spikes['timestamp'], 
                          telegram_spikes['telegram_msgs'],
                          color='red', s=100, marker='o', alpha=0.6, 
                          label='스파이크', zorder=5)
            
            ax1.set_ylabel('메시지 수', fontsize=12, fontweight='bold')
            ax1.set_title('텔레그램 활동', fontsize=14, fontweight='bold', pad=10)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
        
        # 2. 고래 거래 빈도
        if 'whale_tx_count' in recent_data.columns:
            ax2 = axes[1]
            ax2.plot(recent_data['timestamp'], recent_data['whale_tx_count'], 
                    label='고래 거래 빈도', color='#e74c3c', linewidth=1.5)
            
            # 스파이크 표시
            whale_spikes = recent_alerts[
                recent_alerts['reasons'].str.contains('고래', na=False)
            ]
            if not whale_spikes.empty:
                ax2.scatter(whale_spikes['timestamp'], 
                          whale_spikes['whale_txs'],
                          color='darkred', s=100, marker='o', alpha=0.6, 
                          label='스파이크', zorder=5)
            
            ax2.set_ylabel('거래 빈도', fontsize=12, fontweight='bold')
            ax2.set_title('고래 거래 활동', fontsize=14, fontweight='bold', pad=10)
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3)
        
        # 3. 트위터 인게이지먼트
        if 'twitter_engagement' in recent_data.columns:
            ax3 = axes[2]
            ax3.plot(recent_data['timestamp'], recent_data['twitter_engagement'], 
                    label='트위터 인게이지먼트', color='#1da1f2', linewidth=1.5)
            
            # 스파이크 표시
            twitter_spikes = recent_alerts[
                recent_alerts['reasons'].str.contains('트위터', na=False)
            ]
            if not twitter_spikes.empty:
                ax3.scatter(twitter_spikes['timestamp'], 
                          twitter_spikes['twitter_engagement'],
                          color='purple', s=100, marker='o', alpha=0.6, 
                          label='스파이크', zorder=5)
            
            ax3.set_ylabel('인게이지먼트 점수', fontsize=12, fontweight='bold')
            ax3.set_title('트위터 인플루언서 활동', fontsize=14, fontweight='bold', pad=10)
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3)
        
        ax3.set_xlabel('날짜', fontsize=12, fontweight='bold')
        
        plt.suptitle(f'최근 {recent_days}일 활동 및 스파이크 감지', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ 시계열 차트 저장: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_alert_statistics(self, output_path=None):
        """
        알람 통계 시각화
        
        Args:
            output_path: 출력 파일 경로
        """
        if self.alerts_df.empty:
            print("⚠ 알람 데이터가 없습니다.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 알람 레벨별 분포
        ax1 = axes[0, 0]
        level_counts = self.alerts_df['alert_level'].value_counts()
        colors = {'CRITICAL': '#e74c3c', 'HIGH': '#f39c12', 
                 'MEDIUM': '#f1c40f', 'LOW': '#95a5a6'}
        level_colors = [colors.get(level, '#95a5a6') for level in level_counts.index]
        
        ax1.bar(level_counts.index, level_counts.values, color=level_colors, alpha=0.8)
        ax1.set_title('알람 레벨별 분포', fontsize=14, fontweight='bold', pad=10)
        ax1.set_ylabel('개수', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 값 표시
        for i, (level, count) in enumerate(level_counts.items()):
            ax1.text(i, count, f'{count}', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11)
        
        # 2. 우선순위 점수 분포
        ax2 = axes[0, 1]
        ax2.hist(self.alerts_df['priority_score'], bins=30, 
                color='#3498db', alpha=0.7, edgecolor='black')
        ax2.set_title('우선순위 점수 분포', fontsize=14, fontweight='bold', pad=10)
        ax2.set_xlabel('우선순위 점수', fontsize=12, fontweight='bold')
        ax2.set_ylabel('빈도', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. 시간대별 알람 발생 빈도
        ax3 = axes[1, 0]
        self.alerts_df['hour'] = self.alerts_df['timestamp'].dt.hour
        hourly_counts = self.alerts_df['hour'].value_counts().sort_index()
        
        ax3.plot(hourly_counts.index, hourly_counts.values, 
                marker='o', linewidth=2, markersize=6, color='#9b59b6')
        ax3.set_title('시간대별 알람 발생 빈도', fontsize=14, fontweight='bold', pad=10)
        ax3.set_xlabel('시간 (시)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('알람 수', fontsize=12, fontweight='bold')
        ax3.set_xticks(range(0, 24, 2))
        ax3.grid(True, alpha=0.3)
        
        # 4. 월별 알람 추이
        ax4 = axes[1, 1]
        self.alerts_df['month'] = self.alerts_df['timestamp'].dt.to_period('M')
        monthly_counts = self.alerts_df['month'].value_counts().sort_index()
        
        ax4.bar(range(len(monthly_counts)), monthly_counts.values, 
               color='#16a085', alpha=0.8)
        ax4.set_title('월별 알람 발생 추이', fontsize=14, fontweight='bold', pad=10)
        ax4.set_xlabel('월', fontsize=12, fontweight='bold')
        ax4.set_ylabel('알람 수', fontsize=12, fontweight='bold')
        ax4.set_xticks(range(len(monthly_counts)))
        ax4.set_xticklabels([str(m) for m in monthly_counts.index], 
                           rotation=45, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('알람 통계 대시보드', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ 통계 차트 저장: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_lag_correlation(self, lag_data_path, output_path=None):
        """
        시차 상관관계 시각화
        
        Args:
            lag_data_path: 시차 상관관계 데이터 경로 (telegram_to_whale, twitter_to_whale)
            output_path: 출력 파일 경로
        """
        try:
            lag_df = pd.read_csv(lag_data_path)
            
            if lag_df.empty:
                print("⚠ 시차 상관관계 데이터가 없습니다.")
                return
            
            plt.figure(figsize=(12, 6))
            
            plt.plot(lag_df['lag_hours'], lag_df['correlation'], 
                    marker='o', linewidth=2, markersize=8, color='#e67e22')
            
            # 최대 상관관계 표시
            max_idx = lag_df['correlation'].abs().idxmax()
            max_lag = lag_df.loc[max_idx, 'lag_hours']
            max_corr = lag_df.loc[max_idx, 'correlation']
            
            plt.axvline(max_lag, color='red', linestyle='--', alpha=0.7, 
                       label=f'최대 상관관계: {max_lag}h (r={max_corr:.3f})')
            plt.axhline(0, color='gray', linestyle='-', alpha=0.3)
            
            plt.xlabel('시차 (시간)', fontsize=12, fontweight='bold')
            plt.ylabel('상관계수', fontsize=12, fontweight='bold')
            plt.title('시차 상관관계 분석', fontsize=14, fontweight='bold', pad=15)
            plt.legend(loc='best', fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                print(f"✓ 시차 상관관계 차트 저장: {output_path}")
            else:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            print(f"⚠ 시차 상관관계 차트 생성 실패: {e}")
    
    def generate_alert_report(self, output_path, top_n=50):
        """
        알람 리포트 생성 (텍스트)
        
        Args:
            output_path: 출력 파일 경로
            top_n: 상위 N개 알람 포함
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write(" " * 30 + "다중 소스 Spike 알람 리포트\n")
            f.write("=" * 100 + "\n\n")
            
            f.write(f"생성 날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"분석 기간: {self.alerts_df['timestamp'].min()} ~ {self.alerts_df['timestamp'].max()}\n\n")
            
            # 요약 통계
            f.write("=" * 100 + "\n")
            f.write("1. 요약 통계\n")
            f.write("=" * 100 + "\n\n")
            
            f.write(f"총 알람 수: {len(self.alerts_df)}개\n\n")
            
            level_counts = self.alerts_df['alert_level'].value_counts()
            f.write("레벨별 분포:\n")
            for level, count in level_counts.items():
                pct = (count / len(self.alerts_df)) * 100
                f.write(f"  - {level}: {count}개 ({pct:.1f}%)\n")
            f.write("\n")
            
            # CRITICAL 알람 상세
            critical_alerts = self.alerts_df[
                self.alerts_df['alert_level'] == 'CRITICAL'
            ].sort_values('priority_score', ascending=False)
            
            f.write("=" * 100 + "\n")
            f.write(f"2. CRITICAL 알람 ({len(critical_alerts)}개)\n")
            f.write("=" * 100 + "\n\n")
            
            if not critical_alerts.empty:
                for idx, alert in critical_alerts.head(top_n).iterrows():
                    f.write(f"[{alert['timestamp']}] 우선순위: {alert['priority_score']}\n")
                    f.write(f"  사유: {alert['reasons']}\n")
                    f.write(f"  텔레그램: {alert['telegram_msgs']:.0f} msgs, ")
                    f.write(f"고래거래: {alert['whale_txs']:.0f} txs, ")
                    f.write(f"트위터: {alert['twitter_engagement']:.0f}\n\n")
            else:
                f.write("  (없음)\n\n")
            
            # HIGH 알람 상세
            high_alerts = self.alerts_df[
                self.alerts_df['alert_level'] == 'HIGH'
            ].sort_values('priority_score', ascending=False)
            
            f.write("=" * 100 + "\n")
            f.write(f"3. HIGH 알람 ({len(high_alerts)}개)\n")
            f.write("=" * 100 + "\n\n")
            
            if not high_alerts.empty:
                for idx, alert in high_alerts.head(top_n).iterrows():
                    f.write(f"[{alert['timestamp']}] 우선순위: {alert['priority_score']}\n")
                    f.write(f"  사유: {alert['reasons']}\n")
                    f.write(f"  텔레그램: {alert['telegram_msgs']:.0f} msgs, ")
                    f.write(f"고래거래: {alert['whale_txs']:.0f} txs, ")
                    f.write(f"트위터: {alert['twitter_engagement']:.0f}\n\n")
            else:
                f.write("  (없음)\n\n")
            
            # 패턴 요약
            f.write("=" * 100 + "\n")
            f.write("4. 주요 패턴\n")
            f.write("=" * 100 + "\n\n")
            
            # 동시 급증 패턴
            triple_spikes = self.alerts_df[
                self.alerts_df['reasons'].str.contains('3개 소스 모두 급증', na=False)
            ]
            telegram_whale_spikes = self.alerts_df[
                self.alerts_df['reasons'].str.contains('텔레그램\+고래 동시 급증', na=False)
            ]
            twitter_whale_spikes = self.alerts_df[
                self.alerts_df['reasons'].str.contains('트위터\+고래 동시 급증', na=False)
            ]
            
            f.write(f"3개 소스 동시 급증: {len(triple_spikes)}회\n")
            f.write(f"텔레그램 + 고래 동시 급증: {len(telegram_whale_spikes)}회\n")
            f.write(f"트위터 + 고래 동시 급증: {len(twitter_whale_spikes)}회\n\n")
            
            f.write("=" * 100 + "\n")
            f.write("리포트 종료\n")
            f.write("=" * 100 + "\n")
        
        print(f"✓ 알람 리포트 저장: {output_path}")
    
    def generate_all_visualizations(self, output_dir='/Volumes/T7/class/2025-FALL/big_data/data/visualizations'):
        """
        모든 시각화 생성
        
        Args:
            output_dir: 출력 디렉토리
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "=" * 80)
        print("시각화 생성 중...")
        print("=" * 80 + "\n")
        
        # 1. 상관관계 히트맵
        self.plot_correlation_heatmap(
            output_path=os.path.join(output_dir, 'correlation_heatmap.png')
        )
        
        # 2. 시계열 + 스파이크
        self.plot_time_series_with_spikes(
            output_path=os.path.join(output_dir, 'time_series_with_spikes.png'),
            recent_days=90
        )
        
        # 3. 알람 통계
        self.plot_alert_statistics(
            output_path=os.path.join(output_dir, 'alert_statistics.png')
        )
        
        # 4. 시차 상관관계 (텔레그램 → 고래)
        self.plot_lag_correlation(
            lag_data_path='/Volumes/T7/class/2025-FALL/big_data/data/pattern_telegram_to_whale.csv',
            output_path=os.path.join(output_dir, 'lag_correlation_telegram_whale.png')
        )
        
        # 5. 시차 상관관계 (트위터 → 고래)
        self.plot_lag_correlation(
            lag_data_path='/Volumes/T7/class/2025-FALL/big_data/data/pattern_twitter_to_whale.csv',
            output_path=os.path.join(output_dir, 'lag_correlation_twitter_whale.png')
        )
        
        # 6. 텍스트 리포트
        self.generate_alert_report(
            output_path=os.path.join(output_dir, 'alert_report.txt')
        )
        
        print("\n" + "=" * 80)
        print(f"모든 시각화 완료! 출력 디렉토리: {output_dir}")
        print("=" * 80)


if __name__ == '__main__':
    # 데이터 경로
    MERGED_DATA_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/multi_source_merged_data.csv'
    ALERTS_PATH = '/Volumes/T7/class/2025-FALL/big_data/data/multi_source_alerts.csv'
    
    print("=" * 80)
    print("Spike 알람 대시보드 시작")
    print("=" * 80 + "\n")
    
    # 대시보드 초기화
    dashboard = SpikeAlertDashboard(MERGED_DATA_PATH, ALERTS_PATH)
    
    # 모든 시각화 생성
    dashboard.generate_all_visualizations()
    
    print("\n✅ 대시보드 생성 완료!")

