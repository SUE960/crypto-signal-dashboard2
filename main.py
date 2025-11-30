"""
크립토 시그널 대시보드 - 모던 블랙 테마

텔레그램, 뉴스, 트위터 데이터를 통합하여 실시간 시장 신호 제공
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import DataLoader
from utils.composite_score import CompositeScoreCalculator
from analysis.spike_detector import SpikeDetector

# 페이지 설정
st.set_page_config(
    page_title="Crypto Signal Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 숨김
)

# 모던 블랙 테마 CSS
st.markdown("""
<style>
    /* Streamlit 기본 여백 강제 제거 */
    .stApp {
        background-color: #ffffff;
        color: #000000;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 메인 영역 여백 완전 제거 */
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Streamlit 기본 요소 제거 */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    [data-testid="stHeader"] {
        display: none;
    }
    
    #MainMenu {
        display: none;
    }
    
    footer {
        display: none;
    }
    
    [data-testid="stDecoration"] {
        display: none;
    }
    
    /* 상단 네비게이션 - 가로 100% */
    .top-nav {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 1rem 2rem;
        margin: 0 !important;
        width: 100vw;
        position: relative;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .logo {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    
    /* 가격 헤더 */
    .price-header {
        padding: 1.5rem 2rem;
        margin: 0;
    }
    
    /* 종합 점수 - Upbit 가격 스타일 */
    .price-header {
        display: flex;
        align-items: baseline;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .price-label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 600;
    }
    
    .price-value {
        font-size: 42px;
        font-weight: 700;
        color: #000000;
        line-height: 1;
    }
    
    .price-unit {
        font-size: 18px;
        color: #6b7280;
        font-weight: 500;
        margin-left: 4px;
    }
    
    .price-change {
        font-size: 14px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .price-change .symbol {
        font-size: 12px;
    }
    
    /* 신호 박스 카드 - 작고 컴팩트 */
    .signal-box {
        background: rgba(50, 50, 50, 0.3);
        border: 1px solid rgba(100, 100, 100, 0.3);
        border-radius: 8px;
        padding: 12px 8px;
        margin: 4px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    
    .signal-box:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.15);
    }
    
    .signal-title {
        font-size: 11px;
        font-weight: 600;
        color: #00d4ff;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }
    
    .signal-arrow {
        font-size: 20px;
        text-align: center;
        margin: 4px 0;
        color: #7b2ff7;
        line-height: 1;
    }
    
    .signal-value {
        font-size: 18px;
        font-weight: 700;
        text-align: center;
        color: #00d4ff;
        line-height: 1.2;
    }
    
    .signal-label {
        font-size: 9px;
        text-align: center;
        color: #888;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    
    /* 차트 컨테이너 */
    .chart-container {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 16px 16px 0;
    }
    
    /* 지표 리스트 - Upbit 흰색 스타일 */
    .indicator-list {
        background: #ffffff;
        border-radius: 8px;
        padding: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
        margin: 16px 0;
    }
    
    .indicator-header {
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
        font-size: 14px;
        font-weight: 700;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .indicator-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 16px;
        border-bottom: 1px solid #f3f4f6;
        transition: background 0.2s;
    }
    
    .indicator-item:hover {
        background: #f9fafb;
    }
    
    .indicator-item:last-child {
        border-bottom: none;
    }
    
    .indicator-name {
        font-size: 13px;
        color: #374151;
        font-weight: 500;
    }
    
    .indicator-value {
        font-size: 15px;
        font-weight: 700;
        text-align: right;
        color: #111827;
    }
    
    .indicator-change {
        font-size: 11px;
        text-align: right;
        margin-top: 2px;
        font-weight: 600;
    }
    
    .positive {
        color: #dc2626;
    }
    
    .negative {
        color: #2563eb;
    }
    
    .neutral {
        color: #6b7280;
    }
    
    /* 탭 스타일 - 업비트 스타일 (흰색 배경, 파란색 텍스트) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-bottom: 1px solid #e5e7eb;
        padding: 0;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: none;
        border-bottom: 2px solid transparent;
        color: #9ca3af;
        font-weight: 400;
        font-size: 14px;
        padding: 14px 20px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #ffffff;
        color: #374151;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border-bottom: 2px solid #1e3a8a !important;
        font-weight: 600;
    }
    
    /* CTA 버튼 */
    .cta-button {
        background: linear-gradient(135deg, #00ff87 0%, #00d4ff 100%);
        color: #000;
        padding: 20px 48px;
        border-radius: 12px;
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        margin: 32px auto;
        box-shadow: 0 8px 32px rgba(0, 255, 135, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 48px rgba(0, 255, 135, 0.5);
    }
    
    /* 스파이크 알람 */
    .spike-alert {
        background: linear-gradient(135deg, #ff0055 0%, #ff8800 100%);
        border-radius: 12px;
        padding: 16px 24px;
        margin: 8px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* 데이터 테이블 */
    .dataframe {
        background-color: #1a1a1a;
        color: #ffffff;
        border-radius: 12px;
    }
    
    /* 차트 배경 */
    .js-plotly-plot {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_all_data():
    """모든 데이터 로드 (5분 캐시)"""
    loader = DataLoader()
    
    # 전처리된 데이터 로드 (상대 경로)
    try:
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'processed_data.csv')
        df_main = pd.read_csv(data_path)
        df_main['timestamp'] = pd.to_datetime(df_main['timestamp'])
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        df_main = pd.DataFrame()
    
    # 개별 소스 데이터
    data = loader.load_all_data()
    
    return df_main, data


def render_top_navigation():
    """상단 네비게이션 렌더링"""
    st.markdown("""
    <div class="top-nav">
        <div class="logo">CRYPTO SIGNAL DASHBOARD</div>
        <div style="color: rgba(255, 255, 255, 0.8); font-size: 13px; font-weight: 500;">
            Real-time Market Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)


def calculate_correlations_with_price(df):
    """코인 가격과의 상관관계 계산"""
    correlations = {}
    
    if df.empty or 'ETH_close' not in df.columns:
        return correlations
    
    # 트위터 인플루언서
    if 'twitter_count' in df.columns:
        correlations['트위터 게시글 수'] = df['twitter_count'].corr(df['ETH_close'])
    if 'twitter_sentiment_compound' in df.columns:
        correlations['트위터 감정 분석'] = df['twitter_sentiment_compound'].corr(df['ETH_close'])
    
    # 텔레그램
    if 'message_count' in df.columns:
        correlations['텔레그램 게시글 수'] = df['message_count'].corr(df['ETH_close'])
    if 'avg_sentiment' in df.columns:
        correlations['텔레그램 감정 분석'] = df['avg_sentiment'].corr(df['ETH_close'])
    
    # 코인니스 (데이터 수집 중)
    correlations['코인니스 게시글 수'] = None  # 데이터 수집 중
    correlations['코인니스 감정 분석'] = None  # 데이터 수집 중
    
    return correlations


def calculate_correlations_with_whale(df):
    """고래 지갑과의 상관관계 계산"""
    correlations = {}
    
    if df.empty or 'tx_frequency' not in df.columns:
        return correlations
    
    # 트위터 인플루언서
    if 'twitter_count' in df.columns:
        correlations['트위터 게시글 수'] = df['twitter_count'].corr(df['tx_frequency'])
    if 'twitter_sentiment_compound' in df.columns:
        correlations['트위터 감정 분석'] = df['twitter_sentiment_compound'].corr(df['tx_frequency'])
    
    # 텔레그램
    if 'message_count' in df.columns:
        correlations['텔레그램 게시글 수'] = df['message_count'].corr(df['tx_frequency'])
    if 'avg_sentiment' in df.columns:
        correlations['텔레그램 감정 분석'] = df['avg_sentiment'].corr(df['tx_frequency'])
    
    # 코인니스 (데이터 수집 중)
    correlations['코인니스 게시글 수'] = None  # 데이터 수집 중
    correlations['코인니스 감정 분석'] = None  # 데이터 수집 중
    
    return correlations


def render_correlation_indicators(correlations, target_name):
    """상관관계 지표 표시 (Upbit 스타일)"""
    st.markdown(f"""
    <div style="padding: 16px; background: #f9fafb; border-radius: 8px; margin-bottom: 16px;">
        <div style="font-size: 13px; color: #6b7280; margin-bottom: 8px;">
            각 지표와 <strong>{target_name}</strong>의 상관관계 (Pearson Correlation)
        </div>
        <div style="font-size: 12px; color: #9ca3af;">
            -1.0 ~ 1.0 범위: 1.0에 가까울수록 강한 양의 상관관계, -1.0에 가까울수록 강한 음의 상관관계
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="indicator-list">', unsafe_allow_html=True)
    
    for name, value in correlations.items():
        if value is None:
            # 데이터 수집 중
            st.markdown(f"""
            <div class="indicator-item">
                <div>
                    <div class="indicator-name">{name}</div>
                </div>
                <div>
                    <div class="indicator-value neutral" style="font-size: 13px;">
                        데이터 수집 중
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 상관계수 값 표시
            if abs(value) >= 0.7:
                strength = "강한 상관관계"
                color_class = "positive" if value > 0 else "negative"
            elif abs(value) >= 0.4:
                strength = "중간 상관관계"
                color_class = "neutral"
            else:
                strength = "약한 상관관계"
                color_class = "neutral"
            
            st.markdown(f"""
            <div class="indicator-item">
                <div>
                    <div class="indicator-name">{name}</div>
                </div>
                <div>
                    <div class="indicator-value {color_class}">{value:.4f}</div>
                    <div class="indicator-change neutral">{strength}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_recent_news(df_news):
    """최근 뉴스 표시"""
    st.markdown("""
    <div style="padding: 24px; background: #f9fafb; border-radius: 8px; text-align: center;">
        <div style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 12px;">
            📰 코인니스 뉴스
        </div>
        <div style="font-size: 14px; color: #6b7280; margin-bottom: 24px;">
            실시간 암호화폐 뉴스를 수집 중입니다
        </div>
        <div style="padding: 48px; background: #ffffff; border: 2px dashed #e5e7eb; border-radius: 8px;">
            <div style="font-size: 48px; margin-bottom: 16px;">⏳</div>
            <div style="font-size: 15px; color: #9ca3af;">
                데이터 수집 진행 중...
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_news.empty:
        st.markdown("### 최근 수집된 뉴스")
        st.dataframe(df_news.head(10), use_container_width=True)


def render_spike_table(df):
    """스파이크 알람 시계열 표"""
    st.markdown("## 🔔 Spike Alerts")
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return
    
    try:
        # 스파이크 감지
        detector = SpikeDetector(df)
        
        # 최근 스파이크만
        recent_spikes = []
        
        if 'message_count' in df.columns:
            msg_spikes = detector.detect_zscore_spike('message_count', threshold=2.0)
            if not msg_spikes.empty:
                recent_spikes.append(msg_spikes.tail(10))
        
        if recent_spikes:
            spike_df = pd.concat(recent_spikes).sort_values('timestamp', ascending=False)
            
            for _, row in spike_df.head(5).iterrows():
                st.markdown(f"""
                <div class="spike-alert">
                    <strong>⚡ SPIKE DETECTED</strong> | 
                    {row['timestamp'].strftime('%Y-%m-%d %H:%M')} | 
                    {row['spike_column']}: {row['spike_magnitude']:.2f}σ
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent spikes detected")
    except Exception as e:
        st.error(f"스파이크 감지 오류: {e}")


def render_cta_button():
    """차익거래 CTA 버튼"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h2 style="margin-bottom: 24px;">💰 지금이 기회입니다</h2>
            <p style="font-size: 18px; color: #888; margin-bottom: 32px;">
                실시간 시장 신호를 활용한 스마트 차익거래 전략
            </p>
            <a href="https://whale-arbitrage-qwodzy8wpnhpgxaxt23rj8.streamlit.app/" 
               target="_blank" class="cta-button">
                차익거래 시작하기 →
            </a>
        </div>
        """, unsafe_allow_html=True)


def main():
    """메인 함수 - Upbit 스타일 레이아웃"""
    # 상단 네비게이션
    render_top_navigation()
    
    # 데이터 로드
    with st.spinner("Loading market data..."):
        df_main, data = load_all_data()
    
    if df_main.empty:
        st.error("데이터를 로드할 수 없습니다. 먼저 python scripts/preprocess_data.py를 실행하세요.")
        return
    
    # 신호 점수 계산 (화면에는 표시 안 함)
    calculator = CompositeScoreCalculator()
    try:
        df_scored = calculator.calculate_composite_score(
            df_main, 
            df_news=data.get('coinness', pd.DataFrame()), 
            df_twitter=data.get('twitter', pd.DataFrame())
        )
        
        # 최근 점수
        telegram_score = df_scored['telegram_score'].iloc[-1] if not df_scored.empty else 50
        news_score = df_scored['news_score'].iloc[-1] if not df_scored.empty else 50
        twitter_score = df_scored['twitter_score'].iloc[-1] if not df_scored.empty else 50
        composite_score = df_scored['composite_score'].iloc[-1] if not df_scored.empty else 50
        
        # 24시간 변화
        if len(df_scored) > 24:
            composite_score_24h = df_scored['composite_score'].iloc[-25]
            score_change = composite_score - composite_score_24h
            score_change_pct = (score_change / composite_score_24h) * 100 if composite_score_24h != 0 else 0
        else:
            score_change = 0
            score_change_pct = 0
        
        signal_summary = calculator.get_signal_summary(df_scored)
    except Exception as e:
        st.error(f"점수 계산 실패: {e}")
        df_scored = df_main
        telegram_score = news_score = twitter_score = composite_score = 50
        score_change = 0
        score_change_pct = 0
        signal_summary = {'current_level': 'neutral'}
    
    scores = {
        'telegram': telegram_score,
        'news': news_score,
        'twitter': twitter_score,
        'composite': composite_score
    }
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 종합 점수 - Upbit 가격 스타일
    change_class = "positive" if score_change > 0 else "negative" if score_change < 0 else "neutral"
    change_symbol = "▲" if score_change > 0 else "▼" if score_change < 0 else "−"
    
    st.markdown(f"""
    <div class="price-header">
        <div>
            <div class="price-label">크립토 시그널 지수</div>
            <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 8px;">
                <span class="price-value">{composite_score:,.1f}</span>
                <span class="price-unit">SCORE</span>
                <div class="price-change {change_class}">
                    <span class="symbol">{change_symbol}</span>
                    <span>{abs(score_change):.1f} ({abs(score_change_pct):.2f}%)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upbit 스타일 레이아웃: 차트(왼쪽) + 탭+지표(오른쪽)
    st.markdown('<div style="padding: 0 2rem;">', unsafe_allow_html=True)
    col_chart, col_indicators = st.columns([7, 3])
    
    with col_chart:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📈 종합 점수 추이")
        
        if not df_scored.empty and 'composite_score' in df_scored.columns:
            # 종합 점수 차트
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_scored['timestamp'],
                y=df_scored['composite_score'],
                name='Composite Score',
                line=dict(color='#3b82f6', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            fig.update_layout(
                template='plotly_white',
                paper_bgcolor='#ffffff',
                plot_bgcolor='#ffffff',
                height=600,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#f3f4f6',
                    title='시간',
                    title_font=dict(size=12, color='#6b7280')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#f3f4f6',
                    title='점수',
                    title_font=dict(size=12, color='#6b7280'),
                    range=[0, 100]
                ),
                hovermode='x unified',
                font=dict(color='#374151')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_indicators:
        # 탭 추가 - 오른쪽 지표 영역
        st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            background-color: #ffffff;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: #ffffff;
            border-radius: 0px;
            color: #6b7280;
            font-weight: 600;
            font-size: 12px;
            padding: 0 12px;
            border-bottom: 2px solid transparent;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
            color: #3b82f6;
            border-bottom: 2px solid #3b82f6;
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["코인가격 관계", "고래지갑 관계", "지금 뉴스"])
        
        with tab1:
            # 코인가격과의 상관관계 계산
            correlations_price = calculate_correlations_with_price(df_scored)
            render_correlation_indicators(correlations_price, "코인 가격")
        
        with tab2:
            # 고래지갑과의 상관관계 계산
            correlations_whale = calculate_correlations_with_whale(df_scored)
            render_correlation_indicators(correlations_whale, "고래 거래")
        
        with tab3:
            # 최근 뉴스 표시
            render_recent_news(data.get('coinness', pd.DataFrame()))
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
