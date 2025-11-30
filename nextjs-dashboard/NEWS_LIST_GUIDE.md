# 뉴스 리스트 패널 가이드

## 📰 NewsListPanel 컴포넌트

### 기능
- 최근 코인뉴스 리스트 표시
- 필터링 (전체/강세/약세/BTC/ETH)
- 감정 분석 점수 표시
- 실시간 업데이트
- 무한 스크롤 (더보기)

---

## 🎨 UI 구성

### 1. 필터 버튼 (5개)
- **전체**: 모든 뉴스
- **🚀 강세**: 강세 뉴스만
- **📉 약세**: 약세 뉴스만  
- **₿ BTC**: 비트코인 관련
- **Ξ ETH**: 이더리움 관련

### 2. 뉴스 카드
각 카드에는:
- **제목**: 뉴스 헤드라인
- **태그**: BTC/ETH/강세/약세
- **시간**: "5분 전", "2시간 전" 등
- **감정 점수**: 이모지 + 점수
- **상세 감정**: 긍정%/부정%

### 3. 감정 점수 색상
- 🚀 **초록색** (> 0.3): 매우 긍정적
- 📈 **연한 초록** (> 0): 긍정적
- 📊 **회색** (-0.3 ~ 0.3): 중립
- ⚠️ **주황색** (< 0): 부정적
- 📉 **빨강색** (< -0.3): 매우 부정적

---

## 🚀 사용 방법

### 1. 컴포넌트 통합
```typescript
import NewsListPanel from '@/components/NewsListPanel';

// "지금 뉴스" 탭에 추가
<NewsListPanel />
```

### 2. API 라우트 생성 (선택사항)
실제 데이터를 사용하려면:

```typescript
// app/api/news/recent/route.ts
// API_NEWS_ROUTE.ts 파일 내용 사용
```

---

## 📊 데이터 구조

```typescript
interface NewsItem {
  timestamp: string;           // 뉴스 발행 시간
  title: string;              // 제목
  content: string;            // 내용
  link: string;               // 원문 링크
  sentiment_compound: number; // 종합 감정 (-1 ~ 1)
  sentiment_positive: number; // 긍정 (0 ~ 1)
  sentiment_negative: number; // 부정 (0 ~ 1)
  sentiment_neutral: number;  // 중립 (0 ~ 1)
  has_bitcoin?: boolean;      // BTC 관련 여부
  has_ethereum?: boolean;     // ETH 관련 여부
  has_bullish?: boolean;      // 강세 뉴스 여부
  has_bearish?: boolean;      // 약세 뉴스 여부
}
```

---

## 🎯 주요 기능

### 1. 시간 표시
```typescript
"방금 전"      // < 1분
"5분 전"       // < 1시간
"2시간 전"     // < 24시간
"3일 전"       // >= 24시간
```

### 2. 감정 이모지
```typescript
compound > 0.5  → 🚀 (로켓)
compound > 0.2  → 📈 (상승)
compound < -0.5 → 📉 (하락)
compound < -0.2 → ⚠️ (경고)
기타            → 📊 (차트)
```

### 3. 클릭 동작
뉴스 카드 클릭 시 → 새 탭에서 원문 열기

---

## 📱 반응형

- **데스크톱**: 카드 형태
- **모바일**: 세로 스택
- 호버 효과: 색상 변화 + "자세히 보기"

---

## 🔄 실시간 업데이트

```typescript
// 5분마다 자동 새로고침 (선택사항)
useEffect(() => {
  const interval = setInterval(() => {
    loadNews();
  }, 300000); // 5분

  return () => clearInterval(interval);
}, []);
```

---

## 💡 커스터마이징

### 초기 표시 개수 변경
```typescript
const [displayCount, setDisplayCount] = useState(20); // 10 → 20
```

### 필터 추가
```typescript
// 규제 관련 뉴스 필터 추가 예시
<button onClick={() => setFilter('regulation')}>
  ⚖️ 규제 ({news.filter(n => n.has_regulation).length})
</button>
```

---

## 🎨 스타일링

### 색상 테마
- **배경**: gray-900
- **테두리**: gray-800
- **텍스트**: white/gray-400
- **강조**: blue-400 (호버)

### 감정 색상
- 긍정: green-400
- 부정: red-400
- 중립: gray-400

---

## 📊 통계 표시 (선택사항)

```typescript
// 통계 헤더 추가 예시
<div className="grid grid-cols-3 gap-4 mb-4">
  <div className="bg-gray-900 p-4 rounded-lg">
    <div className="text-gray-400 text-sm">총 뉴스</div>
    <div className="text-white text-2xl font-bold">{news.length}</div>
  </div>
  <div className="bg-green-900/20 p-4 rounded-lg">
    <div className="text-green-400 text-sm">강세 뉴스</div>
    <div className="text-white text-2xl font-bold">
      {news.filter(n => n.has_bullish).length}
    </div>
  </div>
  <div className="bg-red-900/20 p-4 rounded-lg">
    <div className="text-red-400 text-sm">약세 뉴스</div>
    <div className="text-white text-2xl font-bold">
      {news.filter(n => n.has_bearish).length}
    </div>
  </div>
</div>
```

---

## 🚀 완료!

"지금 뉴스" 탭에 최근 코인뉴스가 실시간으로 표시됩니다!

### 특징
- ✅ 감정 분석 점수
- ✅ BTC/ETH 태그
- ✅ 시간 표시
- ✅ 필터링
- ✅ 무한 스크롤
- ✅ 클릭 시 원문

