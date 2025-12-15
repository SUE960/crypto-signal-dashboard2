"""
간단한 테스트용 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

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
    
    .signal-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
    }
    
    .score-big {
        font-size: 48px;
        font-weight: bold;
        color: #00d4ff;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🚀 CRYPTO SIGNAL DASHBOARD")
    st.markdown("---")
    
    # 데이터 로드 테스트
    st.subheader("📁 데이터 로드 상태")
    
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'processed_data.csv')
    st.write(f"데이터 경로: `{data_path}`")
    
    if os.path.exists(data_path):
        st.success("✅ 파일 존재")
        
        try:
            df = pd.read_csv(data_path)
            st.success(f"✅ 데이터 로드 성공: {len(df):,}행")
            
            # 데이터 미리보기
            st.subheader("📊 데이터 미리보기")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 컬럼 정보
            st.subheader("🔍 컬럼 정보")
            st.write(f"총 {len(df.columns)}개 컬럼:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**시간 관련:**")
                time_cols = [c for c in df.columns if 'timestamp' in c.lower() or 'date' in c.lower()]
                st.write(time_cols if time_cols else "없음")
            
            with col2:
                st.write("**가격 관련:**")
                price_cols = [c for c in df.columns if 'ETH' in c or 'BTC' in c or 'price' in c.lower()]
                st.write(price_cols[:5] if price_cols else "없음")
            
            with col3:
                st.write("**활동 관련:**")
                activity_cols = [c for c in df.columns if 'message' in c.lower() or 'tx' in c.lower()]
                st.write(activity_cols if activity_cols else "없음")
            
            # 간단한 차트
            if 'timestamp' in df.columns and 'ETH_close' in df.columns:
                st.subheader("📈 ETH 가격 차트")
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['ETH_close'],
                    mode='lines',
                    name='ETH Price',
                    line=dict(color='#00d4ff', width=2)
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#0a0a0a',
                    plot_bgcolor='#1a1a1a',
                    height=400,
                    xaxis_title="Time",
                    yaxis_title="Price (USD)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # 통계
            st.subheader("📊 기본 통계")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="signal-card">
                    <div style="font-size: 14px; color: #888;">ETH 현재가</div>
                    <div class="score-big">${:,.2f}</div>
                </div>
                """.format(df['ETH_close'].iloc[-1] if 'ETH_close' in df.columns else 0), 
                unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="signal-card">
                    <div style="font-size: 14px; color: #888;">BTC 현재가</div>
                    <div class="score-big">${:,.0f}</div>
                </div>
                """.format(df['BTC_close'].iloc[-1] if 'BTC_close' in df.columns else 0), 
                unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="signal-card">
                    <div style="font-size: 14px; color: #888;">텔레그램 메시지</div>
                    <div class="score-big">{:,.0f}</div>
                </div>
                """.format(df['message_count'].sum() if 'message_count' in df.columns else 0), 
                unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="signal-card">
                    <div style="font-size: 14px; color: #888;">고래 거래</div>
                    <div class="score-big">{:,.0f}</div>
                </div>
                """.format(df['tx_frequency'].sum() if 'tx_frequency' in df.columns else 0), 
                unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ 데이터 로드 실패: {e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.error("❌ 파일이 존재하지 않습니다!")
        st.info(f"다음 경로를 확인해주세요: {data_path}")

if __name__ == '__main__':
    main()








