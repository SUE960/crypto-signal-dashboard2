# 환경 변수 설정 가이드

## 📝 .env.local 파일 생성

`nextjs-dashboard` 폴더에 `.env.local` 파일을 생성하세요:

```bash
cd nextjs-dashboard
touch .env.local
```

또는 직접 파일을 생성하고 다음 내용을 추가:

```bash
# Supabase 설정
# Supabase Dashboard → Settings → API → Publishable key를 복사하여 아래에 붙여넣으세요
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_your_key_here
```

## 🔑 Publishable Key 찾는 방법

1. [Supabase Dashboard](https://supabase.com/dashboard) 접속
2. 프로젝트 `goeqmhurrhgwmazaxfpm` 선택
3. **Settings** → **API** → **Publishable key** 섹션
4. 키 값 복사 (예: `sb_publishable_Tst2PM_CuNDmqSpW_uKCEQ_0JIWg7HN`)
5. `.env.local` 파일에 붙여넣기

## ⚠️ 중요 사항

- `.env.local` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨)
- Publishable key는 브라우저에서 안전하게 사용할 수 있습니다 (RLS가 활성화된 경우)
- Secret key는 절대 `.env.local`에 넣지 마세요 (서버 사이드에서만 사용)

## ✅ 확인 방법

환경 변수가 제대로 설정되었는지 확인:

```bash
cd nextjs-dashboard
npm run dev
```

서버가 시작되면 환경 변수가 로드됩니다.

또는 테스트 스크립트로 확인:

```bash
export NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here
npx tsx test-supabase-connection.ts
```

