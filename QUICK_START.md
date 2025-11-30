# 🚀 다중 소스 Spike 알람 시스템 - 빠른 시작 가이드

## 📌 핵심 요약

텔레그램, 고래 거래, 트위터 인플루언서 데이터를 통합하여 암호화폐 시장의 **이상 징후(Spike)**를 실시간으로 감지하는 시스템입니다.

### 🎯 주요 발견사항

1. **텔레그램 → 고래 거래**: 약 **11시간** 시차 상관관계 (r=0.107)
2. **트위터 → 고래 거래**: 약 **5시간** 시차 상관관계 (r=0.061)
3. **Total Alerts**: 4,627개 중 **CRITICAL 29개** (0.6%)
4. **3개 소스 동시 급증**: 매우 드물지만 발생 시 시장 전환점 신호 (2회 발생)

---

## ⚡ 빠른 실행

### 1. 전체 분석 실행
```bash
# 상관관계 분석 + 알람 생성
python analysis/multi_source_correlation.py

# 시각화 생성
python analysis/spike_alert_dashboard.py
```

### 2. 실시간 모니터링
```bash
# 테스트 모드 (한 번만 체크)
python analysis/realtime_spike_monitor.py --test

# 실시간 모니터링 (10분)
python analysis/realtime_spike_monitor.py
```

---

## 📊 생성되는 주요 파일

### 분석 결과
- `data/multi_source_merged_data.csv` - 통합 데이터 (90,600 rows)
- `data/multi_source_alerts.csv` - 전체 알람 (4,627개)
- `data/multi_source_significant_correlations.csv` - 유의미한 상관관계 (20개)

### 시각화
- `data/visualizations/correlation_heatmap.png` - 상관관계 히트맵
- `data/visualizations/time_series_with_spikes.png` - 시계열 + 스파이크
- `data/visualizations/alert_statistics.png` - 알람 통계
- `data/visualizations/lag_correlation_*.png` - 시차 상관관계

---

## 🚨 알람 레벨

| 레벨 | 우선순위 | 조건 | 개수 |
|------|----------|------|------|
| **CRITICAL** | ≥10 | 3개 소스 동시 급증 또는 2개 이상 + 고래 | 29 |
| **HIGH** | 5-9 | 2개 소스 동시 급증 (고래 포함) | 11 |
| **MEDIUM** | 2-4 | 단일 소스 스파이크 | 4,587 |

---

## 🔥 Top Critical 알람

### 1. 2025-10-20 22:00 (우선순위: 26) ⭐
- 🚨 **3개 소스 모두 급증**
- 텔레그램: z=2.48, 고래: z=4.69, 트위터: z=2.87
- 고래 거래: **1,726 txs** (매우 높음)

### 2. 2025-01-01 17:00 (우선순위: 26)
- 🚨 **3개 소스 모두 급증** (신년 효과)
- 트위터 인게이지먼트: **11,204** (높음)

---

## 💡 활용 방법

### 거래 전략
1. **진입**: 텔레그램/트위터 급증 → 시차(5-11h) 대기 후 진입
2. **경고**: CRITICAL 알람 → 포지션 재검토
3. **청산**: 3개 소스 동시 급증 → 이익 실현 고려

### 리스크 관리
- HIGH 이상 알람 → 포지션 사이즈 축소
- 고래 거래 급증 → 변동성 확대 대비
- 알람 쿨다운으로 과도한 반응 방지

---

## 📂 프로젝트 구조

```
big_data/
├── analysis/
│   ├── multi_source_correlation.py    # 상관관계 분석
│   ├── spike_alert_dashboard.py       # 시각화 대시보드
│   └── realtime_spike_monitor.py      # 실시간 모니터
├── data/
│   ├── telegram_data.csv              # 텔레그램 데이터
│   ├── whale_transactions_rows.csv    # 고래 거래 데이터
│   ├── twitter_influencer_labeled_rows.csv  # 트위터 데이터
│   ├── multi_source_*.csv             # 분석 결과
│   └── visualizations/                # 시각화 파일
├── ANALYSIS_REPORT.md                 # 상세 분석 리포트
└── QUICK_START.md                     # 이 파일
```

---

## 🔧 설정 파일

**파일**: `data/monitor_config.json`

```json
{
  "spike_threshold": 2.0,              // 스파이크 Z-score 임계값
  "window_hours": 24,                  // 이동평균 윈도우 (시간)
  "check_interval_seconds": 60,        // 체크 간격 (초)
  "alert_cooldown_hours": 1,           // 알람 쿨다운 (시간)
  "critical_priority_threshold": 10    // CRITICAL 최소 점수
}
```

---

## 📈 주요 상관관계

| 변수 1 | 변수 2 | 상관계수 | 의미 |
|--------|--------|----------|------|
| whale_volume_sum | whale_volume_max | **0.998** | 거래량 합계와 최대값 거의 완벽한 상관 |
| twitter_likes | twitter_engagement | **0.988** | 좋아요가 인게이지먼트 주도 |
| telegram_positive | telegram_neutral | **-0.778** | 긍정/중립 감정의 반비례 |

---

## 🎓 상세 문서

더 자세한 내용은 다음 문서를 참고하세요:
- **[ANALYSIS_REPORT.md](ANALYSIS_REPORT.md)** - 완전한 분석 리포트
- **[data/visualizations/alert_report.txt](data/visualizations/alert_report.txt)** - 알람 상세 리포트

---

## ⚙️ 의존성

주요 라이브러리:
- pandas >= 1.5.0
- numpy >= 1.23.0
- scipy >= 1.9.0
- matplotlib >= 3.6.0
- seaborn >= 0.12.0

설치:
```bash
pip install -r requirements.txt
```

---

## 🐛 문제 해결

### 데이터 로딩 오류
- 타임스탬프 형식 불일치 → `errors='coerce'`로 자동 처리됨
- 타임존 문제 → 자동으로 UTC로 통일 후 제거

### 메모리 부족
- 대용량 데이터 (90,600 rows) → 필요 시 샘플링 사용
- 시각화 시 최근 N일만 표시 (`recent_days` 파라미터)

---

## 🚀 향후 계획

1. ✅ 다중 소스 통합 분석
2. ✅ Spike 알람 시스템
3. ✅ 시각화 대시보드
4. ⏳ 실시간 데이터 수집 (API)
5. ⏳ 머신러닝 예측 모델
6. ⏳ 웹 대시보드 (Streamlit)
7. ⏳ 슬랙/텔레그램 봇 연동

---

## 📞 문의

질문이나 제안이 있으시면 이슈를 등록해주세요!

**Happy Trading! 📊💰**


