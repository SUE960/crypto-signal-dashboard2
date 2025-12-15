"""
모든 뉴스 데이터 파일을 새로 수집한 데이터로 업데이트

새로 수집한 coinness_data2.csv를 기준으로 모든 뉴스 데이터 파일을 업데이트합니다.
"""

import pandas as pd
import os
from datetime import datetime

def update_all_news_data():
    """모든 뉴스 데이터 업데이트"""
    print("=" * 70)
    print("모든 뉴스 데이터 업데이트")
    print("=" * 70)
    
    # 파일 경로
    data_dir = 'data'
    new_data_file = os.path.join(data_dir, 'coinness_data2.csv')
    main_file = os.path.join(data_dir, 'coinness_data.csv')
    
    # 새로 수집한 데이터 로드
    if not os.path.exists(new_data_file):
        print(f"❌ 새로 수집한 데이터 파일을 찾을 수 없습니다: {new_data_file}")
        return
    
    print(f"\n📥 새로 수집한 데이터 로드: {new_data_file}")
    df_new = pd.read_csv(new_data_file)
    df_new['timestamp'] = pd.to_datetime(df_new['timestamp'], errors='coerce')
    df_new = df_new.dropna(subset=['timestamp'])
    
    print(f"   새로 수집한 데이터: {len(df_new):,}개 기사")
    print(f"   기간: {df_new['timestamp'].min()} ~ {df_new['timestamp'].max()}")
    
    # 기존 coinness_data.csv가 있으면 병합 (중복 제거)
    if os.path.exists(main_file):
        print(f"\n📥 기존 데이터 로드: {main_file}")
        df_existing = pd.read_csv(main_file)
        df_existing['timestamp'] = pd.to_datetime(df_existing['timestamp'], errors='coerce')
        df_existing = df_existing.dropna(subset=['timestamp'])
        print(f"   기존 데이터: {len(df_existing):,}개 기사")
        print(f"   기간: {df_existing['timestamp'].min()} ~ {df_existing['timestamp'].max()}")
        
        # 병합 (새 데이터 우선)
        print(f"\n🔄 데이터 병합 중...")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # 중복 제거 (link 기준, 새 데이터 우선)
        if 'link' in df_combined.columns:
            before = len(df_combined)
            df_combined = df_combined.drop_duplicates(subset=['link'], keep='last')
            duplicates_removed = before - len(df_combined)
            print(f"   중복 제거: {duplicates_removed:,}개 (link 기준)")
        
        # title + timestamp 기준으로도 중복 제거
        if 'title' in df_combined.columns:
            before = len(df_combined)
            df_combined = df_combined.drop_duplicates(
                subset=['title', 'timestamp'], 
                keep='last'
            )
            duplicates_removed = before - len(df_combined)
            if duplicates_removed > 0:
                print(f"   추가 중복 제거: {duplicates_removed:,}개 (title+timestamp 기준)")
    else:
        print(f"\n⚠️  기존 데이터 파일이 없습니다. 새 데이터로 생성합니다.")
        df_combined = df_new.copy()
    
    # timestamp 기준으로 정렬 (최신순)
    df_combined = df_combined.sort_values('timestamp', ascending=False).reset_index(drop=True)
    
    print(f"\n✅ 병합 완료: 총 {len(df_combined):,}개 기사")
    print(f"   기간: {df_combined['timestamp'].min()} ~ {df_combined['timestamp'].max()}")
    
    # 데이터 디렉토리 생성
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. coinness_data.csv 업데이트 (Streamlit 대시보드용)
    print(f"\n💾 저장 중: {main_file}")
    df_combined.to_csv(main_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ 저장 완료: {main_file}")
    
    # 2. coinness_data2.csv 업데이트 (Next.js 대시보드용) - 이미 최신이지만 확실히 하기 위해
    print(f"\n💾 저장 중: {new_data_file}")
    df_combined.to_csv(new_data_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ 저장 완료: {new_data_file}")
    
    # 통계 출력
    print(f"\n📊 업데이트 통계:")
    print(f"   총 기사 수: {len(df_combined):,}개")
    if 'sentiment_compound' in df_combined.columns:
        print(f"   평균 감정 점수: {df_combined['sentiment_compound'].mean():.3f}")
        pos = (df_combined['sentiment_compound'] > 0.05).sum()
        neg = (df_combined['sentiment_compound'] < -0.05).sum()
        neu = len(df_combined) - pos - neg
        print(f"   긍정 비율: {pos:,}개 ({pos/len(df_combined)*100:.1f}%)")
        print(f"   부정 비율: {neg:,}개 ({neg/len(df_combined)*100:.1f}%)")
        print(f"   중립 비율: {neu:,}개 ({neu/len(df_combined)*100:.1f}%)")
    
    # 최근 7일 데이터 통계
    seven_days_ago = datetime.now() - pd.Timedelta(days=7)
    df_recent_7d = df_combined[df_combined['timestamp'] >= seven_days_ago]
    print(f"\n📅 최근 7일 통계:")
    print(f"   기사 수: {len(df_recent_7d):,}개")
    if len(df_recent_7d) > 0 and 'sentiment_compound' in df_recent_7d.columns:
        print(f"   평균 감정 점수: {df_recent_7d['sentiment_compound'].mean():.3f}")
    
    # 월별 통계
    if not df_combined.empty:
        print(f"\n📅 월별 기사 수 (최근 6개월):")
        monthly = df_combined.groupby(df_combined['timestamp'].dt.to_period('M')).size().sort_index(ascending=False)
        for month, count in monthly.head(6).items():
            print(f"   {month}: {count:,}개")
    
    print(f"\n✅ 모든 뉴스 데이터 업데이트 완료!")
    print(f"\n📝 업데이트된 파일:")
    print(f"   - {main_file} (Streamlit 대시보드용)")
    print(f"   - {new_data_file} (Next.js 대시보드용)")


if __name__ == '__main__':
    update_all_news_data()

