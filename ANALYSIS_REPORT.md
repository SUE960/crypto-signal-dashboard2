# 다중 소스 Spike 알람 시스템 분석 결과

## 📊 개요

텔레그램, 고래 거래, 트위터 인플루언서 데이터를 통합하여 암호화폐 시장의 이상 징후(Spike)를 실시간으로 감지하고 알람을 생성하는 시스템입니다.

**분석 날짜**: 2025년 11월 30일

---

## 🗂️ 데이터 소스

### 1. 텔레그램 데이터
- **파일**: `telegram_data.csv`
- **행 수**: 12,344 rows
- **시간 범위**: 2025-01-01 ~ 2025-11-29
- **주요 지표**:
  - 메시지 수 (message_count)
  - 평균 조회수 (avg_views)
  - 포워드 수 (total_forwards)
  - 리액션 수 (total_reactions)
  - 감정 점수 (avg_sentiment)

### 2. 고래 거래 데이터
- **파일**: `whale_transactions_rows.csv`
- **행 수**: 241,348 rows (유효한 타임스탬프)
- **시간 범위**: 2015-07-31 ~ 2025-11-29
- **주요 지표**:
  - 거래 빈도 (tx_count)
  - 거래량 합계 (volume_sum)
  - 거래량 평균 (volume_mean)
  - 거래량 최대값 (volume_max)

### 3. 트위터 인플루언서 데이터
- **파일**: `twitter_influencer_labeled_rows.csv`
- **행 수**: 11,426 rows (유효한 타임스탬프)
- **시간 범위**: 2024-12-08 ~ 2025-11-29
- **주요 지표**:
  - 포스트 수 (post_count)
  - 좋아요 (likes)
  - 공유 (shares)
  - 댓글 (comments)
  - 인게이지먼트 점수 (engagement)

---

## 📈 주요 분석 결과

### 1. 상관관계 분석

**20개의 유의미한 상관관계 발견** (p < 0.05)

#### 강한 양의 상관관계 (r > 0.8)
1. `whale_volume_sum` ↔ `whale_volume_max`: **r = 0.998** ⭐
   - 고래 거래량 합계와 최대값은 거의 완벽한 양의 상관관계
   
2. `twitter_likes` ↔ `twitter_engagement`: **r = 0.988**
   - 트위터 좋아요와 전체 인게이지먼트의 강한 연관성
   
3. `twitter_shares` ↔ `twitter_engagement`: **r = 0.931**
   - 공유 수가 인게이지먼트의 주요 요소

4. `whale_volume_mean` ↔ `whale_volume_max`: **r = 0.891**
   - 평균 거래량과 최대 거래량의 높은 상관관계

#### 중간 상관관계 (0.3 < r < 0.8)
- `telegram_avg_positive` ↔ `telegram_avg_neutral`: **r = -0.778**
  - 긍정적 감정과 중립적 감정의 음의 상관관계 (당연한 결과)

- `telegram_avg_sentiment` ↔ `telegram_avg_positive`: **r = 0.637**
  - 전체 감정 점수는 긍정적 감정에 크게 영향받음

#### 소스 간 교차 상관관계
- `twitter_post_count` ↔ `twitter_coin_mentions`: **r = 0.388**
  - 트위터 포스트 증가 시 코인 언급도 증가

### 2. 시차 상관관계 분석 (Lag Correlation)

#### 텔레그램 → 고래 거래
- **최대 상관관계**: lag = **11시간**, r = 0.107
- 텔레그램 활동 증가 후 약 11시간 뒤 고래 거래 증가 경향
- 통계적으로 유의미 (p < 0.0001)

#### 트위터 → 고래 거래
- **최대 상관관계**: lag = **5시간**, r = 0.061
- 트위터 인플루언서 활동 후 약 5시간 뒤 고래 거래 반응
- 통계적으로 유의미 (p < 0.0001)

