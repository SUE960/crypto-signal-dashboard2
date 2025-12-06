# 📰 뉴스 리스트 패널 데이터 및 계산 로직

## 🎯 개요

**"지금뉴스"** 탭은 최신 암호화폐 뉴스를 필터링하여 표시합니다.

**API 엔드포인트:** `/api/news/recent?limit=50`

**데이터 소스:** CSV 파일 (`coinness_data2.csv` 또는 `coinness_data2_preprocessed.csv`)

**참고:** 현재는 CSV 파일에서 읽지만, 향후 Supabase 연동 가능

---

## 📊 데이터 구조

### NewsItem 인터페이스

```typescript
interface NewsItem {
  timestamp: string;              // 발행 시간
  title: string;                  // 뉴스 제목
  content: string;                // 뉴스 내용
  link: string;                   // 원문 링크
  sentiment_compound: number;     // 종합 감정 점수 (-1 ~ 1)
  sentiment_positive: number;    // 긍정 감정 비율 (0 ~ 1)
  sentiment_negative: number;    // 부정 감정 비율 (0 ~ 1)
  sentiment_neutral: number;     // 중립 감정 비율 (0 ~ 1)
  has_bitcoin?: boolean;          // 비트코인 관련 여부
  has_ethereum?: boolean;         // 이더리움 관련 여부
  has_bullish?: boolean;          // 강세 뉴스 여부
  has_bearish?: boolean;          // 약세 뉴스 여부
}
```

---

## 🔍 데이터 처리 로직

### 1. CSV 파일 읽기

**파일 경로 우선순위:**
1. `../../data/coinness_data2_preprocessed.csv`
2. `../../data/coinness_data2.csv`
3. `../data/coinness_data2_preprocessed.csv`
4. `../data/coinness_data2.csv`
5. `data/coinness_data2.csv`

**처리:**
- CSV 파싱 (컬럼 자동 인식)
- 빈 줄 제거
- UTF-8 인코딩

### 2. 데이터 필터링 및 정렬

```typescript
// 1. 필수 필드 확인
.filter(record => record.timestamp && record.title)

// 2. 최신순 정렬
.sort((a, b) => {
  const dateA = new Date(a.timestamp).getTime();
  const dateB = new Date(b.timestamp).getTime();
  return dateB - dateA; // 최신순
})

// 3. 개수 제한
.slice(0, limit) // 기본값: 50개
```

### 3. 데이터 변환

```typescript
{
  timestamp: record.timestamp,
  title: record.title,
  content: record.content || '',
  link: record.link || '#',
  sentiment_compound: parseFloat(record.sentiment_compound) || 0,
  sentiment_positive: parseFloat(record.sentiment_positive) || 0,
  sentiment_negative: parseFloat(record.sentiment_negative) || 0,
  sentiment_neutral: parseFloat(record.sentiment_neutral) || 0,
  has_bitcoin: record.has_bitcoin === 'True' || 
               record.has_bitcoin === '1' || 
               (record.title && (
                 record.title.includes('비트코인') || 
                 record.title.includes('BTC')
               )),
  has_ethereum: record.has_ethereum === 'True' || 
                record.has_ethereum === '1' ||
                (record.title && (
                  record.title.includes('이더리움') || 
                  record.title.includes('ETH')
                )),
  has_bullish: record.has_bullish === 'True' || 
               record.has_bullish === '1' ||
               (record.title && (
                 record.title.includes('급등') || 
                 record.title.includes('상승') || 
                 record.title.includes('강세')
               )),
  has_bearish: record.has_bearish === 'True' || 
               record.has_bearish === '1' ||
               (record.title && (
                 record.title.includes('급락') || 
                 record.title.includes('하락') || 
                 record.title.includes('약세')
               ))
}
```

---

## 🎨 필터링 로직

### 필터 종류

1. **전체 (all)** - 모든 뉴스 표시
2. **강세 (bullish)** - `has_bullish === true`인 뉴스만
3. **약세 (bearish)** - `has_bearish === true`인 뉴스만
4. **BTC (bitcoin)** - `has_bitcoin === true`인 뉴스만
5. **ETH (ethereum)** - `has_ethereum === true`인 뉴스만

### 필터링 함수

