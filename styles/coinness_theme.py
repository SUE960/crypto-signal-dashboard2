"""
코인니스 스타일 테마 정의

코인니스 웹사이트의 디자인 시스템을 참고한 색상, 타이포그래피, 스타일 상수
"""

# 색상 팔레트
COLORS = {
    # Primary Colors (파란색 계열)
    'primary': '#5865F2',
    'primary_hover': '#4752C4',
    'primary_light': '#7289DA',
    
    # Background
    'bg_light': '#FFFFFF',
    'bg_dark': '#1E1E1E',
    'card_bg_light': '#F8F9FA',
    'card_bg_dark': '#2D2D2D',
    
    # Text
    'text_primary_light': '#2C2C2C',
    'text_primary_dark': '#E0E0E0',
    'text_secondary_light': '#6C757D',
    'text_secondary_dark': '#A0A0A0',
    
    # Border
    'border_light': '#E5E7EB',
    'border_dark': '#404040',
    
    # Status Colors
    'success': '#00C853',
    'danger': '#FF5252',
    'warning': '#FFC107',
    'info': '#2196F3',
    
    # Chart Colors
    'chart_up': '#00C853',
    'chart_down': '#FF5252',
    'chart_grid': '#E5E7EB',
    'chart_line_1': '#5865F2',
    'chart_line_2': '#00C853',
    'chart_line_3': '#FFC107',
    'chart_line_4': '#FF5252',
}

# 타이포그래피
TYPOGRAPHY = {
    'font_family': '-apple-system, BlinkMacSystemFont, "Pretendard", "Noto Sans KR", "Segoe UI", sans-serif',
    'font_size_h1': '32px',
    'font_size_h2': '24px',
    'font_size_h3': '20px',
    'font_size_body': '16px',
    'font_size_small': '14px',
    'font_weight_regular': '400',
    'font_weight_medium': '500',
    'font_weight_bold': '700',
}

# 간격
SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '16px',
    'lg': '24px',
    'xl': '32px',
    'xxl': '48px',
}

# Border Radius
RADIUS = {
    'sm': '6px',
    'md': '10px',
    'lg': '12px',
    'xl': '16px',
}

# Shadow
SHADOWS = {
    'sm': '0 1px 3px rgba(0,0,0,0.12)',
    'md': '0 4px 6px rgba(0,0,0,0.1)',
    'lg': '0 10px 20px rgba(0,0,0,0.15)',
    'xl': '0 20px 40px rgba(0,0,0,0.2)',
}

