# 📊 HOME 화면 데이터 소스 분석

## 🏠 HOME 페이지 구성 요소

HOME 페이지(`app/page.tsx`)는 다음 컴포넌트들로 구성됩니다:

1. **CompositeScoreHeader** - 종합 점수 헤더
2. **RealTimeChart** - 실시간 차트
3. **UpbitStyleTabs** - 탭 패널
   - CorrelationPanel (코인가격, 고래지갑, 뉴스)
   - SpikeAlarmList (spike 알람)
   - NewsListPanel (지금뉴스)

---

## 📡 각 컴포넌트의 데이터 소스

### 1. CompositeScoreHeader (종합 점수 헤더)

**API 엔드포인트:** `/api/composite-score`

**데이터 소스:** Supabase `final_integrated_data` 테이블

**사용 데이터:**
- `whale_tx_count` - 고래 거래 건수
- `whale_volume_sum` - 고래 거래 총량
- `btc_close`, `eth_close` - BTC/ETH 종가
- `btc_price_change`, `eth_price_change` - 가격 변화율
- `telegram_message_count` - 텔레그램 메시지 수
- `telegram_avg_sentiment` - 텔레그램 평균 감정
- `twitter_engagement` - 트위터 인게이지먼트
- `twitter_sentiment` - 트위터 감정
- `news_count` - 뉴스 개수
- `news_sentiment_avg` - 뉴스 평균 감정

**계산 로직:**
- 최근 30일 데이터 사용
- 각 지표를 0-100 점수로 정규화
- 가중 평균으로 종합 점수 계산:
  - 텔레그램 활동: 20%
  - 고래 거래: 30%
  - 트위터 인게이지먼트: 20%
  - 뉴스 감정: 30%

---

### 2. RealTimeChart (실시간 차트)

**API 엔드포인트:**
- `/api/timeseries?range={7d|30d|90d}` - 타임시리즈 데이터
- `/api/spike-points?range={7d|30d|90d}` - 스파이크 포인트

**데이터 소스:** Supabase `final_integrated_data` 테이블

**사용 데이터:**
- `timestamp` - 타임스탬프
- `whale_tx_count` - 고래 거래 건수
- `whale_volume_sum` - 고래 거래 총량
- `btc_close`, `eth_close` - BTC/ETH 종가
- `btc_price_change`, `eth_price_change` - 가격 변화율

**차트 표시:**
- 고래 거래 건수 (Area + Bar)
- BTC 가격 (Line)
- ETH 가격 (Line)
- 스파이크 포인트 (ReferenceLine)

---

### 3. CorrelationPanel (상관관계 패널)

**데이터 소스:** 정적 데이터 (`lib/correlationData.ts`)

**사용 데이터:**
- `priceCorrelations` - 코인 가격과의 상관관계
- `whaleCorrelations` - 고래 거래와의 상관관계
- `newsCorrelations` - 뉴스와의 상관관계

**참고:** 현재는 정적 데이터를 사용하지만, 실제로는 Supabase에서 계산된 상관관계 데이터를 사용할 수 있습니다.

---

### 4. SpikeAlarmList (스파이크 알람 리스트)

**API 엔드포인트:** `/api/spike-points?range={7d|30d|90d}`

**데이터 소스:** Supabase `final_integrated_data` 테이블

**사용 데이터:**
- `timestamp` - 타임스탬프
- `whale_tx_count` - 고래 거래 건수
- `telegram_message_count` - 텔레그램 메시지 수
- `twitter_engagement` - 트위터 인게이지먼트
- `news_count` - 뉴스 개수
- `btc_close`, `eth_close` - 가격
- `btc_price_change`, `eth_price_change` - 가격 변화율
- `telegram_avg_sentiment` - 텔레그램 감정
- `twitter_sentiment` - 트위터 감정
- `news_sentiment_avg` - 뉴스 감정

