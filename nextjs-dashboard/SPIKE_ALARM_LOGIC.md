# ⚠️ Spike 알람 리스트 로직

## 🎯 개요

**Spike 알람 리스트**는 이상치를 감지하여 구매 시점을 알려주는 알람 시스템입니다.

**데이터 소스:** Supabase `final_integrated_data` 테이블

**API 엔드포인트:** `/api/spike-points?range={7d|30d|90d}`

---

## 🔍 Spike 감지 로직

### 1. 데이터 조회

**소스:** Supabase `final_integrated_data` 테이블
**기간:** 선택된 범위 (7일, 30일, 90일)

**조회 데이터:**
- `whale_tx_count` - 고래 거래 건수
- `telegram_message_count` - 텔레그램 메시지 수
- `twitter_engagement` - 트위터 인게이지먼트
- `news_count` - 뉴스 개수
- `btc_price_change`, `eth_price_change` - 가격 변화율
- 기타 감정 및 가격 데이터

---

### 2. Z-score 계산

**Z-score란?**
통계적 이상치를 감지하는 방법. 평균으로부터 몇 표준편차 떨어져 있는지 측정.

**계산 공식:**
```
Z-score = (현재값 - 평균) / 표준편차
```

**윈도우:** 최근 24시간 데이터 사용

**계산 함수:**
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

**각 지표의 Z-score:**
1. 고래 거래 Z-score: `calculateZScore(whale_tx_count 배열)`
2. 텔레그램 Z-score: `calculateZScore(telegram_message_count 배열)`
3. 트위터 Z-score: `calculateZScore(twitter_engagement 배열)`
4. 뉴스 Z-score: `calculateZScore(news_count 배열)`

---

### 3. Spike 감지 (임계값)

**임계값:** `threshold = 2.0`

Z-score가 2.0 이상이면 이상치로 판단합니다.

**의미:**
- Z-score 2.0 = 평균보다 2 표준편차 이상 높음
- 통계적으로 약 2.3% 확률로 발생하는 이상치

---

### 4. 우선순위 점수 계산

각 시간 포인트마다 다음 규칙으로 점수를 계산합니다:

#### 개별 스파이크 (기본 점수)

| 지표 | 조건 | 점수 |
|------|------|------|
| 고래 거래 | Z-score > 2.0 | **+3점** |
| 텔레그램 | Z-score > 2.0 | **+2점** |
| 트위터 | Z-score > 2.0 | **+2점** |
| 뉴스 | Z-score > 2.0 | **+2점** |

#### 복합 스파이크 보너스

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

#### 가격 급변 보너스

```typescript
if (|btc_change| > 2% || |eth_change| > 2%) {
  priorityScore += 2점
  이유: "가격 급변 (BTC X%, ETH Y%)"
}
```

---

### 5. 알람 레벨 결정

```typescript
if (priorityScore >= 5) {
  alertLevel = 
    priorityScore >= 10 ? 'CRITICAL' :  // 매우 위험
    priorityScore >= 7 ? 'HIGH' :        // 높음
    'MEDIUM'                             // 중간
}
```

**알람 레벨:**
- **CRITICAL**: 우선순위 점수 >= 10점
- **HIGH**: 우선순위 점수 >= 7점
- **MEDIUM**: 우선순위 점수 >= 5점

---

### 6. Spike 포인트 생성 조건

**조건:** `priorityScore >= 5`

이 조건을 만족하는 경우만 Spike 알람으로 표시됩니다.

---

## 📊 Spike 포인트 데이터 구조

```typescript
interface SpikeAlarm {
  timestamp: string;              // 타임스탬프
  date: string;                  // 포맷팅된 날짜
  priorityScore: number;         // 우선순위 점수
  alertLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  reasons: string[];             // 스파이크 발생 이유 배열
  details: {
    whale_zscore?: number;       // 고래 거래 Z-score
    telegram_zscore?: number;    // 텔레그램 Z-score
    twitter_zscore?: number;     // 트위터 Z-score
    news_zscore?: number;        // 뉴스 Z-score
    btc_price: number;          // BTC 가격
    eth_price: number;          // ETH 가격
    telegram_sentiment: number;  // 텔레그램 감정
    twitter_sentiment: number;   // 트위터 감정
    news_sentiment: number;      // 뉴스 감정
    price_change?: {             // 가격 변화
      btc: number,
      eth: number
    }
  }
}
```

