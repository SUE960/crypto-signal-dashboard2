"""
코인뉴스 지표 컴포넌트

대시보드에 표시할 뉴스 관련 지표와 위젯
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def show_news_summary_metrics(df):
    """뉴스 요약 메트릭 표시"""
    
    # 최근 24시간 데이터
    latest_time = df['timestamp'].max()
    last_24h = df[df['timestamp'] >= latest_time - timedelta(hours=24)]
    
    # 메트릭 계산
    total_news = last_24h['news_count'].sum()
    avg_sentiment = last_24h['news_sentiment_avg'].mean()
    bullish_ratio = (last_24h['news_bullish_count'].sum() / 
                    (last_24h['news_count'].sum() + 1e-10))
    bearish_ratio = (last_24h['news_bearish_count'].sum() / 
                    (last_24h['news_count'].sum() + 1e-10))
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📰 24시간 뉴스",
            value=f"{int(total_news)}건",
            delta=f"시간당 {total_news/24:.1f}건"
        )
    
    with col2:
        sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😐" if avg_sentiment > -0.1 else "😔"
        st.metric(
            label=f"{sentiment_emoji} 뉴스 감정",
            value=f"{avg_sentiment:.3f}",
            delta="긍정적" if avg_sentiment > 0 else "부정적" if avg_sentiment < 0 else "중립"
        )
    
    with col3:
        st.metric(
            label="🚀 강세 뉴스",
            value=f"{bullish_ratio*100:.1f}%",
            delta=f"{last_24h['news_bullish_count'].sum():.0f}건"
        )
    
    with col4:
        st.metric(
            label="📉 약세 뉴스",
            value=f"{bearish_ratio*100:.1f}%",
            delta=f"{last_24h['news_bearish_count'].sum():.0f}건"
        )


def show_news_trend_chart(df, hours=168):
    """뉴스 트렌드 차트 (시간별 뉴스 수 + 감정)"""
    
    # 최근 N시간 데이터
    latest_time = df['timestamp'].max()
    recent = df[df['timestamp'] >= latest_time - timedelta(hours=hours)].copy()
    
    if recent.empty:
        st.warning("표시할 뉴스 데이터가 없습니다.")
        return
    
    # 차트 생성
    fig = go.Figure()
    
    # 뉴스 수 (막대 그래프)
    fig.add_trace(go.Bar(
        x=recent['timestamp'],
        y=recent['news_count'],
        name='뉴스 수',
        marker_color='lightblue',
        yaxis='y1',
        opacity=0.7
    ))
    
    # 감정 점수 (선 그래프)
    fig.add_trace(go.Scatter(
        x=recent['timestamp'],
        y=recent['news_sentiment_avg'],
        name='감정 점수',
        line=dict(color='orange', width=2),
        yaxis='y2'
    ))
    
    # 레이아웃
    fig.update_layout(
        title=f'📰 뉴스 트렌드 (최근 {hours}시간)',
        xaxis=dict(title='시간'),
        yaxis=dict(
            title='뉴스 수',
            side='left'
        ),
        yaxis2=dict(
            title='감정 점수',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_news_topic_distribution(df):
    """뉴스 주제 분포 (최근 7일)"""
    
    # 최근 7일 데이터
    latest_time = df['timestamp'].max()
    last_week = df[df['timestamp'] >= latest_time - timedelta(days=7)]
    
    if last_week.empty:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    # 주제별 합계
    topics = {
        '비트코인': last_week['news_bitcoin_mentions'].sum(),
        '이더리움': last_week['news_ethereum_mentions'].sum(),
        '알트코인': last_week['news_altcoin_mentions'].sum(),
        '규제': last_week['news_regulation_mentions'].sum(),
        '고래': last_week['news_whale_mentions'].sum(),
    }
    
    # 파이 차트
    fig = go.Figure(data=[go.Pie(
        labels=list(topics.keys()),
        values=list(topics.values()),
        hole=0.4,
        marker=dict(colors=['#f7931a', '#627eea', '#00d4ff', '#ff6b6b', '#4ecdc4'])
    )])
    
    fig.update_layout(
        title='📊 뉴스 주제 분포 (최근 7일)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_market_temperature_gauge(df):
    """시장 온도 게이지 (0~100)"""
    
    # 현재 시장 온도
    latest = df.iloc[-1] if not df.empty else None
    
    if latest is None or 'market_temperature' not in df.columns:
        st.warning("시장 온도 데이터가 없습니다.")
        return
    
    temp = latest['market_temperature']
    
    # 게이지 차트
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=temp,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "🌡️ 시장 온도", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "blue"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#e3f2fd'},  # 차가움
                {'range': [30, 70], 'color': '#fff9c4'},  # 중립
                {'range': [70, 100], 'color': '#ffebee'}  # 뜨거움
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': temp
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 설명
    if temp < 30:
        status = "❄️ 차가움 - 시장 활동 저조"
    elif temp < 70:
        status = "🌤️ 중립 - 정상 범위"
    else:
        status = "🔥 뜨거움 - 시장 과열 주의"
    
    st.caption(status)


def show_sentiment_comparison(df):
    """소스별 감정 비교 (최근 7일)"""
    
    # 최근 7일 데이터
    latest_time = df['timestamp'].max()
    last_week = df[df['timestamp'] >= latest_time - timedelta(days=7)]
    
    if last_week.empty:
        return
    
    # 일별 평균 계산
    last_week['date'] = last_week['timestamp'].dt.date
    daily = last_week.groupby('date').agg({
        'telegram_avg_sentiment': 'mean',
        'twitter_sentiment': 'mean',
        'news_sentiment_avg': 'mean',
        'combined_sentiment': 'mean'
    }).reset_index()
    
    # 차트
    fig = go.Figure()
    
    if 'telegram_avg_sentiment' in daily.columns:
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['telegram_avg_sentiment'],
            name='텔레그램',
            mode='lines+markers'
        ))
    
    if 'twitter_sentiment' in daily.columns:
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['twitter_sentiment'],
            name='트위터',
            mode='lines+markers'
        ))
    
    if 'news_sentiment_avg' in daily.columns:
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['news_sentiment_avg'],
            name='뉴스',
            mode='lines+markers'
        ))
    
    if 'combined_sentiment' in daily.columns:
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['combined_sentiment'],
            name='종합',
            mode='lines+markers',
            line=dict(width=3, dash='dash')
        ))
    
    fig.update_layout(
        title='😊 소스별 감정 트렌드 (최근 7일)',
        xaxis_title='날짜',
        yaxis_title='감정 점수',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_news_alerts_table(alerts_df, limit=20):
    """뉴스 기반 알람 테이블"""
    
    if alerts_df.empty:
        st.info("최근 뉴스 기반 알람이 없습니다.")
        return
    
    # 최근 알람만
    recent_alerts = alerts_df.head(limit).copy()
    
    # 포맷팅
    recent_alerts['timestamp'] = pd.to_datetime(recent_alerts['timestamp']).dt.strftime('%m-%d %H:%M')
    recent_alerts['priority_score'] = recent_alerts['priority_score'].astype(int)
    recent_alerts['news_count'] = recent_alerts['news_count'].astype(int)
    recent_alerts['btc_change'] = recent_alerts['btc_change'].apply(lambda x: f"{x:.2f}%")
    
    # 레벨별 색상
    def color_level(val):
        if val == 'CRITICAL':
            return 'background-color: #ff4444; color: white; font-weight: bold'
        elif val == 'HIGH':
            return 'background-color: #ff9800; color: white'
        else:
            return 'background-color: #ffc107'
    
    # 표시할 컬럼
    display_cols = ['timestamp', 'alert_level', 'priority_score', 'reasons', 
                   'news_count', 'btc_change']
    
    display_df = recent_alerts[display_cols].copy()
    display_df.columns = ['시간', '레벨', '점수', '사유', '뉴스수', 'BTC변화']
    
    # 스타일 적용
    styled = display_df.style.applymap(color_level, subset=['레벨'])
    
    st.dataframe(styled, use_container_width=True, height=400)


def show_combined_activity_chart(df, hours=72):
    """종합 활동 지수 차트"""
    
    # 최근 N시간
    latest_time = df['timestamp'].max()
    recent = df[df['timestamp'] >= latest_time - timedelta(hours=hours)].copy()
    
    if recent.empty or 'combined_activity' not in recent.columns:
        return
    
    fig = go.Figure()
    
    # 종합 활동
    fig.add_trace(go.Scatter(
        x=recent['timestamp'],
        y=recent['combined_activity'],
        name='종합 활동',
        fill='tozeroy',
        line=dict(color='#667eea', width=2),
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    
    # 0선 표시
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=f'📈 종합 활동 지수 (최근 {hours}시간)',
        xaxis_title='시간',
        yaxis_title='활동 지수 (Z-score)',
        hovermode='x unified',
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)


# 대시보드 페이지 예시
def show_news_dashboard_page():
    """뉴스 대시보드 전체 페이지"""
    
    st.title("📰 코인뉴스 분석 대시보드")
    
    # 데이터 로드
    @st.cache_data(ttl=300)  # 5분 캐시
    def load_data():
        df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/final_integrated_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        try:
            alerts_df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/news_based_alerts.csv')
            alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
            alerts_df = alerts_df.sort_values('timestamp', ascending=False)
        except:
            alerts_df = pd.DataFrame()
        
        return df, alerts_df
    
    df, alerts_df = load_data()
    
    # 최근 데이터만 (성능을 위해)
    recent_df = df[df['timestamp'] >= df['timestamp'].max() - timedelta(days=30)]
    
    # 요약 메트릭
    st.subheader("📊 24시간 요약")
    show_news_summary_metrics(recent_df)
    
    st.divider()
    
    # 메인 차트들
    col1, col2 = st.columns(2)
    
    with col1:
        # 시장 온도
        show_market_temperature_gauge(recent_df)
        
        # 주제 분포
        show_news_topic_distribution(recent_df)
    
    with col2:
        # 종합 활동
        show_combined_activity_chart(recent_df, hours=72)
        
        # 감정 비교
        show_sentiment_comparison(recent_df)
    
    st.divider()
    
    # 뉴스 트렌드
    st.subheader("📈 뉴스 트렌드")
    hours = st.slider("표시 기간 (시간)", 24, 168, 72, 24)
    show_news_trend_chart(recent_df, hours=hours)
    
    st.divider()
    
    # 알람 테이블
    st.subheader("🚨 최근 뉴스 기반 알람")
    show_news_alerts_table(alerts_df, limit=20)


if __name__ == '__main__':
    # Streamlit 앱 실행 시
    show_news_dashboard_page()

