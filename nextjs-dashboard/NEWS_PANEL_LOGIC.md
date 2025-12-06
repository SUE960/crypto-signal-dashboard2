# 📰 뉴스 리스트 패널 데이터 및 계산 로직

## 🎯 개요

**"지금뉴스"** 탭은 최신 암호화폐 뉴스를 표시하며, 감정 분석과 필터링 기능을 제공합니다.

**데이터 소스:** CSV 파일 (`coinness_data2.csv` 또는 `coinness_data2_preprocessed.csv`)

**참고:** 현재 Supabase와 연동되지 않음. 향후 Supabase 연동 가능

---

## 📡 데이터 소스

### API 엔드포인트
`/api/news/recent?limit=50`

### 데이터 파일 경로 (우선순위 순)
1. `../../data/coinness_data2_preprocessed.csv`
2. `../../data/coinness_data2.csv`
3. `../data/coinness_data2_preprocessed.csv`
4. `../data/coinness_data2.csv`
5. `data/coinness_data2.csv`

### CSV 파일 구조

**필수 컬럼:**
- `timestamp` - 뉴스 발행 시간
- `title` - 뉴스 제목
- `content` - 뉴스 내용 (선택)
- `link` - 뉴스 링크 (선택)

**감정 분석 컬럼:**
- `sentiment_compound` - 종합 감정 점수 (-1 ~ 1)
- `sentiment_positive` - 긍정 감정 비율 (0 ~ 1)
- `sentiment_negative` - 부정 감정 비율 (0 ~ 1)
- `sentiment_neutral` - 중립 감정 비율 (0 ~ 1)

**태그 컬럼:**
- `has_bitcoin` - 비트코인 관련 여부 (True/False 또는 1/0)
- `has_ethereum` - 이더리움 관련 여부 (True/False 또는 1/0)
- `has_bullish` - 강세 뉴스 여부 (True/False 또는 1/0)
- `has_bearish` - 약세 뉴스 여부 (True/False 또는 1/0)

---

## 🔄 데이터 처리 로직

### 1. CSV 파일 읽기

```typescript
// CSV 파일 찾기
const possiblePaths = [
  '../../data/coinness_data2_preprocessed.csv',
  '../../data/coinness_data2.csv',
  // ... 기타 경로
];

// 파일 읽기
const fileContent = fs.readFileSync(dataPath, 'utf-8');
const records = parse(fileContent, {
  columns: true,
  skip_empty_lines: true,
  encoding: 'utf-8'
});
```

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
.map(record => ({
  timestamp: record.timestamp,
  title: record.title,
  content: record.content || '',
  link: record.link || '#',
  
  // 감정 분석
  sentiment_compound: parseFloat(record.sentiment_compound) || 0,
  sentiment_positive: parseFloat(record.sentiment_positive) || 0,
  sentiment_negative: parseFloat(record.sentiment_negative) || 0,
  sentiment_neutral: parseFloat(record.sentiment_neutral) || 0,
  
  // 태그 판단 (다중 조건)
  has_bitcoin: 
    record.has_bitcoin === 'True' || 
    record.has_bitcoin === '1' || 
    (record.title && (
      record.title.includes('비트코인') || 
      record.title.includes('BTC')
    )),
    
  has_ethereum: 
    record.has_ethereum === 'True' || 
    record.has_ethereum === '1' ||
    (record.title && (
      record.title.includes('이더리움') || 
      record.title.includes('ETH')
    )),
    
  has_bullish: 
    record.has_bullish === 'True' || 
    record.has_bullish === '1' ||
    (record.title && (
      record.title.includes('급등') || 
      record.title.includes('상승') || 
      record.title.includes('강세')
    )),
    
  has_bearish: 
    record.has_bearish === 'True' || 
    record.has_bearish === '1' ||
    (record.title && (
      record.title.includes('급락') || 
      record.title.includes('하락') || 
      record.title.includes('약세')
    ))
}))
```

---

## 🎨 필터링 로직

### 필터 종류

1. **전체** (`all`) - 모든 뉴스 표시
2. **강세** (`bullish`) - `has_bullish === true`인 뉴스만
3. **약세** (`bearish`) - `has_bearish === true`인 뉴스만
4. **BTC** (`bitcoin`) - `has_bitcoin === true`인 뉴스만
5. **ETH** (`ethereum`) - `has_ethereum === true`인 뉴스만

### 필터링 함수

```typescript
const getFilteredNews = () => {
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
  
  return filtered.slice(0, displayCount); // 기본값: 10개
};
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
- **초록색**: `compound > 0.3` (강세)
- **빨간색**: `compound < -0.3` (약세)
- **회색**: 그 외 (중립)

### 2. 감정 이모지

```typescript
getSentimentEmoji(compound: number) {
  if (compound > 0.5) return '🚀';  // 매우 긍정
  if (compound > 0.2) return '📈';  // 긍정
  if (compound < -0.5) return '📉'; // 매우 부정
  if (compound < -0.2) return '⚠️';  // 부정
  return '📊';                        // 중립
}
```

### 3. 감정 점수 표시

```typescript
// 종합 감정 점수
(sentiment_compound * 100).toFixed(0)  // 예: 75, -45

// 긍정/부정 비율
(sentiment_positive * 100).toFixed(0)  // 예: 60%
(sentiment_negative * 100).toFixed(0)  // 예: 20%
```

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