---

## 🎨 UI 표시 로직

### 1. 알람 레벨별 색상

```typescript
getAlertLevelColor(level: string) {
  switch (level) {
    case 'CRITICAL': return 'bg-red-500 text-white';    // 빨간색
    case 'HIGH': return 'bg-orange-500 text-white';      // 주황색
    case 'MEDIUM': return 'bg-yellow-500 text-black';     // 노란색
    default: return 'bg-gray-500 text-white';
  }
}
```

### 2. 필터링

```typescript
filter: 'all' | 'critical' | 'high' | 'medium'

filteredSpikes = spikes.filter((spike) => {
  if (filter === 'all') return true;
  return spike.alertLevel === filter.toUpperCase();
});
```

### 3. 날짜 포맷팅

```typescript
formatDate(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleDateString('ko-KR', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
```

**예시:**
- "11. 9. 오전 05시 30분"
- "11. 12. 오후 02시 15분"

---

## 📈 계산 예시

### 예시 1: 단일 스파이크

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
- 알람 레벨: **MEDIUM** (3점 < 5점이므로 표시 안됨)

---

### 예시 2: 복합 스파이크 (표시됨)

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
- 우선순위 점수: **19점**
- 알람 레벨: **CRITICAL**
- 표시: ✅ (19점 >= 5점)
- 이유:
  - "고래 거래 급증 (z=2.50)"
  - "텔레그램 활동 급증 (z=2.30)"
  - "트위터 인게이지먼트 급증 (z=2.10)"
  - "🚨 3개 소스 모두 급증 (CRITICAL)"
  - "가격 급변 (BTC 3.50%, ETH 0.00%)"

---

### 예시 3: Spike 없음

**상황:**
- 모든 지표의 Z-score < 2.0
- 가격 변화 < 2%

**결과:**
- 우선순위 점수: 0점
- 표시: ❌ (0점 < 5점)
- 화면: "Spike 알람 없음" 메시지 표시

---

## 🔄 데이터 흐름

```
Supabase (final_integrated_data)
    ↓
API: /api/spike-points
    ├─ 데이터 조회
    ├─ Z-score 계산 (24시간 윈도우)
    ├─ Spike 감지 (Z > 2.0)
    ├─ 우선순위 점수 계산
    ├─ 알람 레벨 결정
    └─ 필터링 (점수 >= 5)
    ↓
SpikeAlarmList Component
    ├─ 필터링 (all/critical/high/medium)
    ├─ 날짜 포맷팅
    ├─ 알람 레벨별 색상
    └─ UI 렌더링
    ↓
사용자 화면
```

---

## 📊 사용되는 모든 데이터 필드

### Z-score 계산용

| 필드명 | 용도 | 윈도우 |
|--------|------|--------|
| `whale_tx_count` | 고래 거래 Z-score | 24시간 |
| `telegram_message_count` | 텔레그램 Z-score | 24시간 |
| `twitter_engagement` | 트위터 Z-score | 24시간 |
| `news_count` | 뉴스 Z-score | 24시간 |

### 가격 급변 감지용

| 필드명 | 용도 | 임계값 |
|--------|------|--------|
| `btc_price_change` | BTC 가격 급변 | ±2% |
| `eth_price_change` | ETH 가격 급변 | ±2% |

### 상세 정보용

| 필드명 | 용도 |
|--------|------|
| `btc_close` | BTC 가격 |
| `eth_close` | ETH 가격 |
| `telegram_avg_sentiment` | 텔레그램 감정 |
| `twitter_sentiment` | 트위터 감정 |
| `news_sentiment_avg` | 뉴스 감정 |

---

## 🎯 우선순위 점수 계산 요약

### 점수 체계

