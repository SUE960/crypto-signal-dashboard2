# 암호화폐 커뮤니티-거래 상관관계 분석 프로젝트
## 발표 자료 - 상세 로직 설명

---

## 📋 프로젝트 개요

### 목적
암호화폐 커뮤니티 활동(텔레그램, 트위터, 뉴스)과 고래 지갑 거래, 가격 변동 간의 상관관계를 분석하여 시장 신호를 실시간으로 모니터링하는 대시보드를 구축한다.

### 핵심 가설
1. **커뮤니티 활동 급증은 가격 변동의 선행 지표가 될 수 있다.**
2. **고래 지갑 거래와 커뮤니티 활동이 동시에 증가하면 강한 시장 신호를 나타낸다.**
3. **다양한 데이터 소스를 통합하면 시장 예측 정확도가 높아진다.**

---

## 📊 데이터 소스 및 수집 방법

### 2.1 텔레그램 데이터 (telegram_data.csv)
**수집 스크립트**: `scripts/collect_telegram_data.py`

**수집 방법**: Telethon API 기반 채널 메시지 수집 (@Ethereum, @Bitcoin 등)

**수집 데이터**:
- 시간당 메시지 수
- 평균 조회수
- 전달 횟수
- 반응 수
- 평균 감정 점수
- 긍정·부정·중립 비율

**감정 분석 모델**: VADER

### 2.2 트위터 인플루언서 데이터 (twitter_influencer_labeled_rows.csv)
**수집 데이터**: 게시 날짜, 좋아요 수, 감정 점수, 게시글 내용

### 2.3 코인니스 뉴스 데이터 (coinness_data.csv)
**수집 스크립트**:
- `scripts/collect_coinness_data.py`
- `scripts/collect_coinness_selenium.py`
- `scripts/collect_coinness_infinite_scroll.py`

**수집 방법**: Selenium 기반 스크래핑, 최대 2만 건 기사 확보

**수집 데이터**: 기사 시각, 제목, 내용, 감정 점수

### 2.4 고래 지갑 거래 데이터 (whale_transactions_rows_ETH_rev1.csv)
**데이터 구성**: 거래 시간, 시간당 거래 빈도, 거래량(ETH, USD)

### 2.5 가격 데이터
**ETH 가격**: `price_history_eth_rows.csv`  
**BTC 가격**: `price_history_btc_rows.csv`  
(OHLC, 거래량, 거래 횟수 포함)

---

## 🔢 각 지수/점수 계산 로직 상세 설명

### 1. Z-score (표준화 점수)

#### 1.1 정의 및 목적
Z-score는 현재 값이 평균으로부터 몇 표준편차만큼 떨어져 있는지를 나타내는 지표입니다. 이상치 탐지와 스파이크 감지에 사용됩니다.

#### 1.2 수식
```
Z-score = (현재값 - 이동평균) / 이동표준편차
```

**구체적 계산 과정**:

1. **24시간 이동평균 계산**:
   ```
   MA_24(t) = (1/24) × Σ[i=t-23 to t] X(i)
   ```
   - `X(i)`: i시점의 값
   - `t`: 현재 시점

2. **24시간 이동표준편차 계산**:
   ```
   STD_24(t) = √[(1/24) × Σ[i=t-23 to t] (X(i) - MA_24(t))²]
   ```

3. **Z-score 계산**:
   ```
   Z-score(t) = (X(t) - MA_24(t)) / (STD_24(t) + ε)
   ```
   - `ε = 1e-10`: 0으로 나누기 방지

#### 1.3 적용 변수
- `ETH_price_zscore`: ETH 가격의 Z-score
- `tx_frequency_zscore`: 고래 거래 빈도의 Z-score
- `message_count_zscore`: 텔레그램 메시지 수의 Z-score

#### 1.4 해석
- **Z-score = 0**: 평균과 동일
- **|Z-score| > 2.5**: 이상치 (상위/하위 1% 수준)
- **|Z-score| > 3.0**: 극단적 이상치 (상위/하위 0.1% 수준)

