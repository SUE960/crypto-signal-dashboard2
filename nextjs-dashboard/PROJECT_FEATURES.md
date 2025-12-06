# Crypto Signal Dashboard - 전체 기능 목록

## 프로젝트 개요

**Crypto Signal Dashboard**는 실시간 암호화폐 시장 신호를 분석하고 시각화하는 종합 대시보드입니다.

---

## HOME 페이지 (`/`)

### 1. 종합 점수 헤더 (CompositeScoreHeader)

**기능:**
- 4가지 지표를 가중 평균한 종합 점수 표시
- 점수 변화량 및 변화율 표시
- 예측 정확도 표시

**계산 지표:**
- 텔레그램 활동 점수 (20%)
- 고래 거래 점수 (30%)
- 트위터 인게이지먼트 점수 (20%)
- 뉴스 감정 점수 (30%)

**데이터 소스:** Supabase `final_integrated_data` 테이블

---

### 2. 실시간 차트 (RealTimeChart)

**기능:**
- 고래 거래 건수 시계열 차트
- BTC/ETH 가격 추이
- Spike 포인트 마커 표시
- 시간 범위 필터 (7일/30일/90일)
- 코인 선택 필터 (BTC/ETH/Both)
- 드래그로 날짜 범위 선택

**데이터 소스:** Supabase `final_integrated_data` 테이블

---

### 3. 통계 카드 (Stats Cards)

**표시 항목:**
- 평균 고래 거래 (건)
- BTC 평균 가격 ($K)
- BTC 평균 변화 (%)
- ETH 평균 가격 ($)
- ETH 평균 변화 (%)

**계산 방식:** 현재 차트에 표시된 데이터의 단순 평균

---

### 4. 상관관계 패널 (CorrelationPanel)

**3가지 탭:**

#### 코인 가격과의 상관관계
- 고래 거래 빈도 (ETH): +13.3%
- 고래 거래 빈도 (BTC): +9.0%
- 텔레그램 메시지 수 (ETH): +7.1%
- 트위터 인게이지먼트 (ETH): +6.2%
- 등 10개 항목

#### 고래 거래와의 상관관계
- 텔레그램 → 고래 (11시간 시차): +10.7%
- 트위터 → 고래 (5시간 시차): +6.1%
- 강세 뉴스 비율: +58.0%
- 등 7개 항목

#### 뉴스와의 상관관계
- 뉴스 수 (급증 이벤트): +72.0%
- 강세 뉴스 비율: +58.0%
- 규제 뉴스 (변동성): +54.0%
- 등 5개 항목

**데이터 소스:** 정적 데이터 (`lib/correlationData.ts`)

---

### 5. Spike 알람 리스트 (SpikeAlarmList)

**기능:**
- Z-score 기반 이상치 감지
- 우선순위 점수 계산
- 알람 레벨 분류 (CRITICAL/HIGH/MEDIUM)
- 필터링 (전체/긴급/높음/보통)

**감지 로직:**
- 24시간 윈도우로 Z-score 계산
- 임계값 2.0 이상이면 스파이크로 판단
- 우선순위 점수 >= 5점인 경우만 표시

**데이터 소스:** Supabase `final_integrated_data` 테이블

---

### 6. 뉴스 리스트 패널 (NewsListPanel)

**기능:**
- 최신 암호화폐 뉴스 표시
- 감정 분석 (긍정/부정/중립)
- 필터링 (전체/강세/약세/BTC/ETH)
- 태그 표시 (BTC, ETH, 강세, 약세)

**데이터 소스:** CSV 파일 (`coinness_data2.csv`)

**참고:** 향후 Supabase 연동 예정

---

## Community 페이지 (`/community`)

### 1. SentimentTrend (감성 트렌드)

**기능:**
- 시간별 감성 변화와 가격 상관관계 분석
- LineChart (감성 점수 + 가격 추이)
- Rolling correlation 계산

**필터:**
- 주기: 1시간/4시간/1일
- 코인: BTC/ETH
- 날짜 범위: 커스텀 선택

**통계 카드:**
- 글 수
- 평균 감성
- 상관계수
- 분산
- 긍정/부정/중립 비율

**인터랙션:**
- 그래프 클릭 시 해당 시점 카드 데이터 업데이트

**데이터 소스:** API `/api/community/timeseries`

---

### 2. SpikeTimeline (스파이크 분석)

**기능:**
- Z-score 기반 감성 급변 탐지
- LineChart (Z-score 추이 + 임계값 기준선)
- 스파이크 상세 정보 테이블

