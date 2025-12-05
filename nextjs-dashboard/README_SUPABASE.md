# 🚀 Supabase 연동 완료 가이드

## ✅ 이미 완료된 작업

1. **Supabase 클라이언트 라이브러리 설치** ✅
   - `@supabase/supabase-js@2.86.2` 설치 완료

2. **API 라우트 Supabase 연동** ✅
   - `/api/composite-score` - Supabase에서 종합 점수 데이터 조회
   - `/api/timeseries` - Supabase에서 타임시리즈 데이터 조회
   - `/api/spike-points` - Supabase에서 스파이크 포인트 데이터 조회

3. **MCP 설정 파일 생성** ✅
   - `.cursor/mcp.json` 생성 완료

4. **Git 푸시 완료** ✅
   - 커밋: `097891a`

## 📋 남은 작업 (5분이면 완료!)

### 1️⃣ 환경 변수 설정 (1분)

`nextjs-dashboard/.env.local` 파일 생성:

```bash
NEXT_PUBLIC_SUPABASE_ANON_KEY=여기에_Publishable_key_붙여넣기
```

**Publishable key 찾기:**
- Supabase Dashboard → Settings → API → **Publishable key** 복사

> 📖 자세한 내용: `ENV_SETUP.md` 참고

### 2️⃣ Supabase 테이블 생성 (2분)

Supabase 대시보드 → **SQL Editor**에서 `supabase-setup.sql` 파일 내용 실행

또는 직접 실행:

```sql
-- 테이블 생성
CREATE TABLE IF NOT EXISTS final_integrated_data (
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

-- RLS 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책
CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);
```

> 📖 자세한 내용: `supabase-setup.sql` 파일 참고

### 3️⃣ 데이터 확인 (1분)

Supabase 대시보드 → **Table Editor** → `final_integrated_data`에서:
- 데이터가 있는지 확인
- 없으면 CSV 파일을 Supabase로 임포트 필요

### 4️⃣ 연결 테스트 (1분)

```bash
cd nextjs-dashboard
npm run dev
```

브라우저에서 확인:
- `http://localhost:3000/api/timeseries?range=30d`
- `http://localhost:3000/api/composite-score`
- `http://localhost:3000/api/spike-points?range=30d`

## 📚 상세 가이드

- **빠른 설정**: `QUICK_SETUP.md`
- **체크리스트**: `CHECKLIST.md`
- **환경 변수**: `ENV_SETUP.md`
- **SQL 설정**: `supabase-setup.sql`
- **전체 가이드**: `SUPABASE_SETUP.md`

## 🔍 문제 해결

### "Invalid API key" 오류
→ `.env.local` 파일의 Publishable key 확인

### "relation does not exist" 오류
→ `supabase-setup.sql` 실행하여 테이블 생성

### "new row violates row-level security policy" 오류
→ RLS 정책이 설정되었는지 확인 (`supabase-setup.sql` 실행)

### 데이터가 비어있음
→ Supabase 테이블에 데이터가 있는지 확인

## 🎉 완료 후

모든 설정이 완료되면:
1. HOME 페이지에서 실시간 데이터 확인
2. 차트와 그래프가 정상 작동하는지 확인
3. 필요시 데이터 추가/업데이트

---

**도움이 필요하신가요?** 각 가이드 파일을 참고하세요!

