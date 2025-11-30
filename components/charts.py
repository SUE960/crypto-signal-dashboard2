"""
차트 컴포넌트

Plotly를 사용한 다양한 차트 생성 함수들
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# 상대 import로 변경
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styles.coinness_theme import COLORS


def get_coinness_layout(title="", height=400):
    """
    코인니스 스타일 차트 레이아웃 반환
    
    Args:
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        dict: 레이아웃 설정
    """
    return {
        'title': {
            'text': title,
            'font': {'size': 18, 'family': 'Pretendard, Inter, sans-serif', 'color': COLORS['text_primary_light']},
            'x': 0.02
        },
        'height': height,
        'hovermode': 'x unified',
        'paper_bgcolor': COLORS['bg_light'],
        'plot_bgcolor': COLORS['card_bg_light'],
        'font': {'family': 'Pretendard, Inter, sans-serif', 'color': COLORS['text_primary_light']},
        'xaxis': {
            'gridcolor': COLORS['border_light'],
            'linecolor': COLORS['border_light'],
            'title_font': {'size': 14},
            'tickfont': {'size': 12}
        },
        'yaxis': {
            'gridcolor': COLORS['border_light'],
            'linecolor': COLORS['border_light'],
            'title_font': {'size': 14},
            'tickfont': {'size': 12}
        },
        'legend': {
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': COLORS['border_light'],
            'borderwidth': 1,
            'font': {'size': 12}
        },
        'margin': {'l': 60, 'r': 20, 't': 60, 'b': 60}
    }


def get_chart_colors():
    """
    코인니스 차트 색상 팔레트 반환
    
    Returns:
        list: 색상 리스트
    """
    return [
        COLORS['chart_line_1'],  # 파란색
        COLORS['chart_line_2'],  # 초록색
        COLORS['chart_line_3'],  # 노란색
        COLORS['chart_line_4'],  # 빨간색
        COLORS['primary_light'],  # 연한 파란색
    ]


def create_time_series_chart(df, columns, title="Time Series", height=400):
    """
    시계열 차트 생성 (코인니스 스타일)
    
    Args:
        df: 데이터프레임
        columns: 표시할 컬럼 리스트 또는 단일 컬럼
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if isinstance(columns, str):
        columns = [columns]
    
    colors = get_chart_colors()
    
    for i, col in enumerate(columns):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df[col],
                mode='lines',
                name=col,
                line=dict(
                    color=colors[i % len(colors)],
                    width=2.5
                ),
                fill='tonexty' if i > 0 else None,
                fillcolor=f'rgba{tuple(list(int(colors[i % len(colors)][j:j+2], 16) for j in (1, 3, 5)) + [0.1])}',
                hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>'
            ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = "값"
    
    fig.update_layout(**layout)
    
    return fig


def create_multi_axis_chart(df, left_col, right_col, title="Dual Axis Chart", height=400):
    """
    이중 축 차트 생성 (코인니스 스타일)
    
    Args:
        df: 데이터프레임
        left_col: 왼쪽 축 컬럼
        right_col: 오른쪽 축 컬럼
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 왼쪽 축 (코인니스 파란색)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df[left_col],
            mode='lines',
            name=left_col,
            line=dict(color=COLORS['primary'], width=2.5),
            fill='tozeroy',
            fillcolor=f'rgba(88, 101, 242, 0.1)'
        ),
        secondary_y=False
    )
    
    # 오른쪽 축 (코인니스 초록색)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df[right_col],
            mode='lines',
            name=right_col,
            line=dict(color=COLORS['success'], width=2.5)
        ),
        secondary_y=True
    )
    
    layout = get_coinness_layout(title, height)
    fig.update_layout(**layout)
    
    fig.update_xaxes(
        title_text="시간",
        gridcolor=COLORS['border'],
        linecolor=COLORS['border']
    )
    fig.update_yaxes(
        title_text=left_col,
        gridcolor=COLORS['border'],
        linecolor=COLORS['border'],
        secondary_y=False
    )
    fig.update_yaxes(
        title_text=right_col,
        gridcolor=COLORS['border'],
        linecolor=COLORS['border'],
        secondary_y=True
    )
    
    return fig


def create_correlation_heatmap(corr_matrix, title="Correlation Heatmap", height=600):
    """
    상관관계 히트맵 생성 (코인니스 스타일)
    
    Args:
        corr_matrix: 상관계수 행렬
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    # 코인니스 스타일 색상 팔레트 (파란색-흰색-빨간색)
    colorscale = [
        [0.0, COLORS['danger']],
        [0.25, '#FFB3B3'],
        [0.5, '#FFFFFF'],
        [0.75, '#B3C7FF'],
        [1.0, COLORS['primary']]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale=colorscale,
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10, "color": COLORS['text_primary']},
        colorbar=dict(
            title="상관계수",
            titlefont={'size': 12},
            tickfont={'size': 10}
        )
    ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis']['side'] = 'bottom'
    
    fig.update_layout(**layout)
    
    return fig


