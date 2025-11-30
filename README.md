# Crypto Signal Dashboard

실시간 암호화폐 시장 신호 대시보드 + **다중 소스 Spike 알람 시스템**

## 🚀 Features

- 📊 텔레그램, 뉴스, 트위터 데이터 통합 분석
- 🐋 고래 거래 모니터링
- 📈 실시간 가격 추적
- 🔔 **고급 스파이크 알람 시스템** (텔레그램 + 고래 + 트위터)
- 💡 종합 시장 신호 점수
- 🔍 **상관관계 분석 및 시차 예측**
- 📉 **실시간 모니터링 및 알람**

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Streamlit 대시보드
```bash
streamlit run main.py
```

### 다중 소스 Spike 알람 시스템
```bash
# 전체 분석 실행 (상관관계 + 알람 생성)
python analysis/multi_source_correlation.py

# 시각화 대시보드 생성
python analysis/spike_alert_dashboard.py

# 실시간 모니터링
python analysis/realtime_spike_monitor.py --test    # 테스트 모드
python analysis/realtime_spike_monitor.py            # 실시간 모니터링 (10분)
```

📚 **빠른 시작 가이드**: [QUICK_START.md](QUICK_START.md)  
📊 **상세 분석 리포트**: [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)

## 📁 Project Structure

```
.
├── main.py                 # 메인 애플리케이션
├── requirements.txt        # 의존성 패키지
├── data/                   # 데이터 파일
│   └── processed_data.csv
├── utils/                  # 유틸리티 모듈
│   ├── data_loader.py
│   ├── composite_score.py
│   └── sentiment_analyzer.py
├── analysis/              # 분석 모듈
│   ├── correlation_analysis.py
│   ├── spike_detector.py
│   ├── multi_source_correlation.py      # 다중 소스 상관관계 분석 ⭐
│   ├── spike_alert_dashboard.py         # Spike 알람 시각화 대시보드 ⭐
│   └── realtime_spike_monitor.py        # 실시간 Spike 모니터링 ⭐
├── components/            # UI 컴포넌트
│   ├── charts.py
│   ├── metrics.py
│   ├── filters.py
│   └── alerts.py
├── scripts/              # 데이터 수집 스크립트
│   ├── collect_telegram_data.py
│   ├── collect_coinness_selenium.py
│   └── preprocess_data.py
├── ANALYSIS_REPORT.md        # 다중 소스 분석 상세 리포트 ⭐
└── QUICK_START.md            # Spike 알람 시스템 빠른 시작 가이드 ⭐
```

## 🔥 New: 다중 소스 Spike 알람 시스템

### 주요 기능
1. **통합 데이터 분석**
   - 텔레그램 (12,344 rows)
   - 고래 거래 (241,348 rows)
   - 트위터 인플루언서 (11,426 rows)
   - 시간별 동기화 및 통합 (90,600 rows)

2. **상관관계 분석**
   - 20개의 유의미한 상관관계 발견
   - 시차 상관관계: 텔레그램→고래 (11시간), 트위터→고래 (5시간)
   - 선행 지표로 활용 가능

3. **Spike 알람**
   - 총 4,627개 알람 생성
   - CRITICAL: 29개 (3개 소스 동시 급증 등)
   - HIGH: 11개 (2개 소스 동시 급증)
   - 우선순위 점수 기반 자동 분류

4. **실시간 모니터링**
   - Z-score 기반 이상 감지
   - 알람 쿨다운으로 중복 방지
   - 설정 파일 기반 커스터마이징

5. **시각화**
   - 상관관계 히트맵
   - 시계열 + 스파이크 표시
   - 알람 통계 대시보드
   - 시차 상관관계 플롯

### 빠른 예시

```python
from analysis.multi_source_correlation import MultiSourceCorrelationAnalyzer

# 분석기 초기화
analyzer = MultiSourceCorrelationAnalyzer(
    telegram_path='data/telegram_data.csv',
    whale_path='data/whale_transactions_rows.csv',
    twitter_path='data/twitter_influencer_labeled_rows.csv'
)

# 데이터 병합 및 분석
merged_df = analyzer.merge_all_data(freq='1H')
patterns = analyzer.analyze_cross_source_patterns()
alerts = analyzer.generate_all_alerts(min_priority_score=2)

# 결과 저장
analyzer.save_results()
```

### 주요 발견사항
- **텔레그램 → 고래**: 11시간 시차, r=0.107 (유의미)
- **트위터 → 고래**: 5시간 시차, r=0.061 (유의미)
- **3개 소스 동시 급증**: 2회 (매우 드물지만 중요한 신호)
- **텔레그램+고래 동시 급증**: 29회 (가장 빈번한 Critical 패턴)

📊 자세한 내용은 [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)를 참고하세요.
```

## 🌐 Deployment

Streamlit Cloud로 배포:
1. GitHub 저장소 연결
2. Main file path: `main.py`
3. Python version: 3.11

## 📄 License

MIT
