"""
알람 UI 컴포넌트

알람 표시 및 관리 위젯들
"""

import streamlit as st
import pandas as pd
import sys
import os

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.metrics import get_alert_color, format_percentage
from styles.coinness_theme import COLORS


def display_alert_card(alert_row):
    """
    단일 알람 카드 표시 (코인니스 스타일)
    
    Args:
        alert_row: 알람 데이터 (Series)
    """
    alert_level = alert_row.get('alert_level', 'medium')
    
    # 레벨별 색상 및 아이콘 (코인니스 스타일)
    level_config = {
        'low': {'color': COLORS['info'], 'bg': f"{COLORS['info']}15", 'icon': '💡'},
        'medium': {'color': COLORS['warning'], 'bg': f"{COLORS['warning']}15", 'icon': '⚠️'},
        'high': {'color': COLORS['danger'], 'bg': f"{COLORS['danger']}15", 'icon': '🚨'},
        'critical': {'color': COLORS['danger'], 'bg': f"{COLORS['danger']}25", 'icon': '🔥'}
    }
    
    config = level_config.get(alert_level, level_config['medium'])
    
    st.markdown(
        f"""
        <div class="alert-card {alert_level}" style="
            border-left: 4px solid {config['color']};
            border-radius: 12px;
            padding: 20px;
            margin: 12px 0;
            background-color: {config['bg']};
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease;
        "
        onmouseover="this.style.transform='translateX(4px)'"
        onmouseout="this.style.transform='translateX(0)'">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">{config['icon']}</span>
                        <strong style="
                            color: {config['color']};
                            font-size: 16px;
                            font-weight: 600;
                        ">
                            {alert_level.upper()}
                        </strong>
                    </div>
                    <p style="
                        margin: 8px 0;
                        font-size: 14px;
                        line-height: 1.5;
                        color: {COLORS['text_primary_light']};
                    ">
                        {alert_row.get('alert_message', '메시지 없음')}
                    </p>
                    <div style="
                        font-size: 12px;
                        color: {COLORS['text_secondary_light']};
                        margin-top: 8px;
                    ">
                        📅 {alert_row.get('timestamp', '')}
                    </div>
                </div>
                <div style="
                    text-align: right;
                    min-width: 80px;
                    padding-left: 16px;
                ">
                    <div style="
                        font-size: 28px;
                        font-weight: 700;
                        color: {config['color']};
                        line-height: 1;
                    ">
                        {alert_row.get('spike_magnitude', 0):.2f}σ
                    </div>
                    <div style="
                        font-size: 11px;
                        color: {COLORS['text_secondary_light']};
                        margin-top: 4px;
                    ">
                        강도
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_alert_table(alerts_df):
    """
    알람 테이블 표시
    
    Args:
        alerts_df: 알람 데이터프레임
    """
    if alerts_df.empty:
        st.info("알람이 없습니다.")
        return
    
    # 표시할 컬럼 선택
    display_cols = []
    for col in ['timestamp', 'alert_level', 'alert_type', 'alert_message', 'spike_magnitude']:
        if col in alerts_df.columns:
            display_cols.append(col)
    
    # 컬럼명 한글화
    column_config = {
        'timestamp': '시간',
        'alert_level': '레벨',
        'alert_type': '유형',
        'alert_message': '메시지',
        'spike_magnitude': '크기'
    }
    
    # 데이터프레임 표시
    st.dataframe(
        alerts_df[display_cols],
        column_config=column_config,
        hide_index=True,
        use_container_width=True
    )


def display_alert_summary(alerts_df):
    """
    알람 요약 통계 표시
    
    Args:
        alerts_df: 알람 데이터프레임
    """
    if alerts_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 알람", 0)
        with col2:
            st.metric("Critical", 0)
        with col3:
            st.metric("High", 0)
        with col4:
            st.metric("Medium/Low", 0)
        return
    
    # 레벨별 집계
    level_counts = alerts_df['alert_level'].value_counts().to_dict() if 'alert_level' in alerts_df.columns else {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 알람", len(alerts_df))
    
    with col2:
        critical_count = level_counts.get('critical', 0)
        st.metric(
            "Critical",
            critical_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        high_count = level_counts.get('high', 0)
        st.metric(
            "High",
            high_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        medium_low = level_counts.get('medium', 0) + level_counts.get('low', 0)
        st.metric("Medium/Low", medium_low)


def display_alert_settings():
    """
    알람 설정 UI 표시
    
    Returns:
        dict: 설정값
    """
    st.subheader("⚙️ 알람 설정")
    
    with st.expander("감지 임계값 설정", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            zscore_threshold = st.slider(
                "Z-score 임계값",
                min_value=1.0,
                max_value=5.0,
                value=2.5,
                step=0.1,
                help="Z-score가 이 값을 초과하면 스파이크로 감지"
            )
            
            ma_threshold = st.slider(
                "이동평균 대비 변화율 (%)",
                min_value=10,
                max_value=100,
                value=50,
                step=5,
                help="이동평균 대비 변화율이 이 값을 초과하면 감지"
            )
        
        with col2:
            roc_threshold = st.slider(
                "변화율 임계값 (%)",
                min_value=10,
                max_value=100,
                value=30,
                step=5,
                help="단기 변화율이 이 값을 초과하면 감지"
            )
            
            multi_threshold = st.slider(
                "다중 지표 통합 점수",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="통합 스파이크 점수가 이 값을 초과하면 감지"
            )
    
    with st.expander("모니터링 지표 선택", expanded=False):
        monitor_columns = st.multiselect(
            "감시할 지표",
            options=['message_count', 'ETH_close', 'BTC_close', 'tx_frequency', 'avg_sentiment'],
            default=['message_count', 'ETH_close', 'tx_frequency']
        )
    
    with st.expander("알람 조건 설정", expanded=False):
        st.write("**조건 1: 커뮤니티 급증 & 거래량 증가**")
        cond1_enabled = st.checkbox("활성화", value=True, key="cond1")
        
        st.write("**조건 2: 감정 하락 & 가격 하락**")
        cond2_enabled = st.checkbox("활성화", value=True, key="cond2")
        
        st.write("**조건 3: 고래 거래 급증 & 커뮤니티 활동 증가**")
        cond3_enabled = st.checkbox("활성화", value=True, key="cond3")
    
    settings = {
        'zscore_threshold': zscore_threshold,
        'ma_threshold_pct': ma_threshold,
        'roc_threshold_pct': roc_threshold,
        'multi_threshold': multi_threshold,
        'monitor_columns': monitor_columns,
        'conditions': {
            'community_surge_and_volume': cond1_enabled,
            'sentiment_drop_and_price_drop': cond2_enabled,
            'whale_and_community': cond3_enabled
        }
    }
    
    return settings


def display_latest_alerts(alerts_df, n=5):
    """
    최신 알람 N개 표시
    
    Args:
        alerts_df: 알람 데이터프레임
        n: 표시할 개수
    """
    if alerts_df.empty:
        st.info("최근 알람이 없습니다.")
        return
    
    st.subheader(f"📋 최근 {n}개 알람")
    
    latest = alerts_df.head(n)
    
    for idx, row in latest.iterrows():
        display_alert_card(row)


def create_alert_filter_ui():
    """
    알람 필터 UI 생성
    
    Returns:
        dict: 필터 설정
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "기간",
            options=['1시간', '24시간', '7일', '30일', '전체'],
            index=1
        )
    
    with col2:
        alert_levels = st.multiselect(
            "알람 레벨",
            options=['critical', 'high', 'medium', 'low'],
            default=['critical', 'high', 'medium', 'low']
        )
    
    with col3:
        sort_by = st.selectbox(
            "정렬",
            options=['최신순', '중요도순', '크기순'],
            index=0
        )
    
    return {
        'time_range': time_range,
        'alert_levels': alert_levels,
        'sort_by': sort_by
    }

