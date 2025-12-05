# ✅ Supabase 연동 체크리스트

## 🔴 필수 설정 (반드시 해야 함)

### 1. MCP 설정 파일 생성
**위치:** `.cursor/mcp.json` (프로젝트 루트)

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=goeqmhurrhgwmazaxfpm"
    }
  }
}
```

**생성 방법:**
- Cursor에서 "Add to Cursor" 버튼 클릭 (Supabase 대시보드에서)
- 또는 수동으로 `.cursor/mcp.json` 파일 생성

### 2. 환경 변수 파일 생성
**위치:** `nextjs-dashboard/.env.local`

```bash
# Supabase 설정
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
```

**Anon Key 찾는 방법:**
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 `goeqmhurrhgwmazaxfpm` 선택
3. **Settings** → **API** → **Project API keys**
4. `anon` `public` 키 복사

### 3. Supabase 테이블 확인
**Supabase 대시보드에서 확인:**

1. **Table Editor** 메뉴로 이동
2. `final_integrated_data` 테이블이 있는지 확인
3. 없으면 테이블 생성 필요

**필수 컬럼:**
- `timestamp` (timestamptz)
- `whale_tx_count` (numeric)
- `whale_volume_sum` (numeric)
- `btc_close` (numeric)
- `eth_close` (numeric)
- `btc_price_change` (numeric)
- `eth_price_change` (numeric)
- `telegram_message_count` (numeric)
- `telegram_avg_sentiment` (numeric)
- `twitter_engagement` (numeric)
- `twitter_sentiment` (numeric)
- `news_count` (numeric)
- `news_sentiment_avg` (numeric)

### 4. Row Level Security (RLS) 설정
**Supabase SQL Editor에서 실행:**

```sql
-- RLS 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 추가
CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);
```

## 🟡 권장 설정 (데이터가 있을 경우)

### 5. 데이터 확인
- Supabase 대시보드에서 `final_integrated_data` 테이블에 데이터가 있는지 확인
- 최소 30일치 데이터가 있으면 좋음

### 6. 연결 테스트
```bash
cd nextjs-dashboard
npm run dev
```

브라우저에서 테스트:
- `http://localhost:3000/api/timeseries?range=30d`
- `http://localhost:3000/api/composite-score`
- `http://localhost:3000/api/spike-points?range=30d`

## ✅ 완료된 항목

- [x] Supabase 클라이언트 라이브러리 설치
- [x] API 라우트 Supabase 연동
- [x] Git 푸시 완료
- [x] 코드 작성 완료

## 📝 빠른 설정 가이드

1. **MCP 설정** (1분)
   - Supabase 대시보드 → MCP 탭 → "Add to Cursor" 클릭

2. **환경 변수 설정** (2분)
   - Supabase 대시보드 → Settings → API → Anon Key 복사
   - `nextjs-dashboard/.env.local` 파일 생성 및 키 추가

3. **테이블 확인** (3분)
   - Supabase 대시보드 → Table Editor
   - `final_integrated_data` 테이블 확인/생성

4. **RLS 설정** (2분)
   - Supabase 대시보드 → SQL Editor
   - 위의 SQL 실행

5. **테스트** (1분)
   - `npm run dev` 실행
   - API 엔드포인트 확인

**총 소요 시간: 약 10분**

