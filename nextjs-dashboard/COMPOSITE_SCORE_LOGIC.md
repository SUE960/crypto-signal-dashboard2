# 📊 종합 점수 (Composite Score) 계산 로직

## 🎯 개요

**크립토 시그널 지수**는 4가지 지표를 가중 평균하여 계산됩니다.

**표시 정보:**
- 종합 점수 (0-100점)
- 예측 정확도 (%)
- 직전 일자 대비 변화 (점수 및 변화율)

---

## 📈 계산 단계

### 1단계: 데이터 조회

**소스:** Supabase `final_integrated_data` 테이블
**기간:** 최근 30일 데이터

**조회 데이터:**
```typescript
{
  timestamp: string,
  whale_tx_count: number,           // 고래 거래 건수
  whale_volume_sum: number,         // 고래 거래 총량
  btc_close: number,                // BTC 종가
  btc_change: number,               // BTC 가격 변화율
  eth_close: number,                // ETH 종가
  eth_change: number,               // ETH 가격 변화율
  telegram_message_count: number,    // 텔레그램 메시지 수
  telegram_sentiment: number,        // 텔레그램 평균 감정 (-1 ~ 1)
  twitter_engagement: number,        // 트위터 인게이지먼트
  twitter_sentiment: number,         // 트위터 감정 (-1 ~ 1)
  news_count: number,                // 뉴스 개수
  news_sentiment: number             // 뉴스 평균 감정 (-1 ~ 1)
}
```

---

### 2단계: 각 지표 점수 계산 (0-100점)

#### 📊 정규화 함수

```typescript
normalize(value, min, max) = {
  if (max === min) return 50;
  return max(0, min(100, ((value - min) / (max - min)) * 100));
}
```

#### 1️⃣ 텔레그램 활동 점수 (가중치: 20%)

```typescript
telegramScore = 
  normalize(telegram_message_count, min, max) × 0.5 + 
  (telegram_sentiment + 1) × 50 × 0.5
```

**계산 방식:**
- 메시지 수: 최근 30일 데이터에서 최소/최대값 기준 정규화 (50% 가중치)
- 감정 점수: -1~1을 0~100으로 변환 (50% 가중치)
  - 감정 -1 → 0점
  - 감정 0 → 50점
  - 감정 +1 → 100점

**예시:**
- 메시지 수: 100건 (정규화 후 70점)
- 감정: 0.5 (75점)
- 최종: 70 × 0.5 + 75 × 0.5 = **72.5점**

---

#### 2️⃣ 고래 거래 점수 (가중치: 30%)

```typescript
whaleScore = 
  normalize(whale_tx_count, min, max) × 0.6 + 
  (whale_volume_sum > 0 ? 50 : 0) × 0.4
```

**계산 방식:**
- 거래 건수: 최근 30일 데이터에서 최소/최대값 기준 정규화 (60% 가중치)
- 거래량: 거래량이 있으면 50점, 없으면 0점 (40% 가중치)

**예시:**
- 거래 건수: 50건 (정규화 후 80점)
- 거래량: 있음 (50점)
- 최종: 80 × 0.6 + 50 × 0.4 = **68점**

---

#### 3️⃣ 트위터 인게이지먼트 점수 (가중치: 20%)

```typescript
twitterScore = 
  normalize(twitter_engagement, min, max) × 0.5 + 
  (twitter_sentiment + 1) × 50 × 0.5
```

**계산 방식:**
- 인게이지먼트: 최근 30일 데이터에서 최소/최대값 기준 정규화 (50% 가중치)
- 감정 점수: -1~1을 0~100으로 변환 (50% 가중치)

**예시:**
- 인게이지먼트: 5000 (정규화 후 60점)
- 감정: 0.2 (60점)
- 최종: 60 × 0.5 + 60 × 0.5 = **60점**

---

#### 4️⃣ 뉴스 감정 점수 (가중치: 30%)

```typescript
newsScore = 
  normalize(news_count, min, max) × 0.5 + 
  (news_sentiment + 1) × 50 × 0.5
```

**계산 방식:**
- 뉴스 개수: 최근 30일 데이터에서 최소/최대값 기준 정규화 (50% 가중치)
- 감정 점수: -1~1을 0~100으로 변환 (50% 가중치)

**예시:**
- 뉴스 개수: 20건 (정규화 후 65점)
- 감정: 0.3 (65점)
- 최종: 65 × 0.5 + 65 × 0.5 = **65점**