| 조건 | 점수 | 설명 |
|------|------|------|
| 고래 거래 스파이크 | +3 | 가장 중요 |
| 텔레그램 스파이크 | +2 | 커뮤니티 활동 |
| 트위터 스파이크 | +2 | SNS 활동 |
| 뉴스 스파이크 | +2 | 뉴스 급증 |
| 텔레그램+고래 동시 | +5 | 복합 보너스 |
| 트위터+고래 동시 | +4 | 복합 보너스 |
| 3개 소스 모두 | +10 | 최고 위험 |
| 가격 급변 | +2 | 시장 변동 |

### 최대 점수

이론적 최대 점수:
```
3 (고래) + 2 (텔레그램) + 2 (트위터) + 2 (뉴스) + 
10 (3개 소스 모두) + 2 (가격 급변) = 21점
```

---

## 🔍 필터링 로직

### 필터 종류

1. **전체** (`all`) - 모든 알람 표시
2. **CRITICAL** (`critical`) - 우선순위 >= 10점
3. **HIGH** (`high`) - 우선순위 >= 7점
4. **MEDIUM** (`medium`) - 우선순위 >= 5점

### 필터링 함수

```typescript
const filteredSpikes = spikes.filter((spike) => {
  if (filter === 'all') return true;
  return spike.alertLevel === filter.toUpperCase();
});
```

---

## 📝 표시 예시

### Spike 알람 카드 구조

```
┌─────────────────────────────────────────┐
│ [날짜/시간]              [알람 레벨]     │
│ [우선순위 점수]                          │
│ [스파이크 발생 이유들]                   │
│ - 고래 거래 급증 (z=2.50)               │
│ - 텔레그램 활동 급증 (z=2.30)           │
│ - 🚨 3개 소스 모두 급증 (CRITICAL)      │
│ [상세 정보]                              │
└─────────────────────────────────────────┘
```

### 알람 레벨별 표시

- **CRITICAL** (빨간색): 우선순위 >= 10점
- **HIGH** (주황색): 우선순위 >= 7점
- **MEDIUM** (노란색): 우선순위 >= 5점

---

## ⚠️ "Spike 알람 없음" 표시 조건

다음 조건일 때 "Spike 알람 없음" 메시지가 표시됩니다:

1. **데이터 없음**
   - Supabase 테이블에 데이터가 없음
   - API에서 빈 배열 반환

2. **Spike 감지 안됨**
   - 모든 지표의 Z-score < 2.0
   - 우선순위 점수 < 5점

3. **필터링 결과 없음**
   - 선택한 필터에 해당하는 알람이 없음

---

## 📊 계산 로직 요약

### 1단계: 데이터 조회
- Supabase에서 선택된 기간 데이터 조회

### 2단계: Z-score 계산
- 각 지표별 24시간 윈도우로 Z-score 계산
- 임계값 2.0 이상이면 스파이크로 판단

### 3단계: 우선순위 점수 계산
- 개별 스파이크 점수 합산
- 복합 스파이크 보너스 추가
- 가격 급변 보너스 추가

### 4단계: 알람 생성
- 우선순위 점수 >= 5점인 경우만 생성
- 알람 레벨 결정 (CRITICAL/HIGH/MEDIUM)

### 5단계: 필터링 및 표시
- 선택된 필터에 따라 필터링
- 날짜 포맷팅 및 UI 렌더링

---

## 🔍 코드 위치

- **API 라우트**: `app/api/spike-points/route.ts`
- **Supabase 함수**: `lib/supabase.ts` → `getSpikeDetectionData()`
- **컴포넌트**: `components/SpikeAlarmList.tsx`
- **사용 위치**: `app/page.tsx` (HOME 페이지 - "spike 알람" 탭)

---

## 📝 요약

| 항목 | 값 | 설명 |
|------|-----|------|
| **데이터 소스** | Supabase | `final_integrated_data` 테이블 |
| **감지 방법** | Z-score | 24시간 윈도우 |
| **임계값** | 2.0 | Z-score 기준 |
| **표시 조건** | >= 5점 | 우선순위 점수 |
| **알람 레벨** | 3단계 | CRITICAL/HIGH/MEDIUM |
| **필터 종류** | 4개 | 전체/CRITICAL/HIGH/MEDIUM |

---

**참고:** 현재 테이블에 데이터가 없거나 Spike가 감지되지 않으면 "Spike 알람 없음" 메시지가 표시됩니다.

