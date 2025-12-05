-- ============================================
-- Row Level Security (RLS) 설정 SQL
-- ============================================
-- 테이블 생성 후 반드시 실행하세요!
-- Supabase 대시보드 → SQL Editor에서 실행
-- ============================================

-- 1. RLS 활성화
ALTER TABLE final_integrated_data ENABLE ROW LEVEL SECURITY;

-- 2. 공개 읽기 정책 추가 (Publishable key로 접근 가능하도록)
-- 기존 정책이 있으면 삭제 후 재생성
DROP POLICY IF EXISTS "Allow public read access" ON final_integrated_data;

CREATE POLICY "Allow public read access" 
ON final_integrated_data 
FOR SELECT 
USING (true);

-- 3. 확인 쿼리
SELECT 
  tablename,
  policyname,
  permissive,
  roles,
  cmd
FROM pg_policies 
WHERE tablename = 'final_integrated_data';

-- ============================================
-- 완료 메시지
-- ============================================
-- ✅ RLS 활성화 완료
-- ✅ 공개 읽기 정책 추가 완료
-- ============================================

