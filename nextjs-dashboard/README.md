# Crypto Signal Dashboard - Next.js

## 🚀 Vercel 배포 방법

### 1. 의존성 설치

```bash
cd nextjs-dashboard
npm install
```

### 2. 로컬 테스트

```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

### 3. Vercel 배포

#### 옵션 A: Vercel CLI 사용

```bash
npm install -g vercel
vercel login
vercel
```

#### 옵션 B: GitHub 연동

1. GitHub에 nextjs-dashboard 폴더 푸시
2. https://vercel.com 로그인
3. "New Project" 클릭
4. GitHub 저장소 선택
5. Root Directory: `nextjs-dashboard` 설정
6. "Deploy" 클릭

### 4. 환경 변수 설정 (필요시)

Vercel 대시보드에서:

- Settings > Environment Variables
- `NODE_ENV=production` 추가

## 📦 프로젝트 구조

```
nextjs-dashboard/
├── app/
│   ├── api/data/route.ts    # 데이터 API
│   ├── layout.tsx           # 루트 레이아웃
│   ├── page.tsx             # 메인 페이지
│   └── globals.css          # 전역 CSS
├── components/
│   ├── CompositeScoreHeader.tsx
│   ├── CompositeScoreChart.tsx
│   ├── UpbitStyleTabs.tsx
│   └── CorrelationIndicators.tsx
├── public/                  # 정적 파일
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
```

## 🎨 주요 기능

- ✅ 업비트 스타일 UI
- ✅ 실시간 차트 (Plotly.js)
- ✅ 종합 점수 헤더
- ✅ 상관관계 지표
- ✅ 반응형 디자인
- ✅ TypeScript 지원

---

## 🗣️ Community Dashboard

커뮤니티 감성 분석 대시보드 (`/community`)

### 📊 주요 컴포넌트

#### 1. SentimentTrend (감성 트렌드)

- **기능**: 시간별 감성 변화와 가격 상관관계 분석
- **차트**: LineChart (감성 점수 + 가격 추이)
- **필터**: 주기(1h/4h/1d), 코인(BTC/ETH), 날짜 범위
- **카드**: 글 수, 평균 감성, 상관계수, 분산, 긍정/부정 비율
- **인터랙션**: 그래프 클릭 시 해당 시점 카드 데이터 업데이트

#### 2. SpikeTimeline (스파이크 분석)

- **기능**: Z-score 기반 감성 급변 탐지
- **차트**: LineChart (Z-score 추이 + 임계값 기준선)
- **필터**: 주기, 코인, 스파이크 임계값, 날짜 범위
- **테이블**: 스파이크 상세 정보 (시간, 감성, 글 수 등)
- **인터랙션**: 그래프/테이블 클릭 → TopPosts 자동 필터링

#### 3. TopPosts (인기 게시글)

- **기능**: 감성별 인기 게시글 목록
- **정렬**: 점수 (댓글×3 + 공유×2 + 좋아요×1)
- **필터**: 감성, 기간, 검색어, 정렬 기준
- **인터랙션**: 스파이크/키워드 선택 시 자동 필터링

#### 4. KeywordAnalysis (키워드 분석)

- **기능**: WordCloud + Sentiment Breakdown 통합 카드
- **WordCloud**: @visx/wordcloud, 감성별 색상 (긍정:녹색, 부정:빨강, 중립:파랑)
- **BarChart**: 키워드별 감성 분포 (Stacked Bar)
- **필터**: 감성, 기간
- **인터랙션**: 키워드 클릭 → BarChart 포커스 + TopPosts 검색

### 🔄 컴포넌트 간 연동 (CommunityContext)

```
SpikeTimeline → (날짜 선택) → TopPosts 자동 필터
KeywordAnalysis → (키워드 클릭) → TopPosts 검색어 설정
```

### 📁 파일 구조

```
components/community/
├── SentimentTrend.tsx    # 감성 트렌드 차트 + 통계 카드
├── SpikeTimeline.tsx     # 스파이크 타임라인 + 상세 테이블
├── TopPosts.tsx          # 인기 게시글 리스트
├── KeywordAnalysis.tsx   # WordCloud + Breakdown 통합
└── (legacy)
    ├── WordCloud.tsx
    └── KeywordBars.tsx

contexts/
└── CommunityContext.tsx  # 컴포넌트 간 상태 공유

app/community/
└── page.tsx              # 커뮤니티 대시보드 페이지

app/api/community/
├── sentiment/route.ts    # 감성 트렌드 API
├── spikes/route.ts       # 스파이크 API
├── top-posts/route.ts    # 인기 게시글 API
├── wordcloud/route.ts    # 키워드 API
└── price/route.ts        # 가격 데이터 API
```

### 🛠️ 사용 라이브러리

- **차트**: recharts (LineChart, BarChart)
- **워드클라우드**: @visx/wordcloud, @visx/scale, @visx/text
- **날짜선택**: react-date-range
- **스타일**: Tailwind CSS (다크 테마)

---

## 📝 개발 노트

- Next.js 14 App Router 사용
- Tailwind CSS로 스타일링
- Plotly.js로 차트 렌더링
- 완전한 SSR/SSG 지원 (Vercel 최적화)