**해석**: 
- 텔레그램이 트위터보다 고래 거래에 더 긴 시차를 가짐
- 트위터는 더 빠른 반응 속도 (5시간 vs 11시간)
- 둘 다 선행 지표로 활용 가능

---

## 🚨 Spike 알람 분석

### 알람 통계
- **총 알람 수**: 4,627개
- **분석 기간**: 2015-07-31 ~ 2025-11-29 (약 10년)

#### 레벨별 분포
| 레벨 | 개수 | 비율 |
|------|------|------|
| **CRITICAL** | 29 | 0.6% |
| **HIGH** | 11 | 0.2% |
| **MEDIUM** | 4,587 | 99.1% |

### Critical 알람 이벤트 (Top 10)

#### 1. 2025-10-20 22:00:00 (우선순위: 26)
- **사유**: 
  - 텔레그램 메시지 급증 (z=2.48)
  - 고래 거래 급증 (z=4.69) ⭐
  - 트위터 인플루언서 활동 급증 (z=2.87)
  - ⚠️ 텔레그램+고래 동시 급증
  - ⚠️ 트위터+고래 동시 급증
  - 🚨 **3개 소스 모두 급증 (CRITICAL)**
- **데이터**: 
  - 텔레그램: 메시지 수 급증
  - 고래 거래: 매우 높은 거래 빈도
  - 트위터: 높은 인게이지먼트

#### 2. 2025-01-01 17:00:00 (우선순위: 26)
- **사유**: 3개 소스 모두 급증 (신년 효과 추정)
- z-scores: 텔레그램 2.40, 고래 2.02, 트위터 3.47

#### 3-10. 2025년 9월~10월 집중 발생
- 대부분 텔레그램+고래 동시 급증 패턴
- 가을철 시장 활성화 시기와 일치

### 동시 급증 패턴 분석

#### 3개 소스 동시 급증
- **발생 횟수**: 2회
- **날짜**: 2025-01-01, 2025-10-20
- **특징**: 매우 드물지만 발생 시 시장 변동성 극대화 가능성

#### 텔레그램 + 고래 동시 급증
- **발생 횟수**: 29회
- **날짜 범위**: 2025-01-01 ~ 2025-10-31
- **특징**: 가장 빈번한 Critical 패턴
- **의미**: 텔레그램 커뮤니티 활동과 고래 움직임의 높은 연관성

#### 트위터 + 고래 동시 급증
- **발생 횟수**: 13회
- **날짜 범위**: 2024-12-08 ~ 2025-10-20
- **특징**: 텔레그램보다 덜 빈번하지만 영향력 있음

---

## 📊 시각화 결과

생성된 차트 (위치: `data/visualizations/`):

1. **correlation_heatmap.png** - 상관관계 히트맵
2. **time_series_with_spikes.png** - 시계열 + 스파이크 표시
3. **alert_statistics.png** - 알람 통계 대시보드
4. **lag_correlation_telegram_whale.png** - 텔레그램→고래 시차 상관관계
5. **lag_correlation_twitter_whale.png** - 트위터→고래 시차 상관관계
6. **alert_report.txt** - 상세 알람 리포트

---

## 🔧 구현된 시스템

### 1. 다중 소스 상관관계 분석기
**파일**: `analysis/multi_source_correlation.py`

**기능**:
- 시간별 데이터 동기화 (1시간 단위)
- Pearson/Spearman 상관계수 계산
- 통계적 유의성 검정 (p-value)
- 시차 상관관계 분석 (lag correlation)
- 동시 급증 이벤트 감지

**주요 클래스**: `MultiSourceCorrelationAnalyzer`

**사용법**:
```python
analyzer = MultiSourceCorrelationAnalyzer(
    telegram_path='data/telegram_data.csv',
    whale_path='data/whale_transactions_rows.csv',
    twitter_path='data/twitter_influencer_labeled_rows.csv'
)

# 데이터 병합
merged_df = analyzer.merge_all_data(freq='1H')

# 상관관계 분석
sig_corr = analyzer.find_significant_correlations(threshold=0.3)

# 패턴 분석
patterns = analyzer.analyze_cross_source_patterns()

# 알람 생성
alerts = analyzer.generate_all_alerts(min_priority_score=2)

# 결과 저장
analyzer.save_results()
```