# 코인니스 스타일 전역 CSS
def get_global_css(dark_mode=False):
    """전역 CSS 스타일 반환"""
    
    bg = COLORS['bg_dark'] if dark_mode else COLORS['bg_light']
    card_bg = COLORS['card_bg_dark'] if dark_mode else COLORS['card_bg_light']
    text_primary = COLORS['text_primary_dark'] if dark_mode else COLORS['text_primary_light']
    text_secondary = COLORS['text_secondary_dark'] if dark_mode else COLORS['text_secondary_light']
    border = COLORS['border_dark'] if dark_mode else COLORS['border_light']
    
    return f"""
    <style>
    /* 전역 스타일 */
    .stApp {{
        background-color: {bg};
        font-family: {TYPOGRAPHY['font_family']};
        color: {text_primary};
    }}
    
    /* 카드 스타일 */
    .coinness-card {{
        background-color: {card_bg};
        border-radius: {RADIUS['lg']};
        padding: {SPACING['lg']};
        box-shadow: {SHADOWS['md']};
        border: 1px solid {border};
        transition: all 0.3s ease;
    }}
    
    .coinness-card:hover {{
        box-shadow: {SHADOWS['lg']};
        transform: translateY(-2px);
    }}
    
    /* 메트릭 카드 */
    .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {COLORS['primary_light']}15 100%);
        border-radius: {RADIUS['lg']};
        padding: {SPACING['md']};
        box-shadow: {SHADOWS['sm']};
        border: 1px solid {border};
    }}
    
    /* 버튼 스타일 */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border-radius: {RADIUS['md']};
        border: none;
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: {TYPOGRAPHY['font_weight_medium']};
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['primary_hover']};
        box-shadow: {SHADOWS['md']};
        transform: translateY(-1px);
    }}
    
    /* 헤더 스타일 */
    h1 {{
        font-size: {TYPOGRAPHY['font_size_h1']};
        font-weight: {TYPOGRAPHY['font_weight_bold']};
        color: {text_primary};
        margin-bottom: {SPACING['lg']};
    }}
    
    h2 {{
        font-size: {TYPOGRAPHY['font_size_h2']};
        font-weight: {TYPOGRAPHY['font_weight_bold']};
        color: {text_primary};
        margin-top: {SPACING['xl']};
        margin-bottom: {SPACING['md']};
    }}
    
    h3 {{
        font-size: {TYPOGRAPHY['font_size_h3']};
        font-weight: {TYPOGRAPHY['font_weight_medium']};
        color: {text_primary};
        margin-bottom: {SPACING['sm']};
    }}
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {{
        background-color: {card_bg};
        border-right: 1px solid {border};
    }}
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {{
        border-radius: {RADIUS['md']};
        border: 1px solid {border};
        padding: {SPACING['sm']};
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px {COLORS['primary']}20;
    }}
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY['font_size_h2']};
        font-weight: {TYPOGRAPHY['font_weight_bold']};
    }}
    
    /* 차트 컨테이너 */
    .chart-container {{
        background-color: {card_bg};
        border-radius: {RADIUS['lg']};
        padding: {SPACING['lg']};
        box-shadow: {SHADOWS['md']};
        margin-bottom: {SPACING['lg']};
    }}
    
    /* 알람 카드 */
    .alert-card {{
        border-left: 4px solid {COLORS['primary']};
        background-color: {card_bg};
        border-radius: {RADIUS['md']};
        padding: {SPACING['md']};
        margin-bottom: {SPACING['sm']};
    }}
    
    .alert-card.success {{
        border-left-color: {COLORS['success']};
    }}
    
    .alert-card.danger {{
        border-left-color: {COLORS['danger']};
    }}
    
    .alert-card.warning {{
        border-left-color: {COLORS['warning']};
    }}
    
    /* 스크롤바 커스텀 */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {bg};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['primary']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['primary_hover']};
    }}
    
    /* 티커 스타일 */
    .ticker-container {{
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['primary_hover']} 100%);
        color: white;
        padding: {SPACING['md']};
        border-radius: {RADIUS['lg']};
        margin-bottom: {SPACING['lg']};
        display: flex;
        justify-content: space-around;
        align-items: center;
    }}
    
    .ticker-item {{
        text-align: center;
    }}
    
    .ticker-label {{
        font-size: {TYPOGRAPHY['font_size_small']};
        opacity: 0.8;
    }}
    
    .ticker-value {{
        font-size: {TYPOGRAPHY['font_size_h3']};
        font-weight: {TYPOGRAPHY['font_weight_bold']};
        margin-top: {SPACING['xs']};
    }}
    
    /* 애니메이션 */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-out;
    }}
    
    /* 반응형 */
    @media (max-width: 768px) {{
        h1 {{ font-size: 24px; }}
        h2 {{ font-size: 20px; }}
        h3 {{ font-size: 18px; }}
        
        .coinness-card {{
            padding: {SPACING['md']};
        }}
    }}
    </style>
    """


# 차트 색상 설정
CHART_COLORS = {
    'price_up': COLORS['chart_up'],
    'price_down': COLORS['chart_down'],
    'volume': COLORS['primary'],
    'community': COLORS['chart_line_2'],
    'grid': COLORS['chart_grid'],
}

# Plotly 차트 기본 레이아웃
def get_chart_layout(dark_mode=False):
    """Plotly 차트 기본 레이아웃 반환"""
    bg = COLORS['bg_dark'] if dark_mode else COLORS['bg_light']
    text_color = COLORS['text_primary_dark'] if dark_mode else COLORS['text_primary_light']
    grid_color = COLORS['border_dark'] if dark_mode else COLORS['chart_grid']
    
    return {
        'plot_bgcolor': bg,
        'paper_bgcolor': bg,
        'font': {
            'family': TYPOGRAPHY['font_family'],
            'size': 12,
            'color': text_color
        },
        'xaxis': {
            'gridcolor': grid_color,
            'linecolor': grid_color,
        },
        'yaxis': {
            'gridcolor': grid_color,
            'linecolor': grid_color,
        },
        'hoverlabel': {
            'bgcolor': COLORS['card_bg_light'] if not dark_mode else COLORS['card_bg_dark'],
            'font': {'family': TYPOGRAPHY['font_family'], 'size': 12},
            'bordercolor': grid_color,
        },
        'margin': {'l': 60, 'r': 20, 't': 40, 'b': 60},
    }