### 태그 조건

```typescript
// BTC 태그
{item.has_bitcoin && (
  <span className="bg-orange-900/30 text-orange-400">
    BTC
  </span>
)}

// ETH 태그
{item.has_ethereum && (
  <span className="bg-blue-900/30 text-blue-400">
    ETH
  </span>
)}

// 강세 태그
{item.has_bullish && (
  <span className="bg-green-900/30 text-green-400">
    강세
  </span>
)}

// 약세 태그
{item.has_bearish && (
  <span className="bg-red-900/30 text-red-400">
    약세
  </span>
)}
```

---

## 📋 데이터 구조

### NewsItem 인터페이스

```typescript
interface NewsItem {
  timestamp: string;              // 발행 시간
  title: string;                  // 제목
  content: string;                // 내용
  link: string;                   // 링크
  sentiment_compound: number;     // 종합 감정 (-1 ~ 1)
  sentiment_positive: number;     // 긍정 비율 (0 ~ 1)
  sentiment_negative: number;     // 부정 비율 (0 ~ 1)
  sentiment_neutral: number;      // 중립 비율 (0 ~ 1)
  has_bitcoin?: boolean;           // BTC 관련 여부
  has_ethereum?: boolean;          // ETH 관련 여부
  has_bullish?: boolean;           // 강세 여부
  has_bearish?: boolean;           // 약세 여부
}
```

---

## 🔍 필터별 데이터 예시

### 전체 필터
- 모든 뉴스 표시
- 기본값: 최신 10개

### 강세 필터
- `has_bullish === true`인 뉴스만
- 제목에 "급등", "상승", "강세" 포함
- 또는 CSV의 `has_bullish` 컬럼이 True/1

### 약세 필터
- `has_bearish === true`인 뉴스만
- 제목에 "급락", "하락", "약세" 포함
- 또는 CSV의 `has_bearish` 컬럼이 True/1

### BTC 필터
- `has_bitcoin === true`인 뉴스만
- 제목에 "비트코인", "BTC" 포함
- 또는 CSV의 `has_bitcoin` 컬럼이 True/1

### ETH 필터
- `has_ethereum === true`인 뉴스만
- 제목에 "이더리움", "ETH" 포함
- 또는 CSV의 `has_ethereum` 컬럼이 True/1

---

## 📊 표시 예시

### 뉴스 카드 구조

```
┌─────────────────────────────────────────┐
│ [제목]                    [감정 점수]   │
│ [태그들]                  😊 60%       │
│ [시간]                    😔 20%       │
│ [자세히 보기 →]                         │
└─────────────────────────────────────────┘
```

### 감정 점수 표시

- **🚀 75**: 매우 긍정 (compound > 0.5)
- **📈 35**: 긍정 (0.2 < compound <= 0.5)
- **📊 5**: 중립 (-0.2 <= compound <= 0.2)
- **⚠️ -25**: 부정 (-0.5 < compound <= -0.2)
- **📉 -65**: 매우 부정 (compound <= -0.5)

---

## 🔄 데이터 흐름

```
CSV 파일 (coinness_data2.csv)
    ↓
API: /api/news/recent
    ├─ 파일 읽기
    ├─ 필터링 (timestamp, title 존재)
    ├─ 정렬 (최신순)
    ├─ 데이터 변환
    └─ JSON 반환
    ↓
NewsListPanel Component
    ├─ 필터링 (전체/강세/약세/BTC/ETH)
    ├─ 감정 분석 표시
    ├─ 태그 표시
    └─ 시간 표시
    ↓
사용자 화면
```

---

## ⚠️ 현재 상태

### 데이터 소스
- ✅ CSV 파일에서 읽기
- ❌ Supabase와 연동되지 않음

### 향후 개선 가능
1. **Supabase 연동**
   - 뉴스 데이터를 Supabase 테이블에 저장
   - 실시간 뉴스 업데이트
   - 감정 분석 결과 저장

2. **실시간 업데이트**
   - WebSocket 또는 Polling으로 새 뉴스 자동 로드
   - 새로고침 버튼 없이 자동 업데이트

3. **고급 필터링**
   - 날짜 범위 선택
   - 감정 점수 범위 필터
   - 키워드 검색

---

## 📝 요약

| 항목 | 값 | 설명 |
|------|-----|------|
| **데이터 소스** | CSV 파일 | `coinness_data2.csv` |
| **API 엔드포인트** | `/api/news/recent` | 최신 뉴스 조회 |
| **기본 개수** | 50개 | 최신순 정렬 |
| **표시 개수** | 10개 (기본) | 더보기로 증가 가능 |
| **필터 종류** | 5개 | 전체/강세/약세/BTC/ETH |
| **감정 분석** | 4가지 | compound, positive, negative, neutral |
| **태그 판단** | 다중 조건 | CSV 컬럼 + 제목 키워드 |

---

## 🔍 코드 위치

- **API 라우트**: `app/api/news/recent/route.ts`
- **컴포넌트**: `components/NewsListPanel.tsx`
- **사용 위치**: `app/page.tsx` (HOME 페이지 - "지금뉴스" 탭)

---

**참고:** 현재 CSV 파일이 없으면 더미 데이터가 표시됩니다. Supabase 연동 시 실시간 뉴스 데이터를 제공할 수 있습니다.