#### 1.5 코드 구현 위치
- **계산**: `scripts/preprocess_data.py` (143-148줄)
- **사용**: `analysis/spike_detector.py` (27-57줄)

---

### 2. 텔레그램 점수 (Telegram Score)

#### 2.1 정의 및 목적
텔레그램 커뮤니티 활동을 0-100 점수로 정량화하여 시장 신호의 강도를 측정합니다.

#### 2.2 계산 과정

**Step 1: 메시지 수 정규화 (40% 가중치)**

1. **24시간 이동평균 및 표준편차 계산**:
   ```
   msg_rolling_mean(t) = (1/24) × Σ[i=t-23 to t] message_count(i)
   msg_rolling_std(t) = √[(1/24) × Σ[i=t-23 to t] (message_count(i) - msg_rolling_mean(t))²]
   ```

2. **정규화 범위 설정**:
   ```
   min_val(t) = msg_rolling_mean(t) - msg_rolling_std(t)
   max_val(t) = msg_rolling_mean(t) + msg_rolling_std(t)
   ```

3. **0-1 정규화**:
   ```
   msg_score(t) = (message_count(t) - min_val(t)) / (max_val(t) - min_val(t) + ε)
   msg_score(t) = clip(msg_score(t), 0, 1)  # 0과 1 사이로 제한
   ```

**Step 2: 감정 점수 변환 (40% 가중치)**

```
sentiment_score(t) = (avg_sentiment(t) + 1) / 2
```
- `avg_sentiment(t)`: -1 ~ 1 범위의 감정 점수
- 변환 후: 0 ~ 1 범위

**Step 3: 변화율 점수 (20% 가중치)**

1. **변화율 계산**:
   ```
   msg_change(t) = (message_count(t) - message_count(t-1)) / message_count(t-1)
   ```

2. **0-1 정규화**:
   ```
   change_score(t) = clip((msg_change(t) + 1) / 2, 0, 1)
   ```
   - 변화율이 -100% → 0
   - 변화율이 0% → 0.5
   - 변화율이 +100% → 1

**Step 4: 최종 텔레그램 점수**

```
telegram_score(t) = (msg_score(t) × 0.4 + sentiment_score(t) × 0.4 + change_score(t) × 0.2) × 100
```

#### 2.3 점수 해석
- **0-25**: 매우 낮은 활동 (강한 하락 신호)
- **25-40**: 낮은 활동 (하락 신호)
- **40-60**: 평균 활동 (중립)
- **60-75**: 높은 활동 (상승 신호)
- **75-100**: 매우 높은 활동 (강한 상승 신호)

#### 2.4 코드 구현 위치
- `utils/composite_score.py` (39-74줄)

---

### 3. 뉴스 점수 (News Score)

#### 3.1 정의 및 목적
코인니스 뉴스의 시간당 기사 수를 정규화하여 뉴스 활동 강도를 0-100 점수로 표현합니다.

#### 3.2 계산 과정

**Step 1: 시간당 뉴스 수 집계**

```
news_count(h) = 시간 h에 발행된 뉴스 기사 수
```

**Step 2: 24시간 이동평균 및 표준편차 계산**

```
rolling_mean(t) = (1/24) × Σ[i=t-23 to t] news_count(i)
rolling_std(t) = √[(1/24) × Σ[i=t-23 to t] (news_count(i) - rolling_mean(t))²]
```

**Step 3: 정규화**

```
min_val(t) = rolling_mean(t) - rolling_std(t)
max_val(t) = rolling_mean(t) + rolling_std(t)
news_score(t) = (news_count(t) - min_val(t)) / (max_val(t) - min_val(t) + ε)
news_score(t) = clip(news_score(t), 0, 1)
```

**Step 4: 최종 뉴스 점수**

```
news_score(t) = news_score(t) × 100
```

#### 3.3 코드 구현 위치
- `utils/composite_score.py` (76-110줄)

---

