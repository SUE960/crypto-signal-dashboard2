-- ============================================
-- Supabase 테이블 생성 및 RLS 설정 SQL
-- ============================================
-- Supabase 대시보드 → SQL Editor에서 실행하세요
-- ============================================

-- 1. final_integrated_data 테이블 생성 (이미 존재하면 건너뛰기)
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

-- 2. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_final_integrated_data_timestamp 
ON final_integrated_data(timestamp);

CREATE INDEX IF NOT EXISTS idx_final_integrated_data_created_at 
ON final_integrated_data(created_at);

-- 3. Row Level Security (RLS) 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 4. 공개 읽기 정책 추가 (Publishable key로 접근 가능하도록)
-- 기존 정책이 있으면 삭제 후 재생성
DROP POLICY IF EXISTS "Allow public read access" ON final_integrated_data;

CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);

-- 5. 확인 쿼리 (실행 후 결과 확인)
SELECT 
  COUNT(*) as total_records,
  MIN(timestamp) as earliest_record,
  MAX(timestamp) as latest_record
FROM final_integrated_data;

-- ============================================
-- 완료 메시지
-- ============================================
-- ✅ 테이블 생성 완료
-- ✅ 인덱스 생성 완료
-- ✅ RLS 활성화 완료
-- ✅ 공개 읽기 정책 추가 완료
-- ============================================