```typescript
getFilteredNews() {
  let filtered = news;
  
  switch (filter) {
    case 'bullish':
      filtered = news.filter(n => n.has_bullish);
      break;
    case 'bearish':
      filtered = news.filter(n => n.has_bearish);
      break;
    case 'bitcoin':
      filtered = news.filter(n => n.has_bitcoin);
      break;
    case 'ethereum':
      filtered = news.filter(n => n.has_ethereum);
      break;
  }
  
  return filtered.slice(0, displayCount); // 기본 10개
}
```

### 필터 카운트

각 필터 버튼에 표시되는 개수:

```typescript
전체: news.length
강세: news.filter(n => n.has_bullish).length
약세: news.filter(n => n.has_bearish).length
BTC: news.filter(n => n.has_bitcoin).length
ETH: news.filter(n => n.has_ethereum).length
```

---

## 📊 감정 분석 표시

### 1. 감정 점수 색상

```typescript
getSentimentColor(compound: number) {
  if (compound > 0.3) return 'text-green-400 bg-green-900/20 border-green-600';  // 긍정
  if (compound < -0.3) return 'text-red-400 bg-red-900/20 border-red-600';      // 부정
  return 'text-gray-400 bg-gray-900/20 border-gray-600';                          // 중립
}
```

**표시:**
- **초록색**: compound > 0.3 (긍정)
- **빨간색**: compound < -0.3 (부정)
- **회색**: 그 외 (중립)

### 2. 감정 이모지

```typescript
getSentimentEmoji(compound: number) {
  if (compound > 0.5) return '🚀';   // 매우 긍정
  if (compound > 0.2) return '📈';   // 긍정
  if (compound < -0.5) return '📉';  // 매우 부정
  if (compound < -0.2) return '⚠️';  // 부정
  return '📊';                        // 중립
}
```

### 3. 감정 점수 표시

```typescript
// 종합 감정 점수
{(item.sentiment_compound * 100).toFixed(0)}

// 긍정 감정 비율
😊 {(item.sentiment_positive * 100).toFixed(0)}%

// 부정 감정 비율
😔 {(item.sentiment_negative * 100).toFixed(0)}%
```

**예시:**
- compound: 0.75 → **🚀 75**
- positive: 0.6 → **😊 60%**
- negative: 0.0 → **😔 0%**

---

## ⏰ 시간 표시 로직

### 상대 시간 계산

```typescript
getTimeAgo(timestamp: string) {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return '방금 전';
  if (diffMins < 60) return `${diffMins}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  return `${diffDays}일 전`;
}
```

**표시 예시:**
- 30초 전 → "방금 전"
- 15분 전 → "15분 전"
- 3시간 전 → "3시간 전"
- 5일 전 → "5일 전"

---

## 🏷️ 태그 표시 로직

### 태그 종류

1. **BTC 태그**
   - 조건: `has_bitcoin === true`
   - 색상: 주황색 (orange)
   - 표시: "BTC"

2. **ETH 태그**
   - 조건: `has_ethereum === true`
   - 색상: 파란색 (blue)
   - 표시: "ETH"

3. **강세 태그**
   - 조건: `has_bullish === true`
   - 색상: 초록색 (green)
   - 표시: "강세"

4. **약세 태그**
   - 조건: `has_bearish === true`
   - 색상: 빨간색 (red)
   - 표시: "약세"

### 태그 표시 조건

```typescript
{item.has_bitcoin && (
  <span className="px-2 py-0.5 bg-orange-900/30 text-orange-400 text-xs rounded border border-orange-700">
    BTC
  </span>
)}
```

---

## 📋 필터 카운트 계산

각 필터 버튼에 표시되는 개수는 **전체 뉴스 배열**에서 계산됩니다:

```typescript
전체: {news.length}
강세: {news.filter(n => n.has_bullish).length}
약세: {news.filter(n => n.has_bearish).length}
BTC: {news.filter(n => n.has_bitcoin).length}
ETH: {news.filter(n => n.has_ethereum).length}
```

**예시:**
- 전체 뉴스: 50개
- 강세 뉴스: 5개
- 약세 뉴스: 5개
- BTC 관련: 17개
- ETH 관련: 4개

---

## 🔄 데이터 흐름

```
CSV 파일 (coinness_data2.csv)
    ↓
API: /api/news/recent?limit=50
    ├─ CSV 파싱
    ├─ 최신순 정렬
    ├─ 데이터 변환
    └─ 필터링 정보 추가
    ↓
NewsListPanel Component
    ├─ 필터 적용
    ├─ 감정 분석 표시
    ├─ 시간 포맷팅
    └─ 태그 표시
    ↓