### 4. 트위터 점수 (Twitter Score)

#### 4.1 정의 및 목적
트위터 인플루언서의 게시글 좋아요 수와 감정 점수를 통합하여 0-100 점수로 표현합니다.

#### 4.2 계산 과정

**Step 1: 시간당 집계**

```
likes(h) = 시간 h에 게시된 트윗들의 총 좋아요 수
sentiment_score(h) = 시간 h에 게시된 트윗들의 평균 감정 점수
```

**Step 2: 좋아요 수 정규화 (50% 가중치)**

1. **24시간 이동평균 및 표준편차**:
   ```
   likes_rolling_mean(t) = (1/24) × Σ[i=t-23 to t] likes(i)
   likes_rolling_std(t) = √[(1/24) × Σ[i=t-23 to t] (likes(i) - likes_rolling_mean(t))²]
   ```

2. **정규화**:
   ```
   min_val(t) = likes_rolling_mean(t) - likes_rolling_std(t)
   max_val(t) = likes_rolling_mean(t) + likes_rolling_std(t)
   likes_score(t) = (likes(t) - min_val(t)) / (max_val(t) - min_val(t) + ε)
   likes_score(t) = clip(likes_score(t), 0, 1)
   ```

**Step 3: 감정 점수 변환 (50% 가중치)**

```
sentiment_score_normalized(t) = (sentiment_score(t) + 1) / 2
```
- `sentiment_score(t)`: -1 ~ 1 범위
- 변환 후: 0 ~ 1 범위

**Step 4: 최종 트위터 점수**

```
twitter_score(t) = (likes_score(t) × 0.5 + sentiment_score_normalized(t) × 0.5) × 100
```

#### 4.3 코드 구현 위치
- `utils/composite_score.py` (112-152줄)

---

### 5. 종합 점수 (Composite Score)

#### 5.1 정의 및 목적
텔레그램, 뉴스, 트위터 점수를 가중 평균하여 단일 종합 점수를 계산합니다.

#### 5.2 수식

```
composite_score(t) = telegram_score(t) × W_telegram + news_score(t) × W_news + twitter_score(t) × W_twitter
```

**기본 가중치**:
- `W_telegram = 0.3` (30%)
- `W_news = 0.4` (40%)
- `W_twitter = 0.3` (30%)

#### 5.3 신호 레벨 분류

```
if composite_score(t) >= 75:
    signal_level = 'strong_bullish'      # 강한 상승 신호
elif composite_score(t) >= 60:
    signal_level = 'bullish'             # 상승 신호
elif composite_score(t) >= 40:
    signal_level = 'neutral'             # 중립
elif composite_score(t) >= 25:
    signal_level = 'bearish'             # 하락 신호
else:
    signal_level = 'strong_bearish'      # 강한 하락 신호
```

#### 5.4 트렌드 계산

최근 24시간 동안의 점수 변화를 분석:

```
trend_slope = composite_score(t) - composite_score(t-24)

if trend_slope > 5:
    trend = 'bullish'      # 상승 추세
elif trend_slope < -5:
    trend = 'bearish'      # 하락 추세
else:
    trend = 'neutral'       # 중립
```

#### 5.5 코드 구현 위치
- `utils/composite_score.py` (154-206줄)

---

### 6. 상관계수 (Correlation Coefficient)

#### 6.1 Pearson 상관계수

**수식**:
```
r = Σ[(X_i - X̄)(Y_i - Ȳ)] / √[Σ(X_i - X̄)² × Σ(Y_i - Ȳ)²]
```

**의미**:
- **-1 ~ 1** 범위
- **1**: 완벽한 양의 선형 관계
- **0**: 선형 관계 없음
- **-1**: 완벽한 음의 선형 관계

**해석 기준**:
- **|r| ≥ 0.7**: 강한 상관관계
- **0.4 ≤ |r| < 0.7**: 중간 상관관계
- **|r| < 0.4**: 약한 상관관계

#### 6.2 Spearman 상관계수

