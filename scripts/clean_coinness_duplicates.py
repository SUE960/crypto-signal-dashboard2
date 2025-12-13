"""
코인니스 데이터 중복 제거 스크립트
"""

import pandas as pd
from datetime import datetime

print("=" * 70)
print("코인니스 데이터 중복 제거")
print("=" * 70)

# 데이터 로드
print("\n📂 데이터 로딩 중...")
df = pd.read_csv('data/coinness_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ 로드 완료: {len(df):,}개 레코드")

# 중복 제거 전 통계
print(f"\n📊 중복 제거 전:")
print(f"   총 레코드: {len(df):,}개")
print(f"   고유 제목: {df['title'].nunique():,}개")
print(f"   고유 링크: {df['link'].nunique():,}개")

# 중복 제거 (제목 + 시간 기준)
print(f"\n🧹 중복 제거 중...")
df_clean = df.drop_duplicates(subset=['title', 'timestamp'], keep='first')

duplicates_removed = len(df) - len(df_clean)
print(f"✅ {duplicates_removed:,}개 중복 제거 완료!")

# 중복 제거 후 통계
print(f"\n📊 중복 제거 후:")
print(f"   총 레코드: {len(df_clean):,}개")
print(f"   고유 제목: {df_clean['title'].nunique():,}개")
print(f"   고유 링크: {df_clean['link'].nunique():,}개")
print(f"   기간: {df_clean['timestamp'].min()} ~ {df_clean['timestamp'].max()}")

# 월별 분포
print(f"\n📅 월별 기사 수:")
monthly = df_clean.groupby(df_clean['timestamp'].dt.to_period('M')).size().sort_index()
for month, count in monthly.items():
    print(f"   {month}: {count:,}개")

# 백업 및 저장
print(f"\n💾 저장 중...")

# 기존 파일 백업
import shutil
backup_file = 'data/coinness_data_backup.csv'
shutil.copy('data/coinness_data.csv', backup_file)
print(f"   백업: {backup_file}")

# 정리된 데이터 저장
df_clean = df_clean.sort_values('timestamp', ascending=True)
df_clean.to_csv('data/coinness_data.csv', index=False, encoding='utf-8-sig')
print(f"   저장: data/coinness_data.csv")

print(f"\n✅ 완료!")
print(f"   {duplicates_removed:,}개 중복 제거")
print(f"   {len(df_clean):,}개 고유 기사 저장")
print("=" * 70)





