#!/bin/bash

cd /Volumes/T7/class/2025-FALL/big_data

echo "🚀 크립토 시그널 대시보드 시작..."
echo ""
echo "브라우저에서 http://localhost:8501 을 열어주세요"
echo ""

streamlit run app_new.py --server.port=8501 --server.headless=false





