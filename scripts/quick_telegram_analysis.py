#!/usr/bin/env python3
"""
빠른 텔레그램 상관관계 분석
"""

import pandas as pd
import numpy as np
from scipy import stats

# 데이터 로드
print("데이터 로딩 중...")
df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("\n" + "="*80)
print("텔레그램 커뮤니티 활동 상관관계 분석")
print("="*80)

# 기본 통계
print(f"\n📅 분석 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
print(f"📊 총 데이터: {len(df):,} 시간")
print(f"💬 텔레그램 총 메시지: {df['message_count'].sum():.0f}개")
print(f"💬 평균 시간당: {df['message_count'].mean():.2f}개")

# 상관관계 분석
df_clean = df[['message_count', 'ETH_close', 'tx_frequency', 'tx_amount']].dropna()
print(f"\n분석 가능 데이터: {len(df_clean):,} 시간")

print("\n" + "="*80)
print("상관계수 분석 (Pearson Correlation)")
print("="*80)

# 1. 메시지 vs ETH 가격
r1, p1 = stats.pearsonr(df_clean['message_count'], df_clean['ETH_close'])
print(f"\n1. 텔레그램 메시지 수 ↔ ETH 가격")
print(f"   상관계수: {r1:+.4f}")
print(f"   P-value: {p1:.6f} {'✅ 유의함' if p1 < 0.05 else '❌ 유의하지 않음'}")

# 2. 메시지 vs 고래 거래 빈도
r2, p2 = stats.pearsonr(df_clean['message_count'], df_clean['tx_frequency'])
print(f"\n2. 텔레그램 메시지 수 ↔ 고래 거래 빈도")
print(f"   상관계수: {r2:+.4f}")
print(f"   P-value: {p2:.6f} {'✅ 유의함' if p2 < 0.05 else '❌ 유의하지 않음'}")

# 3. 메시지 vs 고래 거래 금액
r3, p3 = stats.pearsonr(df_clean['message_count'], df_clean['tx_amount'])
print(f"\n3. 텔레그램 메시지 수 ↔ 고래 거래 금액")
print(f"   상관계수: {r3:+.4f}")
print(f"   P-value: {p3:.6f} {'✅ 유의함' if p3 < 0.05 else '❌ 유의하지 않음'}")

# 시차 상관관계 (간단 버전)
print("\n" + "="*80)
print("시차 상관관계 (Lag Correlation)")
print("="*80)

print("\n텔레그램 → ETH 가격 (3시간까지):")
for lag in range(4):
    if len(df_clean) > lag:
        x = df_clean['message_count'].iloc[:-lag] if lag > 0 else df_clean['message_count']
        y = df_clean['ETH_close'].iloc[lag:] if lag > 0 else df_clean['ETH_close']
        if len(x) == len(y):
            r, p = stats.pearsonr(x, y)
            print(f"  Lag {lag}h: r={r:+.4f}, p={p:.4f} {'✅' if p < 0.05 else ''}")

print("\n텔레그램 → 고래 거래 (3시간까지):")
for lag in range(4):
    if len(df_clean) > lag:
        x = df_clean['message_count'].iloc[:-lag] if lag > 0 else df_clean['message_count']
        y = df_clean['tx_frequency'].iloc[lag:] if lag > 0 else df_clean['tx_frequency']
        if len(x) == len(y):
            r, p = stats.pearsonr(x, y)
            print(f"  Lag {lag}h: r={r:+.4f}, p={p:.4f} {'✅' if p < 0.05 else ''}")

# 결론
print("\n" + "="*80)
print("결론")
print("="*80)

sig_count = sum([p1 < 0.05, p2 < 0.05, p3 < 0.05])
print(f"\n유의미한 상관관계: {sig_count}/3개")

if sig_count >= 2:
    print("\n✅ 텔레그램 활동과 시장 지표 간 유의미한 상관관계 존재!")
elif sig_count == 1:
    print("\n⚠️ 일부 유의미한 상관관계 발견")
else:
    print("\n❌ 직접적인 상관관계 약함")
    print("   → 시차 효과 확인 필요")
    print("   → 더 많은 데이터 필요")

print("\n💡 대시보드에서 더 자세히 확인: streamlit run app.py\n")