**수식**:
```
ρ = 1 - (6 × Σd²) / (n × (n² - 1))
```
- `d`: 순위 차이
- `n`: 데이터 개수

**의미**:
- 순위 기반 상관관계 (비선형 관계 측정)
- 이상치에 강건함

#### 6.3 코드 구현 위치
- `analysis/correlation_analysis.py` (29-63줄)

---

### 7. 시차 상관관계 (Lag Correlation)

#### 7.1 정의 및 목적
변수 A가 변수 B보다 N시간 앞서서 변화할 때의 상관관계를 측정하여 선행 지표를 찾습니다.

#### 7.2 수식

**Lag 0 (동시 상관관계)**:
```
r(0) = Pearson_Correlation(X(t), Y(t))
```

**Lag k (k시간 선행)**:
```
r(k) = Pearson_Correlation(X(t-k), Y(t))
```
- `X(t-k)`: k시간 전의 X 값
- `Y(t)`: 현재 시점의 Y 값

#### 7.3 계산 과정

```python
for lag in range(0, max_lag + 1):
    if lag == 0:
        # 동시 상관관계
        x = data[col1]
        y = data[col2]
    else:
        # col1이 col2보다 lag 시간 앞서는 경우
        x = data[col1].iloc[:-lag]  # 처음부터 (끝-lag)까지
        y = data[col2].iloc[lag:]   # lag부터 끝까지
    
    correlation, p_value = pearsonr(x, y)
```

#### 7.4 유의성 검정

```
significant = True if p_value < 0.05 else False
```

#### 7.5 해석 예시
- **Lag 2에서 최대 상관관계**: 텔레그램 메시지 수가 2시간 후 ETH 가격과 가장 높은 상관관계
- **의미**: 텔레그램 활동이 가격 변동의 2시간 선행 지표

#### 7.6 코드 구현 위치
- `analysis/correlation_analysis.py` (65-118줄)

---

### 8. 그랜저 인과관계 검정 (Granger Causality Test)

#### 8.1 정의 및 목적
변수 A가 변수 B의 원인인지 통계적으로 검정합니다.

#### 8.2 가설
- **H0 (귀무가설)**: A는 B의 원인이 아니다
- **H1 (대립가설)**: A는 B의 원인이다

#### 8.3 검정 통계량

**F-통계량**:
```
F = [(SSR_restricted - SSR_unrestricted) / p] / [SSR_unrestricted / (n - 2p - 1)]
```
- `SSR_restricted`: 제한된 모델의 잔차 제곱합 (A를 포함하지 않음)
- `SSR_unrestricted`: 비제한 모델의 잔차 제곱합 (A를 포함)
- `p`: 시차 개수
- `n`: 관측치 개수

#### 8.4 판정 기준

```
if p_value < 0.05:
    H0 기각 → A는 B의 원인이다 (인과관계 존재)
else:
    H0 채택 → A는 B의 원인이 아니다
```

#### 8.5 코드 구현 위치
- `analysis/correlation_analysis.py` (120-161줄)

---

### 9. 변동성 분석 (Volatility Analysis)

#### 9.1 정의 및 목적
커뮤니티 활동이 급증할 때 가격 변동성이 평상시보다 얼마나 증가하는지 측정합니다.

#### 9.2 계산 과정

**Step 1: 트리거 이벤트 식별**

```
trigger_events = {t | |Z-score(trigger_col, t)| > threshold}
```
- `threshold = 2.0` (기본값)
- 예: `|message_count_zscore| > 2.0`

**Step 2: 이벤트 발생 시 변동성 계산**

각 트리거 이벤트 발생 후 6시간 동안의 가격 변동성:

```
for each event_time in trigger_events:
    base_value = price(event_time)
    future_values = price[event_time : event_time + 6]
    
    max_value = max(future_values)
    min_value = min(future_values)
    
    max_change = ((max_value - base_value) / base_value) × 100
    min_change = ((min_value - base_value) / base_value) × 100
    
    volatility = max(|max_change|, |min_change|)
```