### 2. Spike 알람 대시보드
**파일**: `analysis/spike_alert_dashboard.py`

**기능**:
- 상관관계 히트맵 생성
- 시계열 데이터 + 스파이크 시각화
- 알람 통계 차트 (레벨별, 시간대별, 월별)
- 시차 상관관계 플롯
- 텍스트 리포트 생성

**주요 클래스**: `SpikeAlertDashboard`

**사용법**:
```python
dashboard = SpikeAlertDashboard(
    merged_data_path='data/multi_source_merged_data.csv',
    alerts_path='data/multi_source_alerts.csv'
)

# 모든 시각화 생성
dashboard.generate_all_visualizations(output_dir='data/visualizations')
```

### 3. 실시간 Spike 모니터
**파일**: `analysis/realtime_spike_monitor.py`

**기능**:
- 실시간 데이터 모니터링
- Z-score 기반 스파이크 감지
- CRITICAL/HIGH 알람 자동 전송
- 알람 쿨다운 (중복 방지)
- 히스토리 로깅

**주요 클래스**: `RealTimeSpikeMonitor`

**사용법**:
```bash
# 테스트 모드 (한 번만 체크)
python analysis/realtime_spike_monitor.py --test

# 실시간 모니터링 (10분)
python analysis/realtime_spike_monitor.py
```

**설정 파일**: `data/monitor_config.json`
```json
{
  "spike_threshold": 2.0,
  "window_hours": 24,
  "check_interval_seconds": 60,
  "alert_cooldown_hours": 1,
  "critical_priority_threshold": 10
}
```

---

## 📝 알람 우선순위 시스템

### 점수 계산 방식

| 이벤트 | 점수 |
|--------|------|
| 텔레그램 스파이크 (z > 2.0) | +2 |
| 고래 거래 스파이크 (z > 2.0) | +3 |
| 트위터 스파이크 (z > 2.0) | +2 |
| 텔레그램+고래 동시 급증 | +5 |
| 트위터+고래 동시 급증 | +4 |
| 3개 소스 모두 급증 | +10 |

### 레벨 분류

- **CRITICAL**: 우선순위 ≥ 10
  - 3개 소스 동시 급증
  - 또는 복합 스파이크 (2개 이상 + 고래)

- **HIGH**: 5 ≤ 우선순위 < 10
  - 2개 소스 동시 급증 (고래 포함)

- **MEDIUM**: 2 ≤ 우선순위 < 5
  - 단일 소스 스파이크

- **LOW**: 우선순위 < 2
  - 약한 이상 신호

---

## 💡 핵심 인사이트

### 1. 고래 거래가 핵심 지표
- 모든 Critical 알람의 공통점: **고래 거래 급증 포함**
- 텔레그램/트위터 활동만으로는 Critical 미달
- 가중치를 고래에 가장 높게 설정 (0.5)

### 2. 시차를 고려한 선행 지표
- 텔레그램: 약 11시간 전에 신호 (장기 계획 논의)
- 트위터: 약 5시간 전에 신호 (빠른 반응)
- 조기 경보 시스템으로 활용 가능

### 3. 2025년 하반기 활성화
- 9-10월에 Critical 알람 집중 발생
- 시장 변동성 증가 시기와 일치
- 계절성 패턴 가능성

### 4. 3개 소스 동시 급증은 매우 드묾
- 전체 기간 중 단 2회 발생
- 발생 시 특별한 주의 필요
- 시장 전환점 신호 가능성

---

## 🎯 활용 방안

### 1. 거래 전략
- **진입 신호**: 텔레그램 또는 트위터 급증 후 시차만큼 대기
- **경고 신호**: CRITICAL 알람 발생 시 포지션 재검토
- **청산 신호**: 3개 소스 동시 급증 시 이익 실현 고려

