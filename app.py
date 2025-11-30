"""
암호화폐 커뮤니티-거래 상관관계 대시보드

메인 Streamlit 애플리케이션
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import timedelta

# 경로 추가
sys.path.append('/Volumes/T7/class/2025-FALL/big_data')

from utils.data_loader import DataLoader
from analysis.correlation_analysis import CorrelationAnalyzer
from analysis.spike_detector import RealTimeSpikeMonitor
from utils.alert_system import AlertSystem
from components import charts, metrics, filters, alerts
from styles.coinness_theme import get_global_css, COLORS


# 페이지 설정
st.set_page_config(
    page_title="코인니스 스타일 암호화폐 대시보드",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 코인니스 스타일 적용
st.markdown(get_global_css(dark_mode=False), unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # 1시간 캐시
def load_data():
    """데이터 로드 (캐시됨)"""
    try:
        df = pd.read_csv('/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("전처리된 데이터 파일이 없습니다. `python scripts/preprocess_data.py`를 먼저 실행하세요.")
        return pd.DataFrame()


def overview_page(df):
    """Overview 페이지"""
    if df.empty:
        st.warning("데이터가 없습니다.")
        return
    
    # 날짜 필터
    st.sidebar.subheader("필터")
    start_date, end_date = filters.date_range_filter(df, key_prefix="overview")
    filtered_df = filters.apply_date_filter(df, start_date, end_date)
    
    st.sidebar.markdown(f"**데이터 범위:** {len(filtered_df)} 시간")
    
    # 실시간 티커 (코인니스 스타일)
    if not filtered_df.empty:
        latest_data = filtered_df.iloc[-1]
        prev_data = filtered_df.iloc[-25] if len(filtered_df) >= 25 else filtered_df.iloc[0]
        
        eth_price = latest_data.get('ETH_close', 0)
        eth_change = ((eth_price - prev_data.get('ETH_close', eth_price)) / prev_data.get('ETH_close', eth_price) * 100) if prev_data.get('ETH_close', 0) != 0 else 0
        
        btc_price = latest_data.get('BTC_close', 0)
        btc_change = ((btc_price - prev_data.get('BTC_close', btc_price)) / prev_data.get('BTC_close', btc_price) * 100) if prev_data.get('BTC_close', 0) != 0 else 0
        
        eth_color = COLORS['success'] if eth_change >= 0 else COLORS['danger']
        btc_color = COLORS['success'] if btc_change >= 0 else COLORS['danger']
        
        st.markdown(f"""
        <div class="ticker-container">
            <div class="ticker-item">
                <div class="ticker-label">ETH/USDT</div>
                <div class="ticker-value">${eth_price:,.2f}</div>
                <div class="ticker-change" style="color: {eth_color};">
                    {'+' if eth_change >= 0 else ''}{eth_change:.2f}%
                </div>
            </div>
            <div class="ticker-item">
                <div class="ticker-label">BTC/USDT</div>
                <div class="ticker-value">${btc_price:,.2f}</div>
                <div class="ticker-change" style="color: {btc_color};">
                    {'+' if btc_change >= 0 else ''}{btc_change:.2f}%
                </div>
            </div>
            <div class="ticker-item">
                <div class="ticker-label">시장 도미넌스</div>
                <div class="ticker-value">BTC 58.8%</div>
                <div class="ticker-label" style="font-size: 11px; margin-top: 4px;">
                    데이터 기간: {len(filtered_df)}시간
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 주요 지표 카드 (코인니스 스타일)
    st.markdown('### 주요 지표', unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom: 24px;"></div>', unsafe_allow_html=True)
    
    # 메트릭 데이터 계산
    current_eth, change_eth, change_pct_eth = metrics.calculate_price_change(filtered_df, 'ETH', '24h')
    current_btc, change_btc, change_pct_btc = metrics.calculate_price_change(filtered_df, 'BTC', '24h')
    community_stats = metrics.calculate_community_stats(filtered_df, 24)
    whale_stats = metrics.calculate_whale_activity(filtered_df, 24)
    
    # 코인니스 스타일 메트릭 카드 표시
    metrics_data = [
        {
            'title': 'ETH 가격',
            'value': f"${current_eth:,.2f}",
            'delta': metrics.format_percentage(change_pct_eth),
            'icon': 'ETH',
            'type': 'info' if change_pct_eth >= 0 else 'danger'
        },
        {
            'title': 'BTC 가격',
            'value': f"${current_btc:,.2f}",
            'delta': metrics.format_percentage(change_pct_btc),
            'icon': 'BTC',
            'type': 'info' if change_pct_btc >= 0 else 'danger'
        },
        {
            'title': '24시간 메시지',
            'value': f"{int(community_stats['total_messages']):,}",
            'delta': f"감정: {community_stats['avg_sentiment']:.2f}",
            'icon': 'TG',
            'type': 'success' if community_stats['avg_sentiment'] > 0 else 'neutral'
        },
        {
            'title': '고래 거래',
            'value': f"{int(whale_stats['total_tx']):,} 건",
            'delta': f"{metrics.format_large_number(whale_stats['total_amount'])} ETH",
            'icon': 'TX',
            'type': 'info'
        }
    ]
    
    metrics.display_coinness_metrics_row(metrics_data)
    
    # === 메인 통합 차트 (3-in-1) ===
    st.markdown('### 통합 분석: 가격 vs 고래 거래 vs 텔레그램 활동', unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom: 16px;"></div>', unsafe_allow_html=True)
    
    # 3-in-1 통합 차트 생성
    fig_integrated = charts.create_triple_axis_chart(
        filtered_df,
        title="",
        height=600
    )
    st.plotly_chart(fig_integrated, use_container_width=True)
    
    st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)
    
    # 시계열 차트
    st.markdown('### 시계열 분석', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["가격 & 커뮤니티", "거래량", "감정 분석"])
    
    with tab1:
        # 이중 축 차트: ETH 가격 & 메시지 수
        if 'message_count' in filtered_df.columns:
            fig = charts.create_multi_axis_chart(
                filtered_df,
                'ETH_close',
                'message_count',
                title="ETH 가격 vs 텔레그램 메시지 수",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("텔레그램 데이터가 없습니다.")
        
        # 캔들스틱 차트
        coin = filters.coin_selector("코인 선택", default="ETH", key_prefix="overview_candle")
        fig_candle = charts.create_candlestick_chart(filtered_df, coin=coin, height=400)
        st.plotly_chart(fig_candle, use_container_width=True)
    
    with tab2:
        # 거래량 차트
        col1, col2 = st.columns(2)
        with col1:
            fig_vol_eth = charts.create_volume_chart(filtered_df, 'ETH', height=350)
            st.plotly_chart(fig_vol_eth, use_container_width=True)
        with col2:
            fig_vol_btc = charts.create_volume_chart(filtered_df, 'BTC', height=350)
            st.plotly_chart(fig_vol_btc, use_container_width=True)
    
    with tab3:
        # 감정 분석 차트
        if 'avg_sentiment' in filtered_df.columns:
            fig_sentiment = charts.create_sentiment_chart(filtered_df, height=400)
            st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # 감정 통계
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("평균 감정", f"{filtered_df['avg_sentiment'].mean():.3f}")
            with col2:
                st.metric("긍정 비율", f"{filtered_df['avg_positive'].mean():.1%}")
            with col3:
                st.metric("부정 비율", f"{filtered_df['avg_negative'].mean():.1%}")
        else:
            st.info("감정 데이터가 없습니다.")
    
    # 비교 차트
    st.markdown('### 주요 지표 비교 (정규화)', unsafe_allow_html=True)
    
    # 기본 컬럼 설정 (존재하는 것만)
    default_compare_cols = []
    for col in ['ETH_close', 'message_count', 'tx_frequency']:
        if col in filtered_df.columns:
            default_compare_cols.append(col)
    
    compare_cols = filters.column_selector(
        filtered_df,
        "비교할 변수 선택",
        default_columns=default_compare_cols if default_compare_cols else None,
        key_prefix="overview_compare"
    )
    
    if compare_cols:
        fig_compare = charts.create_comparison_chart(
            filtered_df,
            compare_cols,
            normalize=True,
            title="주요 지표 비교 (0~1 정규화)",
            height=400
        )
        st.plotly_chart(fig_compare, use_container_width=True)


def correlation_page(df):
    """🔍 상관관계 분석 페이지"""
    st.markdown('# 🔍 상관관계 분석', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return
    
    # 날짜 필터
    st.sidebar.subheader("🔍 필터")
    start_date, end_date = filters.date_range_filter(df, key_prefix="corr")
    filtered_df = filters.apply_date_filter(df, start_date, end_date)
    
    analyzer = CorrelationAnalyzer(filtered_df)
    
    # 상관계수 히트맵
    st.markdown('### 🔥 상관계수 히트맵', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Pearson 상관계수", "Spearman 상관계수"])
    
    with tab1:
        # 주요 변수 선택
        key_columns = []
        for col in ['ETH_close', 'BTC_close', 'message_count', 'tx_frequency', 
                   'avg_sentiment', 'ETH_volume', 'total_reactions']:
            if col in filtered_df.columns:
                key_columns.append(col)
        
        pearson_corr = analyzer.pearson_correlation(key_columns)
        fig_pearson = charts.create_correlation_heatmap(
            pearson_corr,
            title="Pearson 상관계수 (선형 관계)",
            height=600
        )
        st.plotly_chart(fig_pearson, use_container_width=True)
    
    with tab2:
        spearman_corr = analyzer.spearman_correlation(key_columns)
        fig_spearman = charts.create_correlation_heatmap(
            spearman_corr,
            title="Spearman 상관계수 (순위 기반)",
            height=600
        )
        st.plotly_chart(fig_spearman, use_container_width=True)
    
    # ETH 가격과의 상관관계 Top 10
    st.markdown('### 🏆 ETH 가격과 상관관계 Top 10', unsafe_allow_html=True)
    
    top_corr = analyzer.get_top_correlations('ETH_close', n=10, method='pearson')
    
    if not top_corr.empty:
        corr_df = pd.DataFrame({
            '변수': top_corr.index,
            '상관계수': top_corr.values,
            '상관관계 강도': [metrics.get_correlation_strength(v) for v in top_corr.values]
        })
        
        st.dataframe(corr_df, hide_index=True, use_container_width=True)
    
    # 시차 상관관계 분석
    if 'message_count' in filtered_df.columns:
        st.markdown('### ⏰ 시차 상관관계 분석', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.write("**설정**")
            lag_var1 = st.selectbox(
                "선행 변수",
                options=[c for c in filtered_df.columns if c != 'timestamp' and filtered_df[c].dtype in ['float64', 'int64']],
                index=[c for c in filtered_df.columns if c != 'timestamp' and filtered_df[c].dtype in ['float64', 'int64']].index('message_count') 
                    if 'message_count' in filtered_df.columns else 0,
                key="lag_var1"
            )
            
            lag_var2 = st.selectbox(
                "후행 변수",
                options=[c for c in filtered_df.columns if c != 'timestamp' and filtered_df[c].dtype in ['float64', 'int64']],
                index=[c for c in filtered_df.columns if c != 'timestamp' and filtered_df[c].dtype in ['float64', 'int64']].index('ETH_close') 
                    if 'ETH_close' in filtered_df.columns else 1,
                key="lag_var2"
            )
            
            max_lag = st.slider("최대 시차 (시간)", 1, 48, 24)
        
        with col1:
            if lag_var1 and lag_var2:
                lag_corr = analyzer.lag_correlation(lag_var1, lag_var2, max_lag=max_lag)
                
                if not lag_corr.empty:
                    fig_lag = charts.create_lag_correlation_chart(
                        lag_corr,
                        title=f"{lag_var1} → {lag_var2} 시차 상관관계",
                        height=400
                    )
                    st.plotly_chart(fig_lag, use_container_width=True)
                    
                    # 가장 높은 상관관계 시차
                    max_corr_row = lag_corr.loc[lag_corr['correlation'].abs().idxmax()]
                    st.info(f"**최대 상관관계:** Lag {int(max_corr_row['lag'])}시간, "
                           f"상관계수 = {max_corr_row['correlation']:.3f}, "
                           f"p-value = {max_corr_row['p_value']:.4f}")
    
    # 그랜저 인과관계 검정
    if 'message_count' in filtered_df.columns and 'ETH_close' in filtered_df.columns:
        st.markdown('### 🔗 그랜저 인과관계 검정', unsafe_allow_html=True)
        
        st.write("**메시지 수 → ETH 가격** 인과관계 검정")
        
        granger_result = analyzer.granger_causality_test('message_count', 'ETH_close', max_lag=12)
        
        if isinstance(granger_result, pd.DataFrame):
            significant = granger_result[granger_result['significant']]
            
            if not significant.empty:
                st.success(f"✅ 유의한 인과관계가 발견되었습니다! (시차: {significant['lag'].tolist()})")
                st.dataframe(significant, hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ 유의한 인과관계가 발견되지 않았습니다.")
            
            # 전체 결과 표시
            with st.expander("전체 검정 결과 보기"):
                st.dataframe(granger_result, hide_index=True, use_container_width=True)
        else:
            st.error(f"검정 실패: {granger_result.get('error', '알 수 없는 오류')}")
    
    # 변동성 분석
    if 'message_count_zscore' in filtered_df.columns:
        st.markdown('### 커뮤니티 활동 급증 시 가격 변동성', unsafe_allow_html=True)
        
        threshold_vol = st.slider("Z-score 임계값", 1.0, 5.0, 2.0, 0.1, key="vol_threshold")
        
        vol_result = analyzer.volatility_analysis('message_count_zscore', 'ETH_close', threshold=threshold_vol)
        
        if 'error' not in vol_result:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("트리거 이벤트 수", vol_result['trigger_events_count'])
            
            with col2:
                st.metric("이벤트 시 변동성", f"{vol_result['avg_volatility_during_events']:.2f}%")
            
            with col3:
                st.metric("평상시 변동성", f"{vol_result['avg_volatility_normal']:.2f}%")
            
            with col4:
                ratio = vol_result['volatility_ratio']
                st.metric("변동성 비율", f"{ratio:.2f}x", 
                         delta=f"{(ratio - 1) * 100:.0f}%",
                         delta_color="inverse" if ratio > 1 else "normal")
        else:
            st.warning(vol_result['error'])


def alerts_page(df):
    """스파이크 알람 페이지"""
    st.markdown('# 스파이크 알람', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return
    
    # 알람 시스템 초기화
    alert_system = AlertSystem()
    
    # 필터
    st.sidebar.subheader("필터")
    filter_settings = alerts.create_alert_filter_ui()
    
    # 알람 설정
    alert_settings = alerts.display_alert_settings()
    
    st.markdown("---")
    
    # 스파이크 모니터 초기화
    monitor = RealTimeSpikeMonitor(df, config=alert_settings)
    
    # 스파이크 감지 실행
    with st.spinner("스파이크 감지 중..."):
        spike_results = monitor.check_all_spikes()
    
    # 결과 요약
    st.markdown('### 감지 결과 요약', unsafe_allow_html=True)
    
    total_spikes = sum(len(spikes) for spikes in spike_results.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 스파이크", total_spikes)
    
    with col2:
        zscore_spikes = sum(len(v) for k, v in spike_results.items() if 'zscore' in k)
        st.metric("Z-score 스파이크", zscore_spikes)
    
    with col3:
        ma_spikes = sum(len(v) for k, v in spike_results.items() if 'ma' in k)
        st.metric("이동평균 스파이크", ma_spikes)
    
    with col4:
        corr_spikes = len(spike_results.get('correlation', []))
        st.metric("상관 스파이크", corr_spikes)
    
    # 최근 알람
    st.markdown('### 🔔 최근 감지된 스파이크', unsafe_allow_html=True)
    
    hours = filters.convert_period_to_hours(filter_settings['time_range'])
    recent_alerts_df = monitor.get_recent_alerts(hours=hours if hours else 24 * 365)
    
    if not recent_alerts_df.empty:
        # 레벨 필터 적용
        if filter_settings['alert_levels']:
            recent_alerts_df = recent_alerts_df[
                recent_alerts_df['alert_level'].isin(filter_settings['alert_levels'])
            ]
        
        # 정렬
        if filter_settings['sort_by'] == '최신순':
            recent_alerts_df = recent_alerts_df.sort_values('timestamp', ascending=False)
        elif filter_settings['sort_by'] == '크기순':
            recent_alerts_df = recent_alerts_df.sort_values('spike_magnitude', ascending=False)
        
        alerts.display_alert_summary(recent_alerts_df)
        
        st.markdown("---")
        
        # 최신 알람 카드
        alerts.display_latest_alerts(recent_alerts_df, n=5)
        
        # 전체 알람 테이블
        with st.expander("전체 알람 보기"):
            alerts.display_alert_table(recent_alerts_df)
    else:
        st.info("최근 감지된 스파이크가 없습니다.")
    
    # 스파이크 타임라인
    st.markdown('### 📅 스파이크 타임라인', unsafe_allow_html=True)
    
    # 모든 스파이크 합치기
    all_spikes = []
    for spike_type, spike_data in spike_results.items():
        if not spike_data.empty:
            all_spikes.append(spike_data)
    
    if all_spikes:
        combined_spikes = pd.concat(all_spikes, ignore_index=True)
        fig_timeline = charts.create_spike_timeline(combined_spikes, height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("스파이크가 없습니다.")
    
    # 스파이크 유형별 상세
    st.markdown('### 📝 스파이크 유형별 상세', unsafe_allow_html=True)
    
    for spike_type, spike_data in spike_results.items():
        if not spike_data.empty:
            with st.expander(f"{spike_type} ({len(spike_data)}개)"):
                st.dataframe(spike_data.head(10), hide_index=True, use_container_width=True)


def main():
    """메인 함수"""
    # 사이드바
    st.sidebar.title("네비게이션")
    
    # 다크모드 토글 (코인니스 스타일)
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    ">
        <div style="color: white; font-size: 14px; font-weight: 600;">
            코인니스 스타일 대시보드
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "페이지 선택",
        ["Overview", "상관관계 분석", "스파이크 알람"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # 데이터 로드
    with st.spinner("데이터 로딩 중..."):
        df = load_data()
    
    if not df.empty:
        st.sidebar.success(f"데이터 로드 완료\n\n**기간:** {df['timestamp'].min().date()} ~ {df['timestamp'].max().date()}\n\n**총 {len(df):,} 시간**")
    
    # 페이지 라우팅
    if page == "Overview":
        overview_page(df)
    elif page == "상관관계 분석":
        correlation_page(df)
    elif page == "스파이크 알람":
        alerts_page(df)
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 정보")
    st.sidebar.info("""
    **암호화폐 커뮤니티-거래 상관관계 대시보드**
    
    텔레그램 커뮤니티 활동과 암호화폐 거래량/가격 간의 관계를 분석합니다.
    
    - 실시간 가격 모니터링
    - 상관관계 분석
    - 스파이크 감지 및 알람
    """)


if __name__ == '__main__':
    main()