**Step 3: 평균 이벤트 변동성**

```
avg_volatility_during_events = mean(volatilities)
```

**Step 4: 평상시 변동성 계산**

```
normal_periods = {t | |Z-score(trigger_col, t)| ≤ 1.0}
# 24시간마다 샘플링하여 계산
avg_volatility_normal = mean(normal_volatilities)
```

**Step 5: 변동성 비율**

```
volatility_ratio = avg_volatility_during_events / avg_volatility_normal
```

#### 9.3 해석
- **volatility_ratio > 1.5**: 이벤트 시 변동성이 평상시보다 1.5배 이상 증가
- **의미**: 커뮤니티 활동 급증이 가격 변동성 증가와 연관됨

#### 9.4 코드 구현 위치
- `analysis/correlation_analysis.py` (163-232줄)

---

### 10. 스파이크 감지 알고리즘

#### 10.1 Z-score 기반 스파이크 감지

**알고리즘**:
```
if |Z-score(t)| > threshold:
    spike_detected = True
    spike_magnitude = |Z-score(t)|
    spike_type = 'positive_spike' if Z-score(t) > 0 else 'negative_spike'
```

**기본 임계값**: `threshold = 2.5`

#### 10.2 이동평균 기반 스파이크 감지

**알고리즘**:
```
MA_24(t) = 24시간 이동평균
pct_from_ma(t) = ((현재값(t) - MA_24(t)) / MA_24(t)) × 100

if |pct_from_ma(t)| > threshold_pct:
    spike_detected = True
    spike_magnitude = |pct_from_ma(t)|
    spike_type = 'surge' if pct_from_ma(t) > 0 else 'drop'
```

**기본 임계값**: `threshold_pct = 50%`

#### 10.3 변화율 기반 스파이크 감지

**알고리즘**:
```
roc(t) = ((현재값(t) - 현재값(t-3)) / 현재값(t-3)) × 100

if |roc(t)| > threshold_pct:
    spike_detected = True
    spike_magnitude = |roc(t)|
    spike_type = 'rapid_increase' if roc(t) > 0 else 'rapid_decrease'
```

**기본 임계값**: `threshold_pct = 30%`

#### 10.4 다중 지표 통합 스파이크 감지

**알고리즘**:

1. **각 지표의 Z-score를 0-1로 정규화**:
   ```
   normalized = 1 / (1 + exp(-Z-score))
   score = |normalized - 0.5| × 2
   ```

2. **가중 평균 계산**:
   ```
   combined_score(t) = Σ[score_i(t) × weight_i]
   ```

3. **임계값 초과 시 스파이크 감지**:
   ```
   if combined_score(t) > threshold:
       spike_detected = True
   ```

**기본 임계값**: `threshold = 0.7`

#### 10.5 텔레그램-고래 동시 스파이크 (CRITICAL)

**알고리즘**:
```
if (telegram_zscore(t) > 2.0) AND (whale_zscore(t) > 2.0):
    critical_spike_detected = True
    alert_level = 'critical'
    spike_magnitude = (telegram_zscore(t) + whale_zscore(t)) / 2
```

**의미**: 커뮤니티와 대형 투자자가 동시에 활동 → 강한 시장 움직임 예상

#### 10.6 코드 구현 위치
- `analysis/spike_detector.py` (전체)

---

### 11. 알람 레벨 분류

#### 11.1 Z-score 기반 분류

```
if spike_magnitude > 5.0:
    alert_level = 'critical'      # 극단적 이상치
elif spike_magnitude > 3.0:
    alert_level = 'high'           # 높은 이상치
elif spike_magnitude > 2.0:
    alert_level = 'medium'         # 중간 이상치
else:
    alert_level = 'low'            # 낮은 이상치
```

#### 11.2 코드 구현 위치
- `utils/alert_system.py` (76-96줄)

---

## 📈 데이터 전처리 및 통합

### 전처리 스크립트: `scripts/preprocess_data.py`