### 2. 리스크 관리
- HIGH 이상 알람 시 포지션 사이즈 축소
- 고래 거래 급증 시 변동성 확대 대비
- 알람 쿨다운으로 과도한 반응 방지

### 3. 시장 모니터링
- 실시간 모니터를 백그라운드 실행
- 슬랙/텔레그램 봇 연동 (추후 구현)
- 알람 히스토리 분석으로 패턴 학습

---

## 📦 생성된 데이터 파일

### 원본 데이터
- `data/telegram_data.csv` - 텔레그램 데이터
- `data/whale_transactions_rows.csv` - 고래 거래 데이터
- `data/twitter_influencer_labeled_rows.csv` - 트위터 인플루언서 데이터

### 분석 결과
- `data/multi_source_merged_data.csv` - 통합 데이터 (90,600 rows)
- `data/multi_source_correlation_matrix.csv` - 상관관계 매트릭스
- `data/multi_source_significant_correlations.csv` - 유의미한 상관관계 (20개)
- `data/multi_source_alerts.csv` - 전체 알람 (4,627개)

### 패턴 데이터
- `data/pattern_telegram_to_whale.csv` - 텔레그램→고래 시차 상관관계
- `data/pattern_twitter_to_whale.csv` - 트위터→고래 시차 상관관계
- `data/pattern_triple_spike_events.csv` - 3개 소스 동시 급증 이벤트 (2개)
- `data/pattern_telegram_whale_spike_events.csv` - 텔레그램+고래 동시 급증 (29개)
- `data/pattern_twitter_whale_spike_events.csv` - 트위터+고래 동시 급증 (13개)

### 시각화
- `data/visualizations/correlation_heatmap.png`
- `data/visualizations/time_series_with_spikes.png`
- `data/visualizations/alert_statistics.png`
- `data/visualizations/lag_correlation_telegram_whale.png`
- `data/visualizations/lag_correlation_twitter_whale.png`
- `data/visualizations/alert_report.txt`

### 설정
- `data/monitor_config.json` - 실시간 모니터 설정

---

## 🔮 향후 개선 사항

### 1. 실시간 데이터 수집
- API 연동으로 자동 데이터 업데이트
- 웹소켓 기반 실시간 스트리밍
- 데이터베이스 통합 (PostgreSQL/TimescaleDB)

### 2. 머신러닝 모델
- LSTM 기반 시계열 예측
- 이상 탐지 모델 (Isolation Forest, Autoencoder)
- 스파이크 발생 확률 예측

### 3. 알람 시스템 확장
- 슬랙/텔레그램 봇 연동
- 이메일/SMS 알림
- 웹 대시보드 (실시간 차트)

### 4. 추가 데이터 소스
- 레딧 (Reddit) 감정 분석
- 뉴스 헤드라인 분석
- 온체인 메트릭 (가스비, DEX 거래량)
- 공포&탐욕 지수

### 5. 백테스팅
- 과거 알람 기반 거래 시뮬레이션
- 수익률/손실률 계산
- 최적 파라미터 튜닝

---

## 📚 참고 문헌

- Z-score 이상 탐지: [Wikipedia - Standard Score](https://en.wikipedia.org/wiki/Standard_score)
- 시차 상관관계: [Cross-correlation Analysis](https://en.wikipedia.org/wiki/Cross-correlation)
- Pearson 상관계수: [Correlation and Dependence](https://en.wikipedia.org/wiki/Correlation)

---

## 👥 작성자

- **프로젝트**: Big Data 암호화폐 시장 분석
- **날짜**: 2025년 11월 30일
- **버전**: 1.0

---

## 📄 라이센스

이 프로젝트는 교육 목적으로 작성되었습니다.

---

**문의사항이나 개선 제안이 있으시면 이슈를 등록해주세요!** 🚀