---

### 3단계: 종합 점수 계산 (가중 평균)

```typescript
compositeScore = 
  telegramScore × 0.2 +    // 20%
  whaleScore × 0.3 +        // 30%
  twitterScore × 0.2 +     // 20%
  newsScore × 0.3           // 30%
```

**예시:**
- 텔레그램: 72.5점 × 20% = 14.5점
- 고래 거래: 78.2점 × 30% = 23.46점
- 트위터: 70.1점 × 20% = 14.02점
- 뉴스: 73.8점 × 30% = 22.14점
- **종합 점수: 74.12점**

---

### 4단계: 직전 일자 대비 변화 계산

```typescript
// 최신 데이터 (latest)
latestScore = calculateCompositeScore(latest)

// 직전 데이터 (previous)
previousScore = calculateCompositeScore(previous)

// 변화량
scoreChange = latestScore - previousScore
scoreChangePercent = (scoreChange / previousScore) × 100
```

**예시:**
- 최신 점수: 75.3점
- 직전 점수: 70.1점
- 변화: +5.2점
- 변화율: (5.2 / 70.1) × 100 = **7.42%**

---

### 5단계: 예측 정확도 계산

**방법:** 고래 거래와 가격 변화의 일치도 측정

```typescript
for (각 시간 포인트 i = 1 to 데이터 길이) {
  current = 데이터[i]
  prev = 데이터[i-1]
  
  // 고래 거래 증가 여부
  whaleIncrease = current.whale_tx_count > prev.whale_tx_count
  
  // 가격 상승 여부
  priceIncrease = current.btc_change > 0 || current.eth_change > 0
  
  // 예측 일치 여부
  if (whaleIncrease === priceIncrease) {
    correctPredictions++
  }
  totalPredictions++
}

predictionAccuracy = (correctPredictions / totalPredictions) × 100
```

**로직:**
- 고래 거래 증가 → 가격 상승 예측
- 실제 가격 변화와 예측이 일치하는 비율 계산

**예시:**
- 총 예측: 100회
- 정확한 예측: 68회
- **예측 정확도: 68%**

---

## 📊 최종 출력 데이터

```typescript
{
  score: 75.3,                    // 종합 점수 (0-100)
  change: 5.2,                    // 직전 대비 변화 (점수)
  changePercent: 7.42,            // 직전 대비 변화율 (%)
  predictionAccuracy: 68.5,       // 예측 정확도 (%)
  calculationLogic: {
    components: [
      { name: '텔레그램 활동', weight: 0.2, score: 72.5 },
      { name: '고래 거래', weight: 0.3, score: 78.2 },
      { name: '트위터 인게이지먼트', weight: 0.2, score: 70.1 },
      { name: '뉴스 감정', weight: 0.3, score: 73.8 }
    ],
    predictionMethod: '고래 거래와 가격 상관관계 기반 예측',
    accuracyMethod: '실제 가격 변화와 예측 비교 (최근 30일)'
  }
}
```

---

## 🎯 점수 해석 가이드

| 점수 범위 | 의미 | 행동 권장 |
|---------|------|---------|
| **75점 이상** | 강한 매수 신호 🚀 | 매수 고려 |
| **60-75점** | 매수 고려 📈 | 관망 후 매수 |
| **40-60점** | 중립 ⚖️ | 관망 |
| **25-40점** | 매도 고려 📉 | 관망 후 매도 |
| **25점 미만** | 강한 매도 신호 ⚠️ | 매도 고려 |

---

## 📝 계산 로직 요약

1. **데이터 조회**: Supabase에서 최근 30일 데이터
2. **정규화**: 각 지표를 0-100점으로 변환
3. **감정 변환**: -1~1 감정을 0~100점으로 변환
4. **가중 평균**: 4개 지표를 가중치로 합산
5. **변화 계산**: 직전 일자와 비교
6. **정확도 계산**: 고래 거래-가격 상관관계 일치도

---

## 🔍 코드 위치

- **API 라우트**: `app/api/composite-score/route.ts`
- **Supabase 함수**: `lib/supabase.ts` → `getCompositeScoreData()`
- **컴포넌트**: `components/CompositeScoreHeader.tsx`

---

**참고:** 현재 테이블에 데이터가 없으면 기본값(75.3점)이 표시됩니다.