### 데이터 로더: `utils/data_loader.py`

### 주요 단계
1. 모든 데이터 로드 및 타임존 통일
2. 텔레그램, 트위터, 뉴스 데이터를 시간 단위로 집계
3. 고래 거래 데이터를 기준 시간축으로 병합
4. 결측치는 Forward Fill 또는 0 처리
5. 가격, 거래량, 커뮤니티 활동 관련 파생 변수 생성

### 생성되는 주요 변수 예시
- 가격 변화율, 이동평균, 표준편차, Z-score, 볼린저 밴드
- 고래 거래량 변화율 및 Z-score
- 커뮤니티 활동 변화율, 이동평균, Z-score
- 시간 특성(시, 요일, 월 등)

### 최종 결과물: `data/processed_data.csv`

---

## 🖥️ 대시보드 구성

### 5.1 Streamlit 대시보드 (app.py)

**Overview**
- 실시간 가격
- 주요 지표 카드
- 가격·거래량·커뮤니티 활동 통합 차트
- 정규화된 주요 지표 비교

**상관관계 분석 페이지**
- 상관계수 히트맵
- 시차 상관관계
- 그랜저 인과관계 결과

**스파이크 알람 페이지**
- 감지된 스파이크 목록
- 스파이크 타임라인 및 유형별 상세

### 5.2 Next.js 대시보드 (nextjs-dashboard/)

**주요 기능**
- 종합 점수 표시
- 가격 및 고래 활동 상관지표 표시
- 최근 뉴스 출력

**API**
- `/api/composite-score`
- `/api/timeseries`

---

## 📁 프로젝트 구조

```
big_data/
├── app.py
├── app_new.py
├── main.py
├── analysis/
├── utils/
├── components/
├── scripts/
├── data/
└── nextjs-dashboard/
```

---

## 🔍 주요 분석 결과 예시

- 텔레그램 메시지 수와 ETH 가격의 상관관계는 약 0.3~0.5
- 고래 거래와 ETH 가격의 상관관계는 약 0.4~0.6
- 텔레그램 메시지 수는 ETH 가격과 약 2~6시간 시차를 두고 최대 상관
- 고래 거래는 1~3시간 선행 신호
- 커뮤니티 활동 급증 시 가격 변동성이 평상시 대비 1.5~2배 상승

---

## 🚀 실행 방법

**데이터 전처리**
```bash
python scripts/preprocess_data.py
```

**Streamlit 실행**
```bash
streamlit run app.py
```

**Next.js 실행**
```bash
cd nextjs-dashboard
npm install
npm run dev
```

---

## 📊 데이터 흐름도

```
데이터 수집
    ↓
전처리 및 병합
    ↓
통합 데이터 생성
    ↓
상관·시차 분석 및 스파이크 감지
    ↓
Streamlit/Next.js 대시보드
```

---

## 🎯 핵심 기여도

1. 텔레그램, 트위터, 뉴스, 고래 거래, 가격 데이터를 통합
2. 상관관계·시차·인과관계 기반 선행 지표 탐색
3. 다중 스파이크 감지 알고리즘 구현
4. 종합 점수 기반 시장 신호 산출
5. 실시간 모니터링 가능한 대시보드 개발

---

## 🔮 향후 개선 사항

1. LSTM·Prophet 기반 예측 모델 추가
2. 실시간 데이터 수집 자동화
3. 텔레그램·이메일 알림 구현
4. Reddit, Discord 등 데이터 소스 확장
5. 전략 백테스팅 시스템 구축

---

## 💻 기술 스택

- Python, Pandas, NumPy, SciPy, statsmodels
- Telethon, Selenium
- Plotly, Streamlit
- Next.js, React, TypeScript

---

## 📄 참고 파일

- `DEPLOYMENT_GUIDE.md`
- `README.md`
- `requirements.txt`

---

**작성일**: 2025년  
**프로젝트명**: 암호화폐 커뮤니티-거래 상관관계 분석 대시보드