**계산 로직:**
- Z-score 계산 (24시간 윈도우)
- 임계값 2.0 이상 시 스파이크 감지
- 우선순위 점수 계산:
  - 고래 거래 스파이크: +3점
  - 텔레그램 스파이크: +2점
  - 트위터 스파이크: +2점
  - 뉴스 스파이크: +2점
  - 복합 스파이크 보너스: +4~10점
  - 가격 급변: +2점
- 우선순위 5점 이상만 표시

---

### 5. NewsListPanel (뉴스 리스트 패널)

**API 엔드포인트:** `/api/news/recent?limit=50`

**데이터 소스:** 현재는 더미 데이터 또는 별도 뉴스 API

**사용 데이터:**
- 뉴스 제목, 내용, 출처
- 발행 시간
- 감정 분석 (bullish/bearish)
- 관련 코인 (Bitcoin, Ethereum 등)

**참고:** 현재 Supabase와 연동되지 않았을 수 있습니다. 필요시 뉴스 데이터를 Supabase에 저장하도록 수정 가능합니다.

---

## 📋 Supabase 테이블 구조

### `final_integrated_data` 테이블

HOME 화면의 대부분의 데이터는 이 테이블에서 가져옵니다:

```sql
CREATE TABLE final_integrated_data (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  whale_tx_count NUMERIC DEFAULT 0,           -- 고래 거래 건수
  whale_volume_sum NUMERIC DEFAULT 0,          -- 고래 거래 총량
  btc_close NUMERIC DEFAULT 0,                -- BTC 종가
  eth_close NUMERIC DEFAULT 0,                -- ETH 종가
  btc_price_change NUMERIC DEFAULT 0,         -- BTC 가격 변화율
  eth_price_change NUMERIC DEFAULT 0,         -- ETH 가격 변화율
  telegram_message_count NUMERIC DEFAULT 0,    -- 텔레그램 메시지 수
  telegram_avg_sentiment NUMERIC DEFAULT 0,    -- 텔레그램 평균 감정
  twitter_engagement NUMERIC DEFAULT 0,        -- 트위터 인게이지먼트
  twitter_sentiment NUMERIC DEFAULT 0,         -- 트위터 감정
  news_count NUMERIC DEFAULT 0,                 -- 뉴스 개수
  news_sentiment_avg NUMERIC DEFAULT 0,       -- 뉴스 평균 감정
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔄 데이터 흐름

```
Supabase (final_integrated_data)
    ↓
API Routes (/api/*)
    ↓
React Components
    ↓
HOME 화면 표시
```

### API 라우트 매핑

1. `/api/composite-score` → `getCompositeScoreData()` → CompositeScoreHeader
2. `/api/timeseries` → `getTimeseriesData()` → RealTimeChart
3. `/api/spike-points` → `getSpikeDetectionData()` → RealTimeChart, SpikeAlarmList
4. `/api/news/recent` → NewsListPanel (현재 Supabase 미연동 가능)

---

## 📊 데이터 요약

### Supabase에서 가져오는 데이터 (실시간)
- ✅ 종합 점수 계산 데이터
- ✅ 타임시리즈 차트 데이터
- ✅ 스파이크 포인트 데이터

### 정적 데이터
- ⚠️ 상관관계 데이터 (`correlationData.ts`)

### 별도 API 또는 더미 데이터
- ⚠️ 뉴스 데이터 (`/api/news/recent`)

---

## 🎯 요약

HOME 화면은 주로 **Supabase의 `final_integrated_data` 테이블**에서 데이터를 가져옵니다:

1. **종합 점수**: 4개 지표의 가중 평균
2. **실시간 차트**: 고래 거래 + BTC/ETH 가격
3. **스파이크 알람**: Z-score 기반 이상치 감지
4. **상관관계**: 정적 데이터 (향후 Supabase 연동 가능)
5. **뉴스**: 별도 API (향후 Supabase 연동 가능)

---

**참고:** 현재 테이블에 데이터가 없으면 더미 데이터나 빈 배열이 표시됩니다. 데이터를 추가하면 실시간으로 반영됩니다!

