"""
지표 계산 컴포넌트

다양한 지표와 통계를 계산합니다.
"""

import pandas as pd
import numpy as np
import streamlit as st
import sys
import os

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from styles.coinness_theme import COLORS


def calculate_price_change(df, coin='ETH', period='24h'):
    """
    가격 변화 계산
    
    Args:
        df: 데이터프레임
        coin: 코인 심볼
        period: 기간 ('24h', '7d', '30d')
        
    Returns:
        tuple: (현재 가격, 변화액, 변화율)
    """
    if df.empty or f'{coin}_close' not in df.columns:
        return 0, 0, 0
    
    # 시간 설정
    hours = {
        '1h': 1,
        '24h': 24,
        '7d': 24 * 7,
        '30d': 24 * 30
    }.get(period, 24)
    
    current_price = df[f'{coin}_close'].iloc[-1]
    
    if len(df) > hours:
        past_price = df[f'{coin}_close'].iloc[-hours]
    else:
        past_price = df[f'{coin}_close'].iloc[0]
    
    change = current_price - past_price
    change_pct = (change / past_price) * 100 if past_price > 0 else 0
    
    return current_price, change, change_pct


def calculate_volume_stats(df, coin='ETH', period_hours=24):
    """
    거래량 통계 계산
    
    Args:
        df: 데이터프레임
        coin: 코인 심볼
        period_hours: 집계 기간 (시간)
        
    Returns:
        dict: 거래량 통계
    """
    if df.empty or f'{coin}_volume' not in df.columns:
        return {'total': 0, 'avg': 0, 'max': 0}
    
    recent = df.tail(period_hours)
    
    stats = {
        'total': recent[f'{coin}_volume'].sum(),
        'avg': recent[f'{coin}_volume'].mean(),
        'max': recent[f'{coin}_volume'].max(),
        'min': recent[f'{coin}_volume'].min()
    }
    
    return stats


def calculate_community_stats(df, period_hours=24):
    """
    커뮤니티 활동 통계 계산
    
    Args:
        df: 데이터프레임
        period_hours: 집계 기간
        
    Returns:
        dict: 커뮤니티 통계
    """
    if df.empty or 'message_count' not in df.columns:
        return {
            'total_messages': 0,
            'avg_messages': 0,
            'total_views': 0,
            'avg_sentiment': 0
        }
    
    recent = df.tail(period_hours)
    
    stats = {
        'total_messages': recent['message_count'].sum(),
        'avg_messages': recent['message_count'].mean(),
        'total_views': recent['avg_views'].sum() if 'avg_views' in df.columns else 0,
        'avg_sentiment': recent['avg_sentiment'].mean() if 'avg_sentiment' in df.columns else 0,
        'total_reactions': recent['total_reactions'].sum() if 'total_reactions' in df.columns else 0
    }
    
    return stats


def calculate_whale_activity(df, period_hours=24):
    """
    고래 거래 활동 통계
    
    Args:
        df: 데이터프레임
        period_hours: 집계 기간
        
    Returns:
        dict: 고래 활동 통계
    """
    if df.empty or 'tx_frequency' not in df.columns:
        return {
            'total_tx': 0,
            'avg_tx_frequency': 0,
            'total_amount': 0
        }
    
    recent = df.tail(period_hours)
    
    stats = {
        'total_tx': recent['tx_frequency'].sum(),
        'avg_tx_frequency': recent['tx_frequency'].mean(),
        'total_amount': recent['tx_amount'].sum() if 'tx_amount' in df.columns else 0,
        'max_amount': recent['tx_amount'].max() if 'tx_amount' in df.columns else 0
    }
    
    return stats


def get_correlation_strength(corr_value):
    """
    상관계수 값에 대한 강도 판정
    
    Args:
        corr_value: 상관계수
        
    Returns:
        str: 강도 설명
    """
    abs_corr = abs(corr_value)
    
    if abs_corr >= 0.7:
        strength = "매우 강함"
    elif abs_corr >= 0.5:
        strength = "강함"
    elif abs_corr >= 0.3:
        strength = "중간"
    elif abs_corr >= 0.1:
        strength = "약함"
    else:
        strength = "매우 약함"
    
    direction = "양의" if corr_value > 0 else "음의"
    
    return f"{direction} 상관관계 ({strength})"


def calculate_volatility(df, column, window=24):
    """
    변동성 계산
    
    Args:
        df: 데이터프레임
        column: 계산할 컬럼
        window: 윈도우 크기
        
    Returns:
        float: 변동성 (표준편차)
    """
    if df.empty or column not in df.columns:
        return 0
    
    recent = df.tail(window)
    return recent[column].std()


def get_trend_direction(df, column, window=24):
    """
    트렌드 방향 판정
    
    Args:
        df: 데이터프레임
        column: 판정할 컬럼
        window: 윈도우 크기
        
    Returns:
        str: 트렌드 방향 ('상승', '하락', '횡보')
    """
    if df.empty or column not in df.columns or len(df) < window:
        return "알 수 없음"
    
    recent = df.tail(window)
    
    # 선형 회귀 기울기 계산
    x = np.arange(len(recent))
    y = recent[column].values
    
    # NaN 제거
    mask = ~np.isnan(y)
    if sum(mask) < 2:
        return "알 수 없음"
    
    x = x[mask]
    y = y[mask]
    
    slope = np.polyfit(x, y, 1)[0]
    
    # 변화율 계산
    mean_value = np.mean(y)
    slope_pct = (slope / mean_value) * 100 if mean_value != 0 else 0
    
    if slope_pct > 1:
        return "상승 ↗"
    elif slope_pct < -1:
        return "하락 ↘"
    else:
        return "횡보 →"


