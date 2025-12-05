# 🚀 Supabase 빠른 설정 가이드

## 1단계: 환경 변수 설정 (필수)

Supabase 대시보드에서 **Publishable key**를 복사했으니, 이제 환경 변수 파일을 생성하세요:

```bash
cd nextjs-dashboard
cp .env.local.example .env.local
```

그 다음 `.env.local` 파일을 열어서 실제 Publishable key를 붙여넣으세요:

```bash
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_Tst2PM_CuNDmqSpW_uKCEQ_0JIWg7HN
```

> ⚠️ **중요**: 위 키는 예시입니다. 실제 Supabase 대시보드에서 복사한 키를 사용하세요!

## 2단계: Supabase 테이블 확인

Supabase 대시보드에서:

1. **Table Editor** 메뉴로 이동
2. `final_integrated_data` 테이블이 있는지 확인
3. 없으면 테이블 생성 필요

### 테이블이 없는 경우 생성 SQL:

```sql
CREATE TABLE final_integrated_data (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  whale_tx_count NUMERIC DEFAULT 0,
  whale_volume_sum NUMERIC DEFAULT 0,
  btc_close NUMERIC DEFAULT 0,
  eth_close NUMERIC DEFAULT 0,
  btc_price_change NUMERIC DEFAULT 0,
  eth_price_change NUMERIC DEFAULT 0,
  telegram_message_count NUMERIC DEFAULT 0,
  telegram_avg_sentiment NUMERIC DEFAULT 0,
  twitter_engagement NUMERIC DEFAULT 0,
  twitter_sentiment NUMERIC DEFAULT 0,
  news_count NUMERIC DEFAULT 0,
  news_sentiment_avg NUMERIC DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가 (성능 향상)
CREATE INDEX idx_final_integrated_data_timestamp ON final_integrated_data(timestamp);
```

## 3단계: Row Level Security (RLS) 설정 (필수)

Supabase 대시보드 → **SQL Editor**에서 실행:

```sql
-- RLS 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 추가
CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);
```

> ⚠️ **중요**: RLS를 설정하지 않으면 "new row violates row-level security policy" 오류가 발생합니다!

## 4단계: 연결 테스트

```bash
cd nextjs-dashboard
npm run dev
```

브라우저에서 다음 URL들을 확인:

- ✅ `http://localhost:3000/api/timeseries?range=30d`
- ✅ `http://localhost:3000/api/composite-score`
- ✅ `http://localhost:3000/api/spike-points?range=30d`

정상 작동하면 JSON 데이터가 반환됩니다.

## 5단계: 데이터 확인

Supabase 대시보드 → **Table Editor** → `final_integrated_data`에서:

- 데이터가 있는지 확인
- 최소 30일치 데이터가 있으면 좋음
- 데이터가 없으면 CSV 파일을 Supabase로 임포트 필요

## ✅ 완료 체크리스트

- [ ] `.env.local` 파일 생성 및 Publishable key 설정
- [ ] `final_integrated_data` 테이블 존재 확인
- [ ] RLS 정책 설정 완료
- [ ] Next.js 개발 서버 실행
- [ ] API 엔드포인트 테스트 성공
- [ ] 데이터 확인

## 🔧 문제 해결

### 오류: "Invalid API key"
- `.env.local` 파일의 키가 올바른지 확인
- Supabase 대시보드에서 Publishable key 다시 확인

### 오류: "relation does not exist"
- 테이블명이 정확히 `final_integrated_data`인지 확인
- Supabase 대시보드에서 테이블 생성

### 오류: "new row violates row-level security policy"
- RLS 정책이 설정되었는지 확인
- 위의 SQL을 다시 실행

### 데이터가 비어있음
- 테이블에 데이터가 있는지 확인
- CSV 파일을 Supabase로 임포트

## 📝 다음 단계

모든 설정이 완료되면:
1. HOME 페이지에서 실시간 데이터 확인
2. 차트와 그래프가 정상 작동하는지 확인
3. 필요시 데이터 추가/업데이트