**필터:**
- 주기: 1시간/4시간/1일
- 코인: BTC/ETH
- 스파이크 임계값: 조정 가능
- 날짜 범위: 커스텀 선택

**인터랙션:**
- 그래프/테이블 클릭 → TopPosts 자동 필터링

**데이터 소스:** API `/api/community/spikes`

---

### 3. TopPosts (인기 게시글)

**기능:**
- 감성별 인기 게시글 목록
- 인게이지먼트 점수 계산 (댓글×3 + 공유×2 + 좋아요×1)

**필터:**
- 감성: 긍정/중립/부정/전체
- 기간: 1일/1주/1개월/커스텀
- 검색어: 키워드 검색
- 정렬: 최신순/오래된순/점수순

**인터랙션:**
- SpikeTimeline에서 날짜 선택 시 자동 필터링
- KeywordAnalysis에서 키워드 클릭 시 검색어 설정

**데이터 소스:** API `/api/community/top-posts`

---

### 4. KeywordAnalysis (키워드 분석)

**기능:**
- WordCloud (감성별 색상)
- BarChart (키워드별 감성 분포 - Stacked Bar)

**필터:**
- 감성: 긍정/중립/부정/전체
- 기간: 1일/1주/1개월/커스텀

**인터랙션:**
- 키워드 클릭 → BarChart 포커스 + TopPosts 검색어 설정

**데이터 소스:** API `/api/community/wordcloud`

---

## 🔌 API 엔드포인트

### HOME 페이지 관련

- `GET /api/composite-score` - 종합 점수 계산
- `GET /api/timeseries?range={7d|30d|90d}` - 타임시리즈 데이터
- `GET /api/spike-points?range={7d|30d|90d}` - Spike 포인트 감지
- `GET /api/news/recent?limit={number}` - 최신 뉴스

### Community 페이지 관련

- `GET /api/community/timeseries?freq={1h|4h|1d}&coin={btc|eth}` - 감성 트렌드
- `GET /api/community/spikes?freq={1h|4h|1d}&coin={btc|eth}` - 스파이크 감지
- `GET /api/community/top-posts?sentiment={positive|neutral|negative}&page={number}&range={1d|1w|1m|custom}` - 인기 게시글
- `GET /api/community/wordcloud?sentiment={positive|neutral|negative}&range={1d|1w|1m|custom}` - 키워드 분석

---

## 🗄️ 데이터 소스

### Supabase (실시간 데이터)

**테이블:** `final_integrated_data`

**필드:**
- `whale_tx_count` - 고래 거래 건수
- `whale_volume_sum` - 고래 거래량
- `btc_close`, `eth_close` - 코인 가격
- `btc_price_change`, `eth_price_change` - 가격 변화율
- `telegram_message_count` - 텔레그램 메시지 수
- `telegram_avg_sentiment` - 텔레그램 감정
- `twitter_engagement` - 트위터 인게이지먼트
- `twitter_sentiment` - 트위터 감정
- `news_count` - 뉴스 개수
- `news_sentiment_avg` - 뉴스 감정
- `timestamp` - 타임스탬프

### CSV 파일 (정적 데이터)

- `coinness_data2.csv` - 뉴스 데이터
- `correlationData.ts` - 상관관계 데이터 (정적)

---

## 🎨 UI/UX 특징

### 디자인
- 다크 테마 (업비트 스타일)
- 반응형 디자인 (모바일/태블릿/데스크톱)
- 그라데이션 및 애니메이션 효과

### 차트 라이브러리
- **Plotly.js** - 실시간 차트
- **recharts** - Community 페이지 차트
- **@visx/wordcloud** - WordCloud

### 스타일링
- **Tailwind CSS** - 유틸리티 기반 CSS
- 커스텀 다크 테마

---

## 🔄 컴포넌트 간 연동

### Community 페이지

**CommunityContext**를 통한 상태 공유:

```
SpikeTimeline → (날짜 선택) → TopPosts 자동 필터
KeywordAnalysis → (키워드 클릭) → TopPosts 검색어 설정
```

---

## 📊 주요 계산 로직

### 1. 종합 점수 계산
- 4가지 지표의 가중 평균
- 정규화 (min-max scaling)
- 변화량 및 변화율 계산
- 예측 정확도 계산

### 2. Spike 감지
- Z-score 계산 (24시간 윈도우)
- 임계값 2.0 이상 감지
- 우선순위 점수 계산
- 알람 레벨 분류

