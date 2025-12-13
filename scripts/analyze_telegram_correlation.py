"""
텔레그램 커뮤니티 활동 상관관계 분석 스크립트

텔레그램 메시지 수와 고래 거래량, 가격 변화의 상관관계를 분석합니다.
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests
import warnings
import sys
import os

warnings.filterwarnings('ignore')

# 경로 추가
sys.path.append('/Volumes/T7/class/2025-FALL/big_data')

def load_data():
    """전처리된 데이터 로드"""
    try:
        df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        print("❌ 전처리된 데이터를 찾을 수 없습니다.")
        print("먼저 'python scripts/preprocess_data.py'를 실행하세요.")
        sys.exit(1)


def analyze_basic_correlation(df):
    """기본 상관관계 분석"""
    print("\n" + "=" * 80)
    print("1. 피어슨 상관계수 (Pearson Correlation) - 선형 관계")
    print("=" * 80)
    
    # 결측치 제거
    df_clean = df[['message_count', 'ETH_close', 'BTC_close', 'tx_frequency', 'tx_amount', 'avg_sentiment']].dropna()
    
    if len(df_clean) < 10:
        print("⚠️ 데이터가 부족합니다 (최소 10개 필요)")
        return
    
    results = []
    
    # 1. 텔레그램 메시지 수 vs ETH 가격
    corr, p_val = stats.pearsonr(df_clean['message_count'], df_clean['ETH_close'])
    results.append(('메시지 수 ↔ ETH 가격', corr, p_val))
    print(f"\n📊 텔레그램 메시지 수 ↔ ETH 가격")
    print(f"   상관계수: {corr:+.4f}")
    print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
    print(f"   해석: {'양의 상관관계' if corr > 0 else '음의 상관관계'} - " + 
          f"{'강함' if abs(corr) > 0.7 else '중간' if abs(corr) > 0.4 else '약함'} (|r|={abs(corr):.2f})")
    
    # 2. 텔레그램 메시지 수 vs BTC 가격
    corr, p_val = stats.pearsonr(df_clean['message_count'], df_clean['BTC_close'])
    results.append(('메시지 수 ↔ BTC 가격', corr, p_val))
    print(f"\n📊 텔레그램 메시지 수 ↔ BTC 가격")
    print(f"   상관계수: {corr:+.4f}")
    print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
    print(f"   해석: {'양의 상관관계' if corr > 0 else '음의 상관관계'} - " + 
          f"{'강함' if abs(corr) > 0.7 else '중간' if abs(corr) > 0.4 else '약함'} (|r|={abs(corr):.2f})")
    
    # 3. 텔레그램 메시지 수 vs 고래 거래 빈도
    corr, p_val = stats.pearsonr(df_clean['message_count'], df_clean['tx_frequency'])
    results.append(('메시지 수 ↔ 고래 거래 빈도', corr, p_val))
    print(f"\n📊 텔레그램 메시지 수 ↔ 고래 거래 빈도")
    print(f"   상관계수: {corr:+.4f}")
    print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
    print(f"   해석: {'양의 상관관계' if corr > 0 else '음의 상관관계'} - " + 
          f"{'강함' if abs(corr) > 0.7 else '중간' if abs(corr) > 0.4 else '약함'} (|r|={abs(corr):.2f})")
    
    # 4. 텔레그램 메시지 수 vs 고래 거래 금액
    corr, p_val = stats.pearsonr(df_clean['message_count'], df_clean['tx_amount'])
    results.append(('메시지 수 ↔ 고래 거래 금액', corr, p_val))
    print(f"\n📊 텔레그램 메시지 수 ↔ 고래 거래 금액")
    print(f"   상관계수: {corr:+.4f}")
    print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
    print(f"   해석: {'양의 상관관계' if corr > 0 else '음의 상관관계'} - " + 
          f"{'강함' if abs(corr) > 0.7 else '중간' if abs(corr) > 0.4 else '약함'} (|r|={abs(corr):.2f})")
    
    # 5. 텔레그램 감정 vs ETH 가격
    corr, p_val = stats.pearsonr(df_clean['avg_sentiment'], df_clean['ETH_close'])
    results.append(('감정 점수 ↔ ETH 가격', corr, p_val))
    print(f"\n📊 텔레그램 감정 점수 ↔ ETH 가격")
    print(f"   상관계수: {corr:+.4f}")
    print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
    print(f"   해석: {'양의 상관관계' if corr > 0 else '음의 상관관계'} - " + 
          f"{'강함' if abs(corr) > 0.7 else '중간' if abs(corr) > 0.4 else '약함'} (|r|={abs(corr):.2f})")
    
    return results


def analyze_lag_correlation(df):
    """시차 상관관계 분석"""
    print("\n" + "=" * 80)
    print("2. 시차 상관관계 (Lag Correlation) - 텔레그램이 선행하는지 확인")
    print("=" * 80)
    
    df_clean = df[['message_count', 'ETH_close', 'tx_frequency']].dropna()
    
    if len(df_clean) < 50:
        print("⚠️ 데이터가 부족합니다 (최소 50개 필요)")
        return
    
    max_lag = min(12, len(df_clean) // 10)  # 최대 12시간 또는 데이터의 10%
    
    print(f"\n🔍 텔레그램 메시지 수 → ETH 가격 (최대 {max_lag}시간 시차)")
    print("   (텔레그램 활동 후 몇 시간 뒤에 가격이 변하는가?)")
    
    lag_results_eth = []
    for lag in range(0, max_lag + 1):
        if len(df_clean) > lag:
            x = df_clean['message_count'].iloc[:-lag] if lag > 0 else df_clean['message_count']
            y = df_clean['ETH_close'].iloc[lag:] if lag > 0 else df_clean['ETH_close']
            
            if len(x) > 0 and len(y) > 0 and len(x) == len(y):
                corr, p_val = stats.pearsonr(x, y)
                lag_results_eth.append({
                    'lag': lag,
                    'correlation': corr,
                    'p_value': p_val,
                    'significant': p_val < 0.05
                })
                sig_marker = '✅' if p_val < 0.05 else '  '
                print(f"   Lag {lag:2d}시간: r={corr:+.4f}, p={p_val:.4f} {sig_marker}")
    
    if lag_results_eth:
        max_corr_eth = max(lag_results_eth, key=lambda x: abs(x['correlation']))
        print(f"\n   💡 최대 상관: Lag {max_corr_eth['lag']}시간, r={max_corr_eth['correlation']:+.4f}")
        if max_corr_eth['significant']:
            print(f"   ✅ 텔레그램 활동 후 {max_corr_eth['lag']}시간 뒤 ETH 가격과 유의미한 상관!")
    
    print(f"\n🔍 텔레그램 메시지 수 → 고래 거래 빈도 (최대 {max_lag}시간 시차)")
    print("   (텔레그램 활동 후 몇 시간 뒤에 고래가 움직이는가?)")
    
    lag_results_whale = []
    for lag in range(0, max_lag + 1):
        if len(df_clean) > lag:
            x = df_clean['message_count'].iloc[:-lag] if lag > 0 else df_clean['message_count']
            y = df_clean['tx_frequency'].iloc[lag:] if lag > 0 else df_clean['tx_frequency']
            
            if len(x) > 0 and len(y) > 0 and len(x) == len(y):
                corr, p_val = stats.pearsonr(x, y)
                lag_results_whale.append({
                    'lag': lag,
                    'correlation': corr,
                    'p_value': p_val,
                    'significant': p_val < 0.05
                })
                sig_marker = '✅' if p_val < 0.05 else '  '
                print(f"   Lag {lag:2d}시간: r={corr:+.4f}, p={p_val:.4f} {sig_marker}")
    
    if lag_results_whale:
        max_corr_whale = max(lag_results_whale, key=lambda x: abs(x['correlation']))
        print(f"\n   💡 최대 상관: Lag {max_corr_whale['lag']}시간, r={max_corr_whale['correlation']:+.4f}")
        if max_corr_whale['significant']:
            print(f"   ✅ 텔레그램 활동 후 {max_corr_whale['lag']}시간 뒤 고래 거래와 유의미한 상관!")
    
    return lag_results_eth, lag_results_whale


def analyze_change_correlation(df):
    """변화율 상관관계 분석"""
    print("\n" + "=" * 80)
    print("3. 변화율 상관관계 - 급변 시 동시 움직임")
    print("=" * 80)
    
    # 변화율 계산
    df_changes = df.copy()
    df_changes['msg_change'] = df_changes['message_count'].pct_change() * 100
    df_changes['eth_change'] = df_changes['ETH_close'].pct_change() * 100
    df_changes['whale_freq_change'] = df_changes['tx_frequency'].pct_change() * 100
    df_changes['whale_amt_change'] = df_changes['tx_amount'].pct_change() * 100
    
    # 무한대 제거
    df_changes = df_changes.replace([np.inf, -np.inf], np.nan)
    
    # 1. 메시지 변화율 vs ETH 가격 변화율
    df_clean = df_changes[['msg_change', 'eth_change']].dropna()
    if len(df_clean) > 10:
        corr, p_val = stats.pearsonr(df_clean['msg_change'], df_clean['eth_change'])
        print(f"\n📊 메시지 변화율 ↔ ETH 가격 변화율")
        print(f"   상관계수: {corr:+.4f}")
        print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
        if p_val < 0.05:
            print(f"   ✅ 텔레그램 활동이 급증/급감할 때 ETH 가격도 함께 움직임!")
    
    # 2. 메시지 변화율 vs 고래 거래 빈도 변화율
    df_clean = df_changes[['msg_change', 'whale_freq_change']].dropna()
    if len(df_clean) > 10:
        corr, p_val = stats.pearsonr(df_clean['msg_change'], df_clean['whale_freq_change'])
        print(f"\n📊 메시지 변화율 ↔ 고래 거래 빈도 변화율")
        print(f"   상관계수: {corr:+.4f}")
        print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
        if p_val < 0.05:
            print(f"   ✅ 텔레그램 활동이 급증/급감할 때 고래 거래도 함께 움직임!")
    
    # 3. 메시지 변화율 vs 고래 거래 금액 변화율
    df_clean = df_changes[['msg_change', 'whale_amt_change']].dropna()
    if len(df_clean) > 10:
        corr, p_val = stats.pearsonr(df_clean['msg_change'], df_clean['whale_amt_change'])
        print(f"\n📊 메시지 변화율 ↔ 고래 거래 금액 변화율")
        print(f"   상관계수: {corr:+.4f}")
        print(f"   P-value: {p_val:.6f} {'✅ 유의함 (p<0.05)' if p_val < 0.05 else '❌ 유의하지 않음'}")
        if p_val < 0.05:
            print(f"   ✅ 텔레그램 활동이 급증/급감할 때 고래 거래 금액도 함께 움직임!")


def analyze_granger_causality(df):
    """그랜저 인과관계 검정"""
    print("\n" + "=" * 80)
    print("4. 그랜저 인과관계 (Granger Causality) - 텔레그램이 원인인가?")
    print("=" * 80)
    print("   (H0: 텔레그램 활동은 가격/거래의 원인이 아니다)")
    
    df_clean = df[['message_count', 'ETH_close', 'tx_frequency']].dropna()
    
    if len(df_clean) < 50:
        print("⚠️ 데이터가 부족합니다 (최소 50개 필요)")
        return
    
    max_lag = min(8, len(df_clean) // 20)
    
    try:
        # 1. 텔레그램 → ETH 가격
        print(f"\n🔍 텔레그램 메시지 수 → ETH 가격 (최대 {max_lag}시간 lag)")
        test_data = df_clean[['ETH_close', 'message_count']].copy()
        test_result = grangercausalitytests(test_data, max_lag, verbose=False)
        
        significant_lags = []
        for lag in range(1, max_lag + 1):
            p_value = test_result[lag][0]['ssr_ftest'][1]
            if p_value < 0.05:
                significant_lags.append(lag)
                print(f"   Lag {lag}: p={p_value:.4f} ✅ 유의함!")
            else:
                print(f"   Lag {lag}: p={p_value:.4f}")
        
        if significant_lags:
            print(f"\n   ✅ 텔레그램 활동이 ETH 가격에 영향을 줌! (Lag: {significant_lags})")
        else:
            print(f"\n   ❌ 텔레그램 활동이 ETH 가격에 유의미한 영향을 주지 않음")
        
    except Exception as e:
        print(f"   ⚠️ 그랜저 인과관계 검정 실패: {e}")
    
    try:
        # 2. 텔레그램 → 고래 거래
        print(f"\n🔍 텔레그램 메시지 수 → 고래 거래 빈도 (최대 {max_lag}시간 lag)")
        test_data = df_clean[['tx_frequency', 'message_count']].copy()
        test_result = grangercausalitytests(test_data, max_lag, verbose=False)
        
        significant_lags = []
        for lag in range(1, max_lag + 1):
            p_value = test_result[lag][0]['ssr_ftest'][1]
            if p_value < 0.05:
                significant_lags.append(lag)
                print(f"   Lag {lag}: p={p_value:.4f} ✅ 유의함!")
            else:
                print(f"   Lag {lag}: p={p_value:.4f}")
        
        if significant_lags:
            print(f"\n   ✅ 텔레그램 활동이 고래 거래에 영향을 줌! (Lag: {significant_lags})")
        else:
            print(f"\n   ❌ 텔레그램 활동이 고래 거래에 유의미한 영향을 주지 않음")
        
    except Exception as e:
        print(f"   ⚠️ 그랜저 인과관계 검정 실패: {e}")


def generate_summary(df, basic_results):
    """종합 요약"""
    print("\n" + "=" * 80)
    print("📊 종합 분석 결과")
    print("=" * 80)
    
    # 데이터 기본 정보
    print(f"\n📅 분석 기간: {df['timestamp'].min().date()} ~ {df['timestamp'].max().date()}")
    print(f"📊 총 데이터: {len(df)} 시간")
    print(f"💬 텔레그램 총 메시지: {df['message_count'].sum():.0f}개")
    print(f"💬 평균 시간당 메시지: {df['message_count'].mean():.2f}개")
    print(f"🐋 고래 거래 총 건수: {df['tx_frequency'].sum():.0f}건")
    
    # 유의미한 상관관계 카운트
    if basic_results:
        significant_count = sum([1 for _, _, p in basic_results if p < 0.05])
        total_count = len(basic_results)
        
        print(f"\n🎯 유의미한 상관관계: {significant_count}/{total_count}개")
        
        if significant_count >= 2:
            print("\n✅ 결론: 텔레그램 활동과 시장 지표 간 유의미한 상관관계가 존재합니다!")
            print("\n주요 발견:")
            for name, corr, p_val in basic_results:
                if p_val < 0.05:
                    direction = "양의" if corr > 0 else "음의"
                    strength = "강한" if abs(corr) > 0.7 else "중간" if abs(corr) > 0.4 else "약한"
                    print(f"  • {name}: {direction} {strength} 상관관계 (r={corr:+.4f}, p={p_val:.4f})")
            
            print("\n💡 의미:")
            print("  → 텔레그램 커뮤니티 활동을 모니터링하면 가격/거래 변화 예측 가능")
            print("  → 스파이크 알람 시스템으로 실시간 감지 추천")
        
        elif significant_count == 1:
            print("\n⚠️ 결론: 일부 유의미한 상관관계가 발견되었으나 전반적으로 약합니다.")
            print("\n가능한 이유:")
            print("  • 텔레그램 메시지 수가 적음 (더 활발한 채널 필요)")
            print("  • 시차 효과 (Lag Correlation 확인)")
            print("  • 데이터 수집 기간 확장 필요")
        
        else:
            print("\n❌ 결론: 텔레그램 활동과 시장 지표 간 유의미한 직접 상관관계가 없습니다.")
            print("\n가능한 이유:")
            print("  • 데이터 수집 기간이 짧음")
            print("  • 텔레그램 채널이 시장에 영향력이 적음")
            print("  • 시차가 존재 (Lag Correlation이나 Granger Causality 확인)")
            print("  • 비선형 관계일 수 있음 (Spearman 상관계수 확인)")


def save_results_to_file(df, results):
    """결과를 파일로 저장"""
    output_path = '/Volumes/T7/class/2025-FALL/big_data/data/telegram_correlation_analysis.csv'
    
    # 상관관계 매트릭스 생성
    df_corr = df[['message_count', 'ETH_close', 'BTC_close', 'tx_frequency', 'tx_amount', 'avg_sentiment']].corr()
    df_corr.to_csv(output_path)
    
    print(f"\n💾 상관관계 매트릭스가 저장되었습니다: {output_path}")


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 80)
    print("🔍 텔레그램 커뮤니티 활동 상관관계 분석")
    print("=" * 80)
    
    # 데이터 로드
    print("\n📂 데이터 로딩 중...")
    df = load_data()
    print(f"✅ 데이터 로드 완료: {len(df)} 시간")
    
    # 1. 기본 상관관계
    basic_results = analyze_basic_correlation(df)
    
    # 2. 시차 상관관계
    analyze_lag_correlation(df)
    
    # 3. 변화율 상관관계
    analyze_change_correlation(df)
    
    # 4. 그랜저 인과관계
    analyze_granger_causality(df)
    
    # 5. 종합 요약
    generate_summary(df, basic_results)
    
    # 6. 결과 저장
    save_results_to_file(df, basic_results)
    
    print("\n" + "=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    print("\n💡 대시보드에서 더 자세한 시각화를 확인하세요:")
    print("   streamlit run app.py")
    print("\n")


if __name__ == '__main__':
    main()





