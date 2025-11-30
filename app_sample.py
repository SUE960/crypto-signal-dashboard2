"""
샘플 데이터를 생성하여 테스트하는 버전
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_sample_data():
    """샘플 데이터 생성"""
    dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
    
    df = pd.DataFrame({
        'timestamp': dates,
        'ETH_close': 3000 + np.cumsum(np.random.randn(100) * 10),
        'BTC_close': 40000 + np.cumsum(np.random.randn(100) * 100),
        'message_count': np.random.poisson(10, 100),
        'tx_frequency': np.random.poisson(5, 100)
    })
    
    return df

def main():
    st.title("🚀 CRYPTO SIGNAL DASHBOARD (샘플 데이터)")
    
    df = create_sample_data()
    
    st.success(f"✅ 샘플 데이터 생성: {len(df)}행")
    
    # 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ETH 가격", f"${df['ETH_close'].iloc[-1]:,.2f}", 
                 f"{df['ETH_close'].iloc[-1] - df['ETH_close'].iloc[-2]:+.2f}")
    
    with col2:
        st.metric("BTC 가격", f"${df['BTC_close'].iloc[-1]:,.0f}",
                 f"{df['BTC_close'].iloc[-1] - df['BTC_close'].iloc[-2]:+.0f}")
    
    with col3:
        st.metric("텔레그램", f"{df['message_count'].iloc[-1]:,}",
                 f"{df['message_count'].iloc[-1] - df['message_count'].iloc[-2]:+}")
    
    with col4:
        st.metric("고래 거래", f"{df['tx_frequency'].iloc[-1]:,}",
                 f"{df['tx_frequency'].iloc[-1] - df['tx_frequency'].iloc[-2]:+}")
    
    # 차트
    st.subheader("📈 가격 차트")
    st.line_chart(df.set_index('timestamp')[['ETH_close', 'BTC_close']])
    
    # 데이터
    st.subheader("📊 데이터")
    st.dataframe(df, use_container_width=True)

if __name__ == '__main__':
    main()


