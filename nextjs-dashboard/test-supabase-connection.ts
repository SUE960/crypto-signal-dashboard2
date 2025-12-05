/**
 * Supabase 연결 테스트 스크립트
 * 실행: npx tsx test-supabase-connection.ts
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://goeqmhurrhgwmazaxfpm.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || '';

console.log('🔍 Supabase 연결 테스트 시작...\n');
console.log('URL:', supabaseUrl);
console.log('Anon Key:', supabaseAnonKey ? `${supabaseAnonKey.substring(0, 20)}...` : '❌ 설정되지 않음\n');

if (!supabaseAnonKey) {
  console.error('❌ Supabase Anon Key가 설정되지 않았습니다.');
  console.log('환경 변수 NEXT_PUBLIC_SUPABASE_ANON_KEY 또는 SUPABASE_ANON_KEY를 설정해주세요.');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  try {
    // 1. 테이블 존재 확인
    console.log('1️⃣ final_integrated_data 테이블 확인 중...');
    const { data, error, count } = await supabase
      .from('final_integrated_data')
      .select('*', { count: 'exact', head: true })
      .limit(1);

    if (error) {
      console.error('❌ 테이블 조회 오류:', error.message);
      console.error('   코드:', error.code);
      console.error('   상세:', error.details);
      return false;
    }

    console.log(`✅ 테이블 존재 확인됨 (총 레코드 수: ${count || 0}개)\n`);

    // 2. 최근 데이터 조회 테스트
    console.log('2️⃣ 최근 30일 데이터 조회 테스트...');
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30);

    const { data: recentData, error: queryError } = await supabase
      .from('final_integrated_data')
      .select('timestamp, whale_tx_count, btc_close, eth_close')
      .gte('timestamp', cutoffDate.toISOString())
      .order('timestamp', { ascending: false })
      .limit(5);

    if (queryError) {
      console.error('❌ 데이터 조회 오류:', queryError.message);
      return false;
    }

    if (!recentData || recentData.length === 0) {
      console.log('⚠️  최근 30일 데이터가 없습니다.');
      console.log('   테이블에 데이터를 추가해주세요.');
      return false;
    }

    console.log(`✅ 최근 데이터 조회 성공 (${recentData.length}개 레코드)`);
    console.log('   샘플 데이터:');
    recentData.slice(0, 3).forEach((record: any, idx: number) => {
      console.log(`   ${idx + 1}. ${new Date(record.timestamp).toLocaleString('ko-KR')}`);
      console.log(`      고래 거래: ${record.whale_tx_count || 0}건`);
      console.log(`      BTC: $${record.btc_close || 0}`);
      console.log(`      ETH: $${record.eth_close || 0}`);
    });
    console.log('');

    // 3. 컬럼 구조 확인
    console.log('3️⃣ 컬럼 구조 확인 중...');
    const { data: sampleData } = await supabase
      .from('final_integrated_data')
      .select('*')
      .limit(1);

    if (sampleData && sampleData.length > 0) {
      const columns = Object.keys(sampleData[0]);
      console.log(`✅ 컬럼 확인됨 (총 ${columns.length}개 컬럼)`);
      console.log('   주요 컬럼:');
      const importantColumns = [
        'timestamp',
        'whale_tx_count',
        'whale_volume_sum',
        'btc_close',
        'eth_close',
        'btc_price_change',
        'eth_price_change',
        'telegram_message_count',
        'telegram_avg_sentiment',
        'twitter_engagement',
        'twitter_sentiment',
        'news_count',
        'news_sentiment_avg'
      ];
      
      importantColumns.forEach(col => {
        const exists = columns.includes(col);
        console.log(`   ${exists ? '✅' : '❌'} ${col}`);
      });
      console.log('');
    }

    console.log('🎉 Supabase 연결 테스트 완료!');
    console.log('✅ 모든 테스트 통과');
    return true;

  } catch (error: any) {
    console.error('❌ 예상치 못한 오류:', error.message);
    return false;
  }
}

testConnection()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('테스트 실행 중 오류:', error);
    process.exit(1);
  });