사용자 화면
```

---

## 📊 사용되는 데이터 필드

### CSV에서 읽는 필드

| 필드명 | 타입 | 용도 |
|--------|------|------|
| `timestamp` | string | 발행 시간 |
| `title` | string | 뉴스 제목 |
| `content` | string | 뉴스 내용 |
| `link` | string | 원문 링크 |
| `sentiment_compound` | number | 종합 감정 점수 |
| `sentiment_positive` | number | 긍정 감정 비율 |
| `sentiment_negative` | number | 부정 감정 비율 |
| `sentiment_neutral` | number | 중립 감정 비율 |
| `has_bitcoin` | boolean/string | BTC 관련 여부 |
| `has_ethereum` | boolean/string | ETH 관련 여부 |
| `has_bullish` | boolean/string | 강세 여부 |
| `has_bearish` | boolean/string | 약세 여부 |

### 계산/추론되는 필드

- `has_bitcoin`: CSV 값 또는 제목에서 "비트코인", "BTC" 포함 여부
- `has_ethereum`: CSV 값 또는 제목에서 "이더리움", "ETH" 포함 여부
- `has_bullish`: CSV 값 또는 제목에서 "급등", "상승", "강세" 포함 여부
- `has_bearish`: CSV 값 또는 제목에서 "급락", "하락", "약세" 포함 여부

---

## 🎯 표시 예시

### 뉴스 카드 구조

```
┌─────────────────────────────────────────┐
│ [제목]                    [감정 점수]   │
│ [태그들]                  😊 60%       │
│ 5일 전                      😔 0%       │
│ [자세히 보기 →]                        │
└─────────────────────────────────────────┘
```

### 필터 버튼

```
[전체 (50)] [🚀 강세 (5)] [📉 약세 (5)] [₿ BTC (17)] [Ξ ETH (4)]
```

---

## 📝 더보기 기능

### 초기 표시 개수
```typescript
displayCount = 10  // 기본값
```

### 더보기 버튼
```typescript
if (displayCount < news.length) {
  // "더 보기 (40개 더)" 버튼 표시
  // 클릭 시 displayCount += 10
}
```

---

## 🔄 새로고침 기능

```typescript
loadNews() {
  // API 재호출
  fetch('/api/news/recent?limit=50')
    .then(res => res.json())
    .then(data => setNews(data))
}
```

**동작:**
- "새로운 뉴스 불러오기" 버튼 클릭
- API 재호출하여 최신 뉴스 가져오기
- 필터 카운트 자동 업데이트

---

## ⚠️ 주의사항

1. **CSV 파일 의존성**
   - 현재는 CSV 파일에서 읽음
   - 파일이 없으면 빈 배열 반환
   - API 실패 시 더미 데이터 표시

2. **필터 카운트**
   - 필터 버튼의 개수는 **전체 뉴스** 기준
   - 필터 적용 후 표시되는 개수와 다를 수 있음

3. **감정 분석**
   - CSV 파일에 감정 분석 결과가 있어야 함
   - 없으면 기본값 0 사용

---

## 📊 요약

| 항목 | 값 | 설명 |
|------|-----|------|
| **데이터 소스** | CSV 파일 | `coinness_data2.csv` |
| **API 엔드포인트** | `/api/news/recent` | 최대 50개 |
| **정렬** | 최신순 | timestamp 기준 내림차순 |
| **필터 종류** | 5개 | 전체, 강세, 약세, BTC, ETH |
| **초기 표시** | 10개 | 더보기로 추가 가능 |
| **감정 표시** | 3가지 | 종합, 긍정, 부정 |
| **시간 표시** | 상대 시간 | "N일 전", "N시간 전" |

---

## 🔍 코드 위치

- **API 라우트**: `app/api/news/recent/route.ts`
- **컴포넌트**: `components/NewsListPanel.tsx`
- **사용 위치**: `app/page.tsx` (HOME 페이지)

---

## 💡 향후 개선 가능 사항

1. **Supabase 연동**
   - 뉴스 데이터를 Supabase 테이블에 저장
   - 실시간 뉴스 업데이트

2. **감정 분석 개선**
   - 실시간 감정 분석
   - 더 정확한 강세/약세 판단

3. **필터 개선**
   - 날짜 범위 필터
   - 키워드 검색
   - 다중 필터 조합

---

**참고:** 현재는 CSV 파일에서 읽지만, 향후 Supabase로 마이그레이션 가능합니다.

