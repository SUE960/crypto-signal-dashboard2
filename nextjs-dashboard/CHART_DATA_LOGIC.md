# 📊 실시간 차트 데이터 및 계산 로직

## 🎯 개요

**"고래 지갑 & 코인 가격 트렌드"** 차트는 두 가지 데이터를 표시합니다:
1. **타임시리즈 데이터** - 고래 거래와 코인 가격의 시간별 변화
2. **스파이크 포인트** - 이상치 감지 및 구매 시점 알람

---

## 📈 1. 타임시리즈 데이터

### API 엔드포인트
`/api/timeseries?range={7d|30d|90d}`

### 데이터 소스
Supabase `final_integrated_data` 테이블

### 조회 데이터 필드

```typescript
{
  timestamp: string,              // 타임스탬프
  whale_tx_count: number,         // 고래 거래 건수
  whale_volume_sum: number,       // 고래 거래 총량
  btc_close: number,              // BTC 종가 ($)
  eth_close: number,              // ETH 종가 ($)
  btc_price_change: number,       // BTC 가격 변화율 (%)
  eth_price_change: number        // ETH 가격 변화율 (%)
}
```

### 데이터 처리

1. **시간 범위 필터링**
   - `7d`: 최근 7일
   - `30d`: 최근 30일 (기본값)
   - `90d`: 최근 90일

2. **날짜 포맷팅**
   ```typescript
   date = new Date(timestamp).toLocaleDateString('ko-KR', {
     month: 'numeric',
     day: 'numeric',
     ...(range === '90d' ? {} : { hour: '2-digit' })
   })
   ```
   - 90일: "11. 9" (월. 일)
   - 30일/7일: "11. 9. 오전 05시" (월. 일. 시간)

3. **데이터 필터링**
   - `btc_close > 0` 또는 `eth_close > 0`인 데이터만 사용
   - 유효하지 않은 가격 데이터 제외

### 차트 표시

#### Y축 (왼쪽) - 고래 거래
- **단위**: 건수
- **표시**: 보라색 영역(Area) + 보라색 막대(Bar)
- **데이터**: `whale_tx_count`

#### Y축 (오른쪽) - 코인 가격
- **단위**: 달러 ($)
- **표시**: 
  - BTC: 주황색 선(Line)
  - ETH: 파란색 선(Line)
- **데이터**: `btc_close`, `eth_close`

#### X축 - 시간
- **표시**: 날짜 및 시간
- **데이터**: `timestamp` → `date` (포맷팅된 문자열)

---

## ⚠️ 2. 스파이크 포인트 감지

### API 엔드포인트
`/api/spike-points?range={7d|30d|90d}`

### 데이터 소스
Supabase `final_integrated_data` 테이블 (전체 필드)

### Z-score 계산

#### Z-score란?
통계적 이상치를 감지하는 방법. 평균으로부터 몇 표준편차 떨어져 있는지 측정.

```typescript
Z-score = (현재값 - 평균) / 표준편차
```

#### 계산 함수

```typescript
calculateZScore(values: number[], window: number = 24) {
  zscores = []
  
  for (각 시간 포인트 i) {
    // 최근 24시간 윈도우
    windowStart = max(0, i - 24 + 1)
    windowValues = values[windowStart ~ i]
    
    // 평균 계산
    mean = sum(windowValues) / windowValues.length
    
    // 표준편차 계산
    std = sqrt(sum((value - mean)²) / windowValues.length)
    
    // Z-score 계산
    zscore = std > 0 ? (values[i] - mean) / std : 0
    zscores.push(zscore)
  }
  
  return zscores
}
```

#### 각 지표의 Z-score 계산

1. **고래 거래 Z-score**
   ```typescript
   whaleZ = calculateZScore(whale_tx_count 배열)
   ```

2. **텔레그램 Z-score**
   ```typescript
   telegramZ = calculateZScore(telegram_message_count 배열)
   ```