### 3. 상관관계 분석
- 피어슨 상관계수 계산
- p-value 기반 유의도 판단
- 시차 상관관계 분석

### 4. 감정 분석
- VADER 감정 분석
- 긍정/부정/중립 비율 계산
- 종합 감정 점수 (-1 ~ 1)

---

## 🛠️ 기술 스택

### Frontend
- **Next.js 14** (App Router)
- **React 18** (Client Components)
- **TypeScript**
- **Tailwind CSS**

### Backend
- **Next.js API Routes**
- **Supabase Client**

### 차트/시각화
- **Plotly.js**
- **recharts**
- **@visx/wordcloud**

### 데이터 처리
- **CSV 파싱** (csv-parse)
- **날짜 처리** (date-fns)

---

## 📁 프로젝트 구조

```
nextjs-dashboard/
├── app/
│   ├── api/              # API 라우트
│   │   ├── composite-score/
│   │   ├── timeseries/
│   │   ├── spike-points/
│   │   ├── news/
│   │   └── community/
│   ├── community/        # Community 페이지
│   ├── page.tsx         # HOME 페이지
│   └── layout.tsx       # 루트 레이아웃
├── components/
│   ├── community/       # Community 컴포넌트
│   ├── CompositeScoreHeader.tsx
│   ├── RealTimeChart.tsx
│   ├── CorrelationPanel.tsx
│   ├── SpikeAlarmList.tsx
│   └── NewsListPanel.tsx
├── contexts/
│   └── CommunityContext.tsx
├── lib/
│   ├── supabase.ts      # Supabase 클라이언트
│   └── correlationData.ts
└── [문서 파일들]
```

---

## 🚀 배포

### Vercel 배포
- GitHub 연동 자동 배포
- 환경 변수 설정 지원
- SSR/SSG 최적화

### 환경 변수
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase Anon Key

---

## 📝 문서

### 계산 로직 문서
- `COMPOSITE_SCORE_LOGIC.md` - 종합 점수 계산 로직
- `CHART_DATA_LOGIC.md` - 차트 데이터 및 스파이크 감지 로직
- `STATS_CARDS_LOGIC.md` - 통계 카드 계산 로직
- `CORRELATION_PANEL_LOGIC.md` - 상관관계 패널 로직
- `SPIKE_ALARM_LOGIC.md` - Spike 알람 로직
- `NEWS_PANEL_LOGIC.md` - 뉴스 패널 로직

### 설정 문서
- `SUPABASE_SETUP.md` - Supabase 설정 가이드
- `ENV_SETUP.md` - 환경 변수 설정
- `RLS_SETUP.sql` - Row Level Security 설정

---

## ✅ 기능 체크리스트

### HOME 페이지
- [x] 종합 점수 헤더
- [x] 실시간 차트
- [x] 통계 카드
- [x] 상관관계 패널 (3개 탭)
- [x] Spike 알람 리스트
- [x] 뉴스 리스트 패널

### Community 페이지
- [x] SentimentTrend (감성 트렌드)
- [x] SpikeTimeline (스파이크 분석)
- [x] TopPosts (인기 게시글)
- [x] KeywordAnalysis (키워드 분석)

### 데이터 연동
- [x] Supabase 연동 (종합 점수, 차트, Spike)
- [x] CSV 파일 읽기 (뉴스)
- [ ] Supabase 연동 (뉴스) - 향후 예정

### API
- [x] 종합 점수 API
- [x] 타임시리즈 API
- [x] Spike 포인트 API
- [x] 뉴스 API
- [x] Community API (4개 엔드포인트)

---

## 🎯 향후 개선 사항

1. **뉴스 데이터 Supabase 연동**
   - 현재 CSV 파일에서 읽기
   - Supabase 테이블로 마이그레이션

2. **실시간 업데이트**
   - WebSocket 또는 Polling
   - 자동 새로고침

3. **고급 필터링**
   - 날짜 범위 선택 (HOME 페이지)
   - 키워드 검색 (HOME 페이지)

4. **알림 시스템**
   - Spike 알람 푸시 알림
   - 이메일 알림

---

## 📊 데이터 통계

### Supabase 테이블
- `final_integrated_data`: 통합 데이터 (시간별)

### CSV 파일
- 뉴스 데이터: `coinness_data2.csv`
- 상관관계 데이터: 정적 데이터

---

**총 기능 수:** 10개 주요 기능 (HOME 6개 + Community 4개)

