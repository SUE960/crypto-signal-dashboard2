# 시계열 차트 컴포넌트 가이드

## 📊 생성된 컴포넌트

### 1. **RealTimeChart.tsx** (추천 ⭐)
- 완전한 기능을 갖춘 시계열 차트
- 듀얼 Y축 (고래 거래 + 코인 가격)
- 3가지 차트 타입 (선형/영역/복합)
- 기간 선택 (7일/30일/90일)
- 코인 선택 (BTC/ETH/Both)
- 통계 카드 포함

### 2. **TimeSeriesChart.tsx**
- 기본 버전 (간단한 구현)
- 가격/변화율 모드
- 커스텀 툴팁

### 3. **API_ROUTE_EXAMPLE.ts**
- 실제 CSV 데이터를 읽는 API 예제
- `/api/timeseries` 라우트

---

## 🚀 사용 방법

### 단계 1: 패키지 설치 완료 ✅
```bash
npm install recharts
```

### 단계 2: 컴포넌트 임포트
```typescript
// app/page.tsx 또는 원하는 페이지에서
import RealTimeChart from '@/components/RealTimeChart';

export default function Dashboard() {
  return (
    <div className="p-8">
      <RealTimeChart />
    </div>
  );
}
```

### 단계 3: API 라우트 생성 (선택사항)
실제 데이터를 사용하려면:
```typescript
// app/api/timeseries/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const range = searchParams.get('range') || '30d';
  
  // CSV 파일 읽기
  const data = fs.readFileSync('../data/final_integrated_data.csv', 'utf-8');
  const records = parse(data, { columns: true });
  
  // 필터링 및 변환
  // ... (API_ROUTE_EXAMPLE.ts 참고)
  
  return NextResponse.json(records);
}
```

---

## 🎨 차트 기능

### 듀얼 Y축
- **왼쪽 Y축** (보라색): 고래 거래 빈도 (건)
- **오른쪽 Y축** (파란색): 코인 가격 ($)

### 차트 타입
1. **선형 (Line)**: 깔끔한 선 그래프
2. **영역 (Area)**: 그라데이션 영역 차트
3. **복합 (Composed)**: 영역 + 바 + 선 조합 ⭐

### 컨트롤
- **기간**: 7일 / 30일 / 90일
- **코인**: BTC / ETH / Both
- **차트 타입**: 선형 / 영역 / 복합

### 통계 카드
- 평균 고래 거래
- BTC 평균 가격
- BTC 평균 변화율
- ETH 평균 가격
- ETH 평균 변화율

---

## 📐 데이터 구조

차트는 다음 데이터를 기대합니다:

```typescript
interface ChartDataPoint {
  timestamp: string;           // ISO 날짜
  date: string;               // 표시용 날짜
  whale_tx_count: number;     // 고래 거래 빈도
  whale_volume_sum: number;   // 고래 거래량
  btc_close: number;          // BTC 종가
  eth_close: number;          // ETH 종가
  btc_change: number;         // BTC 변화율 (%)
  eth_change: number;         // ETH 변화율 (%)
}
```

---

## 🎯 실제 데이터 연결

### 방법 1: API 라우트 (권장)
```typescript
// app/api/timeseries/route.ts 생성
// 위의 API_ROUTE_EXAMPLE.ts 코드 사용
```

### 방법 2: 직접 CSV 로딩
```typescript
// RealTimeChart 컴포넌트 수정
useEffect(() => {
  const loadData = async () => {
    const response = await fetch('/path/to/final_integrated_data.csv');
    const text = await response.text();
    // CSV 파싱...
  };
  loadData();
}, []);
```

---

## 🎨 스타일 커스터마이징

### 색상 변경
```typescript
// 고래 거래: #a855f7 (보라색)
// BTC: #f97316 (주황색)
// ETH: #3b82f6 (파란색)
```

### 크기 조정
```typescript
<ResponsiveContainer width="100%" height={550}>
  // height를 원하는 값으로 변경
```

---

## 💡 사용 예시

### 기본 사용
```typescript
<RealTimeChart />
```

### 커스텀 데이터 경로
```typescript
<RealTimeChart dataPath="/custom/path/to/data.csv" />
```

---

## 🔧 문제 해결

### 1. "recharts not found" 에러
```bash
cd nextjs-dashboard
npm install recharts
```

### 2. 데이터가 표시되지 않음
- API 라우트가 제대로 설정되었는지 확인
- 브라우저 콘솔에서 에러 확인
- 더미 데이터가 정상 작동하는지 확인

### 3. 차트가 느림
- 데이터 포인트 수를 줄이기 (샘플링)
- 기간을 짧게 설정 (7일)

---

## 📊 결과 화면

차트에는 다음이 표시됩니다:

1. **헤더**
   - 제목: "🐋 고래 지갑 & 코인 가격 트렌드"
   - 부제목: "실시간 상관관계 분석"

2. **컨트롤 패널**
   - 기간 선택 버튼 (7/30/90일)
   - 코인 선택 버튼 (BTC/ETH/Both)
   - 차트 타입 버튼 (선형/영역/복합)

3. **메인 차트**
   - 듀얼 Y축
   - 반응형 크기
   - 호버 툴팁
   - 범례

4. **통계 카드** (4개)
   - 보라색: 평균 고래 거래
   - 주황색: BTC 통계
   - 파란색: ETH 통계

---

## 🎉 완료!

이제 Next.js 대시보드에 고래 지갑과 코인 가격의 트렌드를 보여주는 전문적인 시계열 차트가 준비되었습니다!

```bash
# 개발 서버 실행
npm run dev
```

http://localhost:3000 에서 확인하세요! 📊✨