3. **트위터 Z-score**
   ```typescript
   twitterZ = calculateZScore(twitter_engagement 배열)
   ```

4. **뉴스 Z-score**
   ```typescript
   newsZ = calculateZScore(news_count 배열)
   ```

---

## 🎯 스파이크 포인트 감지 로직

### 임계값
`threshold = 2.0` (Z-score가 2.0 이상이면 이상치로 판단)

### 우선순위 점수 계산

각 시간 포인트마다 다음 규칙으로 점수를 계산:

#### 1️⃣ 개별 스파이크 (기본 점수)

| 지표 | Z-score > 2.0 | 점수 |
|------|---------------|------|
| 고래 거래 | ✅ | +3점 |
| 텔레그램 | ✅ | +2점 |
| 트위터 | ✅ | +2점 |
| 뉴스 | ✅ | +2점 |

#### 2️⃣ 복합 스파이크 보너스

```typescript
if (고래 + 텔레그램 동시 스파이크) {
  priorityScore += 5점
  이유: "⚠️ 텔레그램+고래 동시 급증"
}

if (고래 + 트위터 동시 스파이크) {
  priorityScore += 4점
  이유: "⚠️ 트위터+고래 동시 급증"
}

if (고래 + 텔레그램 + 트위터 모두 스파이크) {
  priorityScore += 10점
  이유: "🚨 3개 소스 모두 급증 (CRITICAL)"
}
```

#### 3️⃣ 가격 급변 보너스

```typescript
if (|btc_change| > 2% || |eth_change| > 2%) {
  priorityScore += 2점
  이유: "가격 급변 (BTC X%, ETH Y%)"
}
```

### 알람 레벨 결정

```typescript
if (priorityScore >= 5) {
  alertLevel = 
    priorityScore >= 10 ? 'CRITICAL' :
    priorityScore >= 7 ? 'HIGH' :
    'MEDIUM'
}
```

### 스파이크 포인트 생성 조건

**조건**: `priorityScore >= 5`

스파이크 포인트가 생성되면 다음 정보가 포함됩니다:

```typescript
{
  timestamp: string,              // 타임스탬프
  date: string,                   // 포맷팅된 날짜
  priorityScore: number,          // 우선순위 점수
  alertLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM',
  reasons: string[],              // 스파이크 발생 이유 배열
  details: {
    whale_zscore?: number,        // 고래 거래 Z-score
    telegram_zscore?: number,     // 텔레그램 Z-score
    twitter_zscore?: number,      // 트위터 Z-score
    news_zscore?: number,         // 뉴스 Z-score
    btc_price: number,            // BTC 가격
    eth_price: number,            // ETH 가격
    telegram_sentiment: number,   // 텔레그램 감정
    twitter_sentiment: number,    // 트위터 감정
    news_sentiment: number,      // 뉴스 감정
    price_change?: {              // 가격 변화
      btc: number,
      eth: number
    }
  }
}
```

---

## 📊 차트 표시 로직

### 차트 타입

1. **선형 (Line)**: 선 그래프만 표시
2. **영역 (Area)**: 영역 그래프로 표시
3. **복합 (Composed)**: 영역 + 막대 + 선 조합 (기본값)

### 코인 선택

- **BTC**: BTC 가격만 표시
- **ETH**: ETH 가격만 표시
- **Both**: BTC와 ETH 모두 표시 (기본값)

### 스파이크 마커 표시

스파이크 포인트가 감지되면:
- 차트에 **금색 수직선** 표시
- 라벨: **"⭐ SPIKE!"**
- 툴팁에 상세 정보 표시

---

## 🔍 사용되는 모든 데이터 필드

### 타임시리즈 차트용

| 필드명 | 용도 | 표시 방식 |
|--------|------|----------|
| `timestamp` | 시간축 | X축 라벨 |
| `whale_tx_count` | 고래 거래 | 보라색 영역 + 막대 |
| `whale_volume_sum` | 고래 거래량 | (현재 미표시) |
| `btc_close` | BTC 가격 | 주황색 선 |
| `eth_close` | ETH 가격 | 파란색 선 |
| `btc_price_change` | BTC 변화율 | (툴팁에 표시) |
| `eth_price_change` | ETH 변화율 | (툴팁에 표시) |

