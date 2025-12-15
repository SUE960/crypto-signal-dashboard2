"""
뉴스 데이터 업데이트 스크립트

최근 수집한 뉴스 데이터를 기존 데이터와 병합하여 업데이트합니다.
"""

import pandas as pd
import os
from datetime import datetime

def update_news_data():
    """뉴스 데이터 업데이트"""
    print("=" * 60)
    print("뉴스 데이터 업데이트")
    print("=" * 60)
    
    # 파일 경로
    data_dir = 'data'
    recent_file = os.path.join(data_dir, 'coinness_data_recent_7days.csv')
    main_file = os.path.join(data_dir, 'coinness_data.csv')
    main_file2 = os.path.join(data_dir, 'coinness_data2.csv')
    
    # 최근 수집한 데이터 로드
    if not os.path.exists(recent_file):
        print(f"❌ 최근 수집 데이터 파일을 찾을 수 없습니다: {recent_file}")
        return
    
    print(f"\n📥 최근 수집 데이터 로드: {recent_file}")
    df_recent = pd.read_csv(recent_file)
    df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp'], errors='coerce')
    df_recent = df_recent.dropna(subset=['timestamp'])
    print(f"   최근 수집 데이터: {len(df_recent)}개 기사")
    print(f"   기간: {df_recent['timestamp'].min()} ~ {df_recent['timestamp'].max()}")
    
    # 기존 데이터 로드 (있으면)
    df_existing = pd.DataFrame()
    if os.path.exists(main_file):
        print(f"\n📥 기존 데이터 로드: {main_file}")
        df_existing = pd.read_csv(main_file)
        df_existing['timestamp'] = pd.to_datetime(df_existing['timestamp'], errors='coerce')
        df_existing = df_existing.dropna(subset=['timestamp'])
        print(f"   기존 데이터: {len(df_existing)}개 기사")
        print(f"   기간: {df_existing['timestamp'].min()} ~ {df_existing['timestamp'].max()}")
    else:
        print(f"\n⚠️  기존 데이터 파일이 없습니다. 새로 생성합니다: {main_file}")
    
    # 데이터 병합
    print(f"\n🔄 데이터 병합 중...")
    if not df_existing.empty:
        # 중복 제거 기준: link 또는 (title + timestamp)
        # 먼저 link 기준으로 중복 제거
        df_combined = pd.concat([df_existing, df_recent], ignore_index=True)
        
        # link가 있는 경우 link 기준으로 중복 제거
        if 'link' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset=['link'], keep='last')
            print(f"   link 기준 중복 제거 후: {len(df_combined)}개 기사")
        
        # link가 없는 경우 title + timestamp 기준으로 중복 제거
        if 'title' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(
                subset=['title', 'timestamp'], 
                keep='last'
            )
            print(f"   title+timestamp 기준 중복 제거 후: {len(df_combined)}개 기사")
    else:
        df_combined = df_recent.copy()
    
    # timestamp 기준으로 정렬 (최신순)
    df_combined = df_combined.sort_values('timestamp', ascending=False).reset_index(drop=True)
    
    print(f"\n✅ 병합 완료: 총 {len(df_combined)}개 기사")
    print(f"   기간: {df_combined['timestamp'].min()} ~ {df_combined['timestamp'].max()}")
    
    # 데이터 디렉토리 생성
    os.makedirs(data_dir, exist_ok=True)
    
    # coinness_data.csv 저장
    print(f"\n💾 저장 중: {main_file}")
    df_combined.to_csv(main_file, index=False, encoding='utf-8-sig')
    print(f"   ✅ 저장 완료: {main_file}")
    
    # coinness_data2.csv도 저장 (Next.js 대시보드용)
    print(f"\n💾 저장 중: {main_file2}")
    df_combined.to_csv(main_file2, index=False, encoding='utf-8-sig')
    print(f"   ✅ 저장 완료: {main_file2}")
    
    # 통계 출력
    print(f"\n📊 업데이트 통계:")
    print(f"   총 기사 수: {len(df_combined)}개")
    if 'sentiment_compound' in df_combined.columns:
        print(f"   평균 감정 점수: {df_combined['sentiment_compound'].mean():.3f}")
        print(f"   긍정 비율: {(df_combined['sentiment_compound'] > 0.05).sum() / len(df_combined) * 100:.1f}%")
        print(f"   부정 비율: {(df_combined['sentiment_compound'] < -0.05).sum() / len(df_combined) * 100:.1f}%")
        print(f"   중립 비율: {((df_combined['sentiment_compound'] >= -0.05) & (df_combined['sentiment_compound'] <= 0.05)).sum() / len(df_combined) * 100:.1f}%")
    
    # 최근 7일 데이터 통계
    seven_days_ago = datetime.now() - pd.Timedelta(days=7)
    df_recent_7d = df_combined[df_combined['timestamp'] >= seven_days_ago]
    print(f"\n📅 최근 7일 통계:")
    print(f"   기사 수: {len(df_recent_7d)}개")
    if len(df_recent_7d) > 0 and 'sentiment_compound' in df_recent_7d.columns:
        print(f"   평균 감정 점수: {df_recent_7d['sentiment_compound'].mean():.3f}")
    
    print(f"\n✅ 뉴스 데이터 업데이트 완료!")


if __name__ == '__main__':
    update_news_data()


