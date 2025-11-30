"""
필터 UI 컴포넌트

데이터 필터링을 위한 Streamlit 위젯들
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from styles.coinness_theme import COLORS


def date_range_filter(df, key_prefix=""):
    """
    날짜 범위 필터
    
    Args:
        df: 데이터프레임
        key_prefix: 위젯 키 접두사
        
    Returns:
        tuple: (시작일, 종료일)
    """
    if df.empty or 'timestamp' not in df.columns:
        return None, None
    
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "시작일",
            value=max_date - timedelta(days=7),
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "종료일",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_end_date"
        )
    
    return start_date, end_date


def column_selector(df, label="변수 선택", default_columns=None, key_prefix=""):
    """
    컬럼 선택 필터
    
    Args:
        df: 데이터프레임
        label: 라벨
        default_columns: 기본 선택 컬럼
        key_prefix: 위젯 키 접두사
        
    Returns:
        list: 선택된 컬럼 리스트
    """
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # timestamp 관련 컬럼 제외
    numeric_columns = [c for c in numeric_columns 
                      if c not in ['hour', 'day_of_week', 'day', 'month']]
    
    if default_columns is None:
        default_columns = numeric_columns[:5] if len(numeric_columns) >= 5 else numeric_columns
    
    selected = st.multiselect(
        label,
        options=numeric_columns,
        default=default_columns,
        key=f"{key_prefix}_columns"
    )
    
    return selected


def threshold_slider(label="임계값", min_value=0.0, max_value=5.0, default_value=2.5, 
                     step=0.1, key_prefix=""):
    """
    임계값 슬라이더
    
    Args:
        label: 라벨
        min_value: 최소값
        max_value: 최대값
        default_value: 기본값
        step: 스텝
        key_prefix: 위젯 키 접두사
        
    Returns:
        float: 선택된 값
    """
    value = st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        step=step,
        key=f"{key_prefix}_threshold"
    )
    
    return value


def period_selector(label="기간 선택", options=None, default_index=0, key_prefix=""):
    """
    기간 선택 라디오 버튼
    
    Args:
        label: 라벨
        options: 옵션 리스트
        default_index: 기본 인덱스
        key_prefix: 위젯 키 접두사
        
    Returns:
        str: 선택된 기간
    """
    if options is None:
        options = ['1시간', '24시간', '7일', '30일', '전체']
    
    period = st.radio(
        label,
        options=options,
        index=default_index,
        horizontal=True,
        key=f"{key_prefix}_period"
    )
    
    return period


def coin_selector(label="코인 선택", default="ETH", key_prefix=""):
    """
    코인 선택 셀렉트박스
    
    Args:
        label: 라벨
        default: 기본값
        key_prefix: 위젯 키 접두사
        
    Returns:
        str: 선택된 코인
    """
    coins = ['ETH', 'BTC']
    
    coin = st.selectbox(
        label,
        options=coins,
        index=coins.index(default) if default in coins else 0,
        key=f"{key_prefix}_coin"
    )
    
    return coin


def alert_level_filter(label="알람 레벨", key_prefix=""):
    """
    알람 레벨 필터
    
    Args:
        label: 라벨
        key_prefix: 위젯 키 접두사
        
    Returns:
        list: 선택된 레벨 리스트
    """
    levels = ['low', 'medium', 'high', 'critical']
    
    selected = st.multiselect(
        label,
        options=levels,
        default=levels,
        key=f"{key_prefix}_alert_level"
    )
    
    return selected


def apply_date_filter(df, start_date, end_date):
    """
    데이터프레임에 날짜 필터 적용
    
    Args:
        df: 데이터프레임
        start_date: 시작일
        end_date: 종료일
        
    Returns:
        DataFrame: 필터된 데이터프레임
    """
    if df.empty or 'timestamp' not in df.columns:
        return df
    
    if start_date is None or end_date is None:
        return df
    
    # date를 datetime으로 변환
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)
    
    filtered = df[(df['timestamp'] >= start_datetime) & (df['timestamp'] <= end_datetime)]
    
    return filtered


def convert_period_to_hours(period_str):
    """
    기간 문자열을 시간으로 변환
    
    Args:
        period_str: 기간 문자열 ('1시간', '24시간', '7일' 등)
        
    Returns:
        int: 시간 수 (None은 전체)
    """
    mapping = {
        '1시간': 1,
        '24시간': 24,
        '7일': 24 * 7,
        '30일': 24 * 30,
        '전체': None
    }
    
    return mapping.get(period_str, 24)

