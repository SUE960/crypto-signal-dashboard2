# ✅ 최종 설정 완료 가이드

## ✅ 완료된 항목

1. **환경 변수 파일 생성** ✅
   - `.env.local` 파일 생성 완료
   - Publishable key 설정 완료: `sb_publishable_Tst2PM_CuNDmqSpW_uKCEQ_0JIWg7HN`

2. **MCP 설정 파일** ✅
   - `.cursor/mcp.json` 생성 완료

3. **코드 연동** ✅
   - 모든 API 라우트 Supabase 연동 완료

## ⚠️ 남은 작업: Supabase 테이블 생성

테스트 결과 테이블이 아직 생성되지 않았습니다. 다음 단계를 진행하세요:

### 1. Supabase 대시보드 접속
1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 `goeqmhurrhgwmazaxfpm` 선택

### 2. SQL Editor에서 테이블 생성

**방법 1: SQL Editor 사용 (권장)**
1. 왼쪽 메뉴에서 **SQL Editor** 클릭
2. **New query** 클릭
3. 아래 SQL을 복사하여 붙여넣기
4. **Run** 버튼 클릭

**방법 2: Table Editor 사용**
1. 왼쪽 메뉴에서 **Table Editor** 클릭
2. **New table** 클릭
3. 테이블명: `final_integrated_data`
4. 컬럼 추가 (아래 참고)

### 3. 실행할 SQL

`nextjs-dashboard/supabase-setup.sql` 파일의 내용을 복사하여 실행하세요:

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

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_final_integrated_data_timestamp 
ON final_integrated_data(timestamp);

-- RLS 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 공개 읽기 정책 추가
DROP POLICY IF EXISTS "Allow public read access" ON final_integrated_data;

CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);
```

### 4. 테이블 생성 확인

SQL 실행 후:
1. **Table Editor**로 이동
2. `final_integrated_data` 테이블이 보이는지 확인
3. 테이블 구조 확인

### 5. 연결 테스트

테이블 생성 후 다시 테스트:

```bash
cd nextjs-dashboard
npm run dev
```

브라우저에서 확인:
- `http://localhost:3000/api/timeseries?range=30d`
- `http://localhost:3000/api/composite-score`
- `http://localhost:3000/api/spike-points?range=30d`

## 📊 데이터 추가 (선택사항)

테이블이 생성되면 데이터를 추가할 수 있습니다:

1. **CSV 파일 임포트**
   - Supabase 대시보드 → Table Editor → Import data
   - 기존 CSV 파일 (`data/final_integrated_data.csv`) 임포트

2. **수동 데이터 추가**
   - Table Editor에서 직접 행 추가

## ✅ 최종 체크리스트

- [x] 환경 변수 파일 생성 (`.env.local`)
- [x] MCP 설정 파일 생성 (`.cursor/mcp.json`)
- [x] 코드 연동 완료
- [ ] Supabase 테이블 생성
- [ ] RLS 정책 설정
- [ ] 연결 테스트 성공
- [ ] 데이터 확인

## 🎉 완료 후

모든 설정이 완료되면:
1. HOME 페이지에서 실시간 데이터 확인
2. 차트와 그래프가 정상 작동하는지 확인
3. 필요시 데이터 추가/업데이트

---

**도움이 필요하신가요?** `supabase-setup.sql` 파일을 참고하세요!

