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

## 📝 개발 노트
- Next.js 14 App Router 사용
- Tailwind CSS로 스타일링
- Plotly.js로 차트 렌더링
- 완전한 SSR/SSG 지원 (Vercel 최적화)