def create_lag_correlation_chart(lag_corr_df, title="Lag Correlation", height=400):
    """
    시차 상관관계 차트 생성
    
    Args:
        lag_corr_df: 시차 상관관계 데이터프레임 (lag, correlation, p_value 컬럼)
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # 상관계수
    fig.add_trace(go.Bar(
        x=lag_corr_df['lag'],
        y=lag_corr_df['correlation'],
        name='Correlation',
        marker_color=['green' if sig else 'lightgray' 
                     for sig in lag_corr_df['significant']],
        hovertemplate='Lag: %{x}h<br>Correlation: %{y:.3f}<extra></extra>'
    ))
    
    # 유의수준 선
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title=title,
        xaxis_title="Lag (hours)",
        yaxis_title="Correlation Coefficient",
        height=height,
        template='plotly_white'
    )
    
    return fig


def create_spike_timeline(spike_df, title="Spike Timeline", height=400):
    """
    스파이크 타임라인 차트 생성
    
    Args:
        spike_df: 스파이크 데이터프레임
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    if spike_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="스파이크가 감지되지 않았습니다",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=height, template='plotly_white')
        return fig
    
    # 스파이크 타입별 색상 (코인니스 스타일)
    color_map = {
        'positive_spike': COLORS['danger'],
        'negative_spike': COLORS['primary'],
        'surge': COLORS['warning'],
        'drop': COLORS['info'],
        'rapid_increase': COLORS['success'],
        'rapid_decrease': COLORS['danger'],
        'multi_indicator': COLORS['warning'],
        'correlated_spike': COLORS['primary_light']
    }
    
    fig = go.Figure()
    
    # 스파이크 포인트
    for spike_type in spike_df['spike_type'].unique():
        type_data = spike_df[spike_df['spike_type'] == spike_type]
        
        fig.add_trace(go.Scatter(
            x=type_data['timestamp'],
            y=type_data['spike_magnitude'],
            mode='markers',
            name=spike_type,
            marker=dict(
                size=10,
                color=color_map.get(spike_type, 'gray'),
                line=dict(width=1, color='white')
            ),
            hovertemplate='%{x}<br>Magnitude: %{y:.2f}<extra></extra>'
        ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = "스파이크 강도 (σ)"
    layout['hovermode'] = 'closest'
    layout['showlegend'] = True
    
    fig.update_layout(**layout)
    
    return fig


def create_candlestick_chart(df, coin='ETH', title=None, height=400):
    """
    캔들스틱 차트 생성
    
    Args:
        df: 데이터프레임
        coin: 코인 심볼 ('ETH' 또는 'BTC')
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    if title is None:
        title = f"{coin} Price Candlestick"
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df[f'{coin}_open'],
        high=df[f'{coin}_high'],
        low=df[f'{coin}_low'],
        close=df[f'{coin}_close'],
        name=coin,
        increasing=dict(line=dict(color=COLORS['success']), fillcolor=COLORS['success']),
        decreasing=dict(line=dict(color=COLORS['danger']), fillcolor=COLORS['danger'])
    )])
    
    # 볼린저 밴드 추가 (있으면)
    if f'{coin}_bb_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df[f'{coin}_bb_upper'],
            mode='lines',
            name='BB Upper',
            line=dict(color='rgba(250, 128, 114, 0.5)', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df[f'{coin}_bb_lower'],
            mode='lines',
            name='BB Lower',
            line=dict(color='rgba(135, 206, 250, 0.5)', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(200, 200, 200, 0.2)'
        ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = f"{coin} 가격 (USD)"
    layout['xaxis_rangeslider_visible'] = False
    
    fig.update_layout(**layout)
    
    return fig


def create_scatter_matrix(df, columns, title="Scatter Matrix", height=800):
    """
    산점도 매트릭스 생성
    
    Args:
        df: 데이터프레임
        columns: 표시할 컬럼 리스트
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    # 데이터 샘플링 (너무 많으면 느림)
    if len(df) > 1000:
        plot_df = df.sample(n=1000, random_state=42)
    else:
        plot_df = df
    
    fig = px.scatter_matrix(
        plot_df,
        dimensions=columns,
        title=title,
        height=height
    )
    
    fig.update_traces(diagonal_visible=False, showupperhalf=False)
    fig.update_layout(template='plotly_white')
    
    return fig


def create_volume_chart(df, coin='ETH', title=None, height=300):
    """
    거래량 차트 생성 (코인니스 스타일)
    
    Args:
        df: 데이터프레임
        coin: 코인 심볼
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    if title is None:
        title = f"{coin} 거래량"
    
    fig = go.Figure()
    
    # 가격 상승/하락에 따른 색상 변경
    colors = []
    for i in range(len(df)):
        if i == 0:
            colors.append(COLORS['chart_neutral'])
        else:
            if df[f'{coin}_close'].iloc[i] >= df[f'{coin}_close'].iloc[i-1]:
                colors.append(COLORS['success'])
            else:
                colors.append(COLORS['danger'])
    
    fig.add_trace(go.Bar(
        x=df['timestamp'],
        y=df[f'{coin}_volume'],
        name='거래량',
        marker=dict(
            color=colors,
            opacity=0.7,
            line=dict(width=0)
        ),
        hovertemplate='%{x}<br>거래량: %{y:,.0f}<extra></extra>'
    ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = f"거래량 ({coin})"
    layout['bargap'] = 0.1
    
    fig.update_layout(**layout)
    
    return fig


def create_sentiment_chart(df, title="Community Sentiment", height=400):
    """
    감정 분석 차트 생성
    
    Args:
        df: 데이터프레임
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    if 'avg_sentiment' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="감정 데이터가 없습니다",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=height, template='plotly_white')
        return fig
    
    fig = go.Figure()
    
    # 감정 점수 (코인니스 스타일 - 파란색)
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['avg_sentiment'],
        mode='lines',
        name='감정 점수',
        line=dict(color=COLORS['primary'], width=2.5),
        fill='tozeroy',
        fillcolor='rgba(88, 101, 242, 0.15)',
        hovertemplate='%{x}<br>감정: %{y:.3f}<extra></extra>'
    ))
    
    # 중립선
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS['border'],
        line_width=1,
        annotation_text="중립"
    )
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = "감정 점수"
    layout['yaxis']['range'] = [-1, 1]
    
    fig.update_layout(**layout)
    
    return fig


