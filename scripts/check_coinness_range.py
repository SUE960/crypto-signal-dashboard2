"""
코인니스 데이터 날짜 범위 확인
"""
import pandas as pd

df = pd.read_csv('data/coinness_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 중복 제거
df = df.drop_duplicates(subset=['title', 'timestamp'])

print(f"총 {len(df):,}개 기사")
print(f"시작: {df['timestamp'].min()}")
print(f"종료: {df['timestamp'].max()}")

# 월별 분포
print(f"\n월별 기사 수:")
monthly = df.groupby(df['timestamp'].dt.to_period('M')).size().sort_index()
for month, count in monthly.items():
    print(f"  {month}: {count:,}개")

# 2025년 1월 1일부터인지 확인
from datetime import datetime
target_start = datetime(2025, 1, 1)
if df['timestamp'].min() > target_start:
    print(f"\n⚠️  2025년 1월 1일부터 수집 필요!")
    print(f"   현재 시작일: {df['timestamp'].min().date()}")
else:
    print(f"\n✅ 2025년 1월 1일부터 데이터 확보!")