### 스파이크 감지용

| 필드명 | 용도 | 계산 방식 |
|--------|------|----------|
| `whale_tx_count` | 고래 거래 Z-score | 24시간 윈도우 |
| `telegram_message_count` | 텔레그램 Z-score | 24시간 윈도우 |
| `twitter_engagement` | 트위터 Z-score | 24시간 윈도우 |
| `news_count` | 뉴스 Z-score | 24시간 윈도우 |
| `btc_price_change` | 가격 급변 감지 | 절댓값 > 2% |
| `eth_price_change` | 가격 급변 감지 | 절댓값 > 2% |
| `btc_close` | 스파이크 시점 가격 | 상세 정보 |
| `eth_close` | 스파이크 시점 가격 | 상세 정보 |
| `telegram_avg_sentiment` | 감정 정보 | 상세 정보 |
| `twitter_sentiment` | 감정 정보 | 상세 정보 |
| `news_sentiment_avg` | 감정 정보 | 상세 정보 |

---

## 📈 데이터 흐름

```
Supabase (final_integrated_data)
    ↓
API Routes
    ├─ /api/timeseries → 타임시리즈 데이터
    └─ /api/spike-points → 스파이크 포인트 (Z-score 계산)
    ↓
RealTimeChart Component
    ├─ 차트 렌더링 (Recharts)
    └─ 스파이크 마커 표시
    ↓
사용자 화면
```

---

## 🎯 계산 예시

### 예시 1: 고래 거래 스파이크

**상황:**
- 평소 고래 거래: 평균 50건, 표준편차 10건
- 현재 고래 거래: 80건

**계산:**
```
Z-score = (80 - 50) / 10 = 3.0
```

**결과:**
- Z-score > 2.0 → 스파이크 감지
- 우선순위 점수: +3점
- 이유: "고래 거래 급증 (z=3.00)"

---

### 예시 2: 복합 스파이크

**상황:**
- 고래 거래 Z-score: 2.5
- 텔레그램 Z-score: 2.3
- 트위터 Z-score: 2.1
- BTC 가격 변화: +3.5%

**계산:**
```
우선순위 점수 = 
  3 (고래) + 
  2 (텔레그램) + 
  2 (트위터) + 
  10 (3개 소스 모두) + 
  2 (가격 급변)
= 19점
```

**결과:**
- 우선순위 점수: 19점
- 알람 레벨: **CRITICAL**
- 이유:
  - "고래 거래 급증 (z=2.50)"
  - "텔레그램 활동 급증 (z=2.30)"
  - "트위터 인게이지먼트 급증 (z=2.10)"
  - "🚨 3개 소스 모두 급증 (CRITICAL)"
  - "가격 급변 (BTC 3.50%, ETH 0.00%)"

---

## 📝 요약

### 타임시리즈 데이터
- **목적**: 시간에 따른 고래 거래와 코인 가격 변화 시각화
- **데이터**: Supabase에서 직접 조회
- **표시**: 영역, 막대, 선 그래프

### 스파이크 포인트
- **목적**: 이상치 감지 및 구매 시점 알람
- **방법**: Z-score 계산 (24시간 윈도우)
- **임계값**: Z-score > 2.0
- **필터링**: 우선순위 점수 >= 5점만 표시

---

## 🔍 코드 위치

- **API 라우트**: 
  - `app/api/timeseries/route.ts`
  - `app/api/spike-points/route.ts`
- **Supabase 함수**: 
  - `lib/supabase.ts` → `getTimeseriesData()`
  - `lib/supabase.ts` → `getSpikeDetectionData()`
- **컴포넌트**: `components/RealTimeChart.tsx`

---

**참고:** 현재 테이블에 데이터가 없으면 더미 데이터가 표시됩니다.

