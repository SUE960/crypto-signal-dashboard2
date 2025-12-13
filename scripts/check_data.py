"""
수집된 데이터 확인 스크립트
"""

import pandas as pd
from datetime import datetime

print("=" * 70)
print("수집된 데이터 확인")
print("=" * 70)

# 1. 텔레그램 데이터
print("\n📱 텔레그램 데이터 (telegram_data.csv)")
print("-" * 70)
try:
    telegram_df = pd.read_csv('data/telegram_data.csv')
    telegram_df['timestamp'] = pd.to_datetime(telegram_df['timestamp'])
    
    print(f"✅ 총 {len(telegram_df):,}개 레코드")
    print(f"   기간: {telegram_df['timestamp'].min()} ~ {telegram_df['timestamp'].max()}")
    print(f"   채널: {telegram_df['channel'].nunique()}개 - {', '.join(telegram_df['channel'].unique())}")
    print(f"\n채널별 메시지 수:")
    for channel, count in telegram_df.groupby('channel')['message_count'].sum().sort_values(ascending=False).items():
        print(f"   {channel}: {count:,}개")
    
    print(f"\n평균 감정 점수:")
    print(f"   전체: {telegram_df['avg_sentiment'].mean():.3f}")
    print(f"   긍정 비율: {telegram_df['avg_positive'].mean():.3f}")
    print(f"   부정 비율: {telegram_df['avg_negative'].mean():.3f}")
    
except Exception as e:
    print(f"❌ 오류: {e}")

# 2. 코인니스 데이터
print("\n\n📰 코인니스 뉴스 데이터 (coinness_data.csv)")
print("-" * 70)
try:
    coinness_df = pd.read_csv('data/coinness_data.csv')
    coinness_df['timestamp'] = pd.to_datetime(coinness_df['timestamp'])
    
    # 중복 제거
    coinness_df_unique = coinness_df.drop_duplicates(subset=['title', 'timestamp'])
    
    print(f"✅ 총 {len(coinness_df):,}개 레코드 (중복 제거 후: {len(coinness_df_unique):,}개)")
    print(f"   기간: {coinness_df_unique['timestamp'].min()} ~ {coinness_df_unique['timestamp'].max()}")
    
    print(f"\n일별 뉴스 수:")
    daily_news = coinness_df_unique.groupby(coinness_df_unique['timestamp'].dt.date).size()
    print(f"   평균: {daily_news.mean():.1f}개/일")
    print(f"   최대: {daily_news.max()}개/일 ({daily_news.idxmax()})")
    print(f"   최소: {daily_news.min()}개/일 ({daily_news.idxmin()})")
    
    print(f"\n감정 분석:")
    print(f"   평균 감정 점수: {coinness_df_unique['sentiment_compound'].mean():.3f}")
    positive = (coinness_df_unique['sentiment_compound'] > 0.05).sum()
    negative = (coinness_df_unique['sentiment_compound'] < -0.05).sum()
    neutral = len(coinness_df_unique) - positive - negative
    print(f"   긍정: {positive} ({positive/len(coinness_df_unique)*100:.1f}%)")
    print(f"   부정: {negative} ({negative/len(coinness_df_unique)*100:.1f}%)")
    print(f"   중립: {neutral} ({neutral/len(coinness_df_unique)*100:.1f}%)")
    
except Exception as e:
    print(f"❌ 오류: {e}")

# 3. 고래 거래 데이터
print("\n\n🐋 고래 거래 데이터 (whale_transactions_rows_ETH_rev1.csv)")
print("-" * 70)
try:
    whale_df = pd.read_csv('data/whale_transactions_rows_ETH_rev1.csv')
    whale_df['timestamp'] = pd.to_datetime(whale_df['timestamp'], errors='coerce')
    whale_df = whale_df.dropna(subset=['timestamp'])
    
    print(f"✅ 총 {len(whale_df):,}개 거래")
    print(f"   기간: {whale_df['timestamp'].min()} ~ {whale_df['timestamp'].max()}")
    if 'amount' in whale_df.columns:
        print(f"   총 거래량: {whale_df['amount'].sum():,.2f} ETH")
        print(f"   평균 거래량: {whale_df['amount'].mean():.2f} ETH")
    
except Exception as e:
    print(f"❌ 오류: {e}")

# 4. ETH 가격 데이터
print("\n\n💰 ETH 가격 데이터 (price_history_eth_rows.csv)")
print("-" * 70)
try:
    eth_price_df = pd.read_csv('data/price_history_eth_rows.csv')
    eth_price_df['timestamp'] = pd.to_datetime(eth_price_df['timestamp'], errors='coerce')
    eth_price_df = eth_price_df.dropna(subset=['timestamp'])
    
    print(f"✅ 총 {len(eth_price_df):,}개 가격 데이터")
    print(f"   기간: {eth_price_df['timestamp'].min()} ~ {eth_price_df['timestamp'].max()}")
    if 'price' in eth_price_df.columns:
        print(f"   최고가: ${eth_price_df['price'].max():,.2f}")
        print(f"   최저가: ${eth_price_df['price'].min():,.2f}")
        print(f"   현재가: ${eth_price_df['price'].iloc[-1]:,.2f}")
    
except Exception as e:
    print(f"❌ 오류: {e}")

# 5. BTC 가격 데이터
print("\n\n💰 BTC 가격 데이터 (price_history_btc_rows.csv)")
print("-" * 70)
try:
    btc_price_df = pd.read_csv('data/price_history_btc_rows.csv')
    btc_price_df['timestamp'] = pd.to_datetime(btc_price_df['timestamp'], errors='coerce')
    btc_price_df = btc_price_df.dropna(subset=['timestamp'])
    
    print(f"✅ 총 {len(btc_price_df):,}개 가격 데이터")
    print(f"   기간: {btc_price_df['timestamp'].min()} ~ {btc_price_df['timestamp'].max()}")
    if 'price' in btc_price_df.columns:
        print(f"   최고가: ${btc_price_df['price'].max():,.2f}")
        print(f"   최저가: ${btc_price_df['price'].min():,.2f}")
        print(f"   현재가: ${btc_price_df['price'].iloc[-1]:,.2f}")
    
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "=" * 70)
print("데이터 확인 완료!")
print("=" * 70)

# 다음 단계 안내
print("\n📋 다음 단계:")
print("1. 데이터 전처리 및 통합: python scripts/preprocess_data.py")
print("2. 대시보드 실행: streamlit run app.py")