def format_large_number(num):
    """
    큰 숫자를 읽기 쉽게 포맷
    
    Args:
        num: 숫자
        
    Returns:
        str: 포맷된 문자열
    """
    if pd.isna(num):
        return "N/A"
    
    if abs(num) >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"


def format_percentage(value, decimals=2):
    """
    퍼센트 포맷
    
    Args:
        value: 값
        decimals: 소수점 자리수
        
    Returns:
        str: 포맷된 문자열
    """
    if pd.isna(value):
        return "N/A"
    
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def get_alert_color(alert_level):
    """
    알람 레벨에 따른 색상 반환
    
    Args:
        alert_level: 알람 레벨
        
    Returns:
        str: 색상 코드
    """
    colors = {
        'low': '#90EE90',      # 연두색
        'medium': '#FFD700',   # 노란색
        'high': '#FF8C00',     # 주황색
        'critical': '#FF0000'  # 빨간색
    }
    
    return colors.get(alert_level, '#808080')


def calculate_performance_metrics(df, coin='ETH'):
    """
    성과 지표 계산
    
    Args:
        df: 데이터프레임
        coin: 코인 심볼
        
    Returns:
        dict: 성과 지표
    """
    if df.empty or f'{coin}_close' not in df.columns:
        return {}
    
    prices = df[f'{coin}_close'].dropna()
    
    if len(prices) == 0:
        return {}
    
    # 수익률
    returns = prices.pct_change().dropna()
    
    metrics = {
        'total_return': ((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100,
        'avg_return': returns.mean() * 100,
        'volatility': returns.std() * 100,
        'sharpe_ratio': (returns.mean() / returns.std()) if returns.std() > 0 else 0,
        'max_price': prices.max(),
        'min_price': prices.min(),
        'current_price': prices.iloc[-1]
    }
    
    return metrics


def create_coinness_metric_card(title, value, delta=None, icon="📊", card_type="neutral"):
    """
    코인니스 스타일 메트릭 카드 생성
    
    Args:
        title: 카드 제목
        value: 메인 값
        delta: 변화량 (선택)
        icon: 아이콘 (선택)
        card_type: 카드 타입 ('success', 'danger', 'neutral', 'info')
        
    Returns:
        str: HTML 마크업
    """
    import streamlit as st
    from styles.coinness_theme import COLORS
    
    # 카드 타입에 따른 색상
    type_colors = {
        'success': f"linear-gradient(135deg, {COLORS['success']} 0%, #00E676 100%)",
        'danger': f"linear-gradient(135deg, {COLORS['danger']} 0%, #FF6E6E 100%)",
        'neutral': f"linear-gradient(135deg, #6C757D 0%, #868E96 100%)",
        'info': f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%)"
    }
    
    bg_gradient = type_colors.get(card_type, type_colors['neutral'])
    
    delta_html = ""
    if delta is not None:
        # delta 값 처리 (숫자 변환 시도)
        try:
            # '%' 기호만 있는 경우 (예: "+5.2%")
            if '%' in str(delta):
                numeric_value = float(str(delta).replace('%', '').replace('+', '').strip())
                delta_color = COLORS['success'] if numeric_value > 0 else COLORS['danger']
            # 숫자만 있는 경우
            elif isinstance(delta, (int, float)):
                delta_color = COLORS['success'] if delta > 0 else COLORS['danger']
            # 그 외 문자열 (예: "감정: 0.00")
            else:
                delta_color = COLORS['text_secondary_light']
        except:
            # 변환 실패 시 기본 색상
            delta_color = COLORS['text_secondary_light']
        
        delta_html = f'''
        <div style="
            font-size: 14px;
            margin-top: 8px;
            padding: 4px 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            display: inline-block;
            color: {delta_color};
        ">
            {delta}
        </div>
        '''
    
    card_html = f'''
    <div style="
        background: {bg_gradient};
        color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: transform 0.25s ease-in-out, box-shadow 0.25s ease-in-out;
        height: 100%;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    "
    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0, 0, 0, 0.12)'"
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.08)'">
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        ">
            <span style="font-size: 24px;">{icon}</span>
            <span style="
                font-size: 14px;
                font-weight: 500;
                opacity: 0.9;
            ">{title}</span>
        </div>
        <div style="
            font-size: 28px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        ">{value}</div>
        {delta_html}
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)


def display_coinness_metrics_row(metrics_list):
    """
    코인니스 스타일 메트릭 카드 행 생성
    
    Args:
        metrics_list: 메트릭 딕셔너리 리스트
                      [{'title': '', 'value': '', 'delta': '', 'icon': '', 'type': ''}, ...]
    """
    import streamlit as st
    
    cols = st.columns(len(metrics_list))
    
    for i, metric in enumerate(metrics_list):
        with cols[i]:
            create_coinness_metric_card(
                title=metric.get('title', ''),
                value=metric.get('value', ''),
                delta=metric.get('delta'),
                icon=metric.get('icon', '📊'),
                card_type=metric.get('type', 'neutral')
            )