def create_comparison_chart(df, columns, normalize=True, title="Comparison", height=400):
    """
    여러 변수 비교 차트 (정규화 옵션, 코인니스 스타일)
    
    Args:
        df: 데이터프레임
        columns: 비교할 컬럼 리스트
        normalize: 정규화 여부
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    colors = get_chart_colors()
    
    for i, col in enumerate(columns):
        if col in df.columns:
            if normalize:
                # Min-Max 정규화 (0~1)
                values = df[col].values
                normalized = (values - np.nanmin(values)) / (np.nanmax(values) - np.nanmin(values) + 1e-10)
                y_data = normalized
            else:
                y_data = df[col]
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=y_data,
                mode='lines',
                name=col,
                line=dict(
                    color=colors[i % len(colors)],
                    width=2.5
                ),
                hovertemplate='%{x}<br>%{y:.3f}<extra></extra>'
            ))
    
    layout = get_coinness_layout(title, height)
    layout['xaxis_title'] = "시간"
    layout['yaxis_title'] = "정규화된 값 (0-1)" if normalize else "값"
    
    fig.update_layout(**layout)
    
    return fig


def create_triple_axis_chart(df, title="통합 분석: 가격 vs 고래 거래 vs 텔레그램 활동", height=600):
    """
    3-in-1 통합 차트 생성: 가격, 고래 거래, 텔레그램을 하나의 차트에 표시
    
    Args:
        df: 데이터프레임 (timestamp, ETH_close, tx_frequency, message_count 필요)
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        Plotly Figure with 3 Y-axes
    """
    from plotly.subplots import make_subplots
    
    # 서브플롯 생성 (3개의 Y축)
    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )
    
    # 1. ETH 가격 (왼쪽 Y축, 파란색)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['ETH_close'],
            name='ETH 가격',
            line=dict(color=COLORS['chart_line_1'], width=2.5),
            yaxis='y',
            hovertemplate='<b>ETH 가격</b><br>$%{y:,.2f}<extra></extra>'
        )
    )
    
    # 2. 고래 거래 빈도 (오른쪽 Y축, 빨간색)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['tx_frequency'],
            name='고래 거래',
            line=dict(color=COLORS['chart_line_4'], width=2),
            yaxis='y2',
            hovertemplate='<b>고래 거래</b><br>%{y:.0f} 건<extra></extra>'
        )
    )
    
    # 3. 텔레그램 메시지 수 (세 번째 Y축, 초록색)
    if 'message_count' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['message_count'],
                name='텔레그램 메시지',
                line=dict(color=COLORS['chart_line_2'], width=2),
                yaxis='y3',
                hovertemplate='<b>텔레그램</b><br>%{y:.0f} 건<extra></extra>'
            )
        )
    
    # 레이아웃 설정
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 20, 'family': 'Pretendard, Inter, sans-serif', 'color': COLORS['text_primary_light']},
            'x': 0.02,
            'y': 0.98
        },
        height=height,
        hovermode='x unified',
        paper_bgcolor=COLORS['bg_light'],
        plot_bgcolor=COLORS['card_bg_light'],
        font={'family': 'Pretendard, Inter, sans-serif', 'color': COLORS['text_primary_light']},
        xaxis=dict(
            title='시간',
            gridcolor=COLORS['border_light'],
            linecolor=COLORS['border_light'],
            title_font={'size': 14},
            tickfont={'size': 12}
        ),
        yaxis=dict(
            title=dict(
                text='<b style="color:#1E88E5;">ETH 가격 ($)</b>',
                font=dict(size=14, color=COLORS['chart_line_1'])
            ),
            side='left',
            gridcolor=COLORS['border_light'],
            linecolor=COLORS['chart_line_1'],
            tickfont=dict(color=COLORS['chart_line_1'], size=11),
            showgrid=True
        ),
        yaxis2=dict(
            title=dict(
                text='<b style="color:#E53935;">고래 거래 (건)</b>',
                font=dict(size=14, color=COLORS['chart_line_4'])
            ),
            side='right',
            overlaying='y',
            gridcolor='rgba(0,0,0,0)',
            linecolor=COLORS['chart_line_4'],
            tickfont=dict(color=COLORS['chart_line_4'], size=11),
            showgrid=False,
            anchor='x'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor=COLORS['border_light'],
            borderwidth=1,
            font={'size': 12}
        ),
        margin={'l': 70, 'r': 70, 't': 100, 'b': 60}
    )
    
    # 세 번째 Y축 (텔레그램)을 오른쪽에 추가
    if 'message_count' in df.columns:
        fig.update_layout(
            yaxis3=dict(
                title=dict(
                    text='<b style="color:#43A047;">텔레그램 (건)</b>',
                    font=dict(size=14, color=COLORS['chart_line_2'])
                ),
                side='right',
                overlaying='y',
                gridcolor='rgba(0,0,0,0)',
                linecolor=COLORS['chart_line_2'],
                tickfont=dict(color=COLORS['chart_line_2'], size=11),
                showgrid=False,
                anchor='free',
                position=0.98
            )
        )
    
    return fig

