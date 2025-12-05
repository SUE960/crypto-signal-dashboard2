/**
 * Supabase 클라이언트 설정
 * 프로젝트 참조: goeqmhurrhgwmazaxfpm
 */
import { createClient } from '@supabase/supabase-js';

// Supabase 프로젝트 정보
const supabaseUrl = 'https://goeqmhurrhgwmazaxfpm.supabase.co';
// 환경 변수에서 API 키를 가져오거나, 공개 키 사용 (Row Level Security가 활성화되어 있어야 함)
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || '';

// Supabase 클라이언트 생성
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * 통합 데이터 조회
 * @param days 조회할 일수 (기본값: 30)
 * @returns 통합 데이터 배열
 */
export async function getIntegratedData(days: number = 30) {
  try {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const { data, error } = await supabase
      .from('final_integrated_data')
      .select('*')
      .gte('timestamp', cutoffDate.toISOString())
      .order('timestamp', { ascending: true });
    
    if (error) {
      console.error('Supabase 데이터 조회 오류:', error);
      return [];
    }
    
    return data || [];
  } catch (error) {
    console.error('데이터 조회 중 오류:', error);
    return [];
  }
}

/**
 * 타임시리즈 데이터 조회
 * @param range 시간 범위 ('7d', '30d', '90d')
 * @returns 타임시리즈 데이터 배열
 */
export async function getTimeseriesData(range: '7d' | '30d' | '90d' = '30d') {
  try {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const { data, error } = await supabase
      .from('final_integrated_data')
      .select('timestamp, whale_tx_count, whale_volume_sum, btc_close, eth_close, btc_price_change, eth_price_change')
      .gte('timestamp', cutoffDate.toISOString())
      .order('timestamp', { ascending: true });
    
    if (error) {
      console.error('Supabase 타임시리즈 조회 오류:', error);
      return [];
    }
    
    return (data || []).map((record: any) => ({
      timestamp: record.timestamp,
      date: new Date(record.timestamp).toLocaleDateString('ko-KR', {
        month: 'numeric',
        day: 'numeric',
        ...(range === '90d' ? {} : { hour: '2-digit' })
      }),
      whale_tx_count: parseFloat(record.whale_tx_count) || 0,
      whale_volume_sum: parseFloat(record.whale_volume_sum) || 0,
      btc_close: parseFloat(record.btc_close) || 0,
      eth_close: parseFloat(record.eth_close) || 0,
      btc_change: parseFloat(record.btc_price_change) || 0,
      eth_change: parseFloat(record.eth_price_change) || 0,
    })).filter((item: any) => item.btc_close > 0 || item.eth_close > 0);
  } catch (error) {
    console.error('타임시리즈 조회 중 오류:', error);
    return [];
  }
}

/**
 * 종합 점수 계산을 위한 데이터 조회
 * @param days 조회할 일수 (기본값: 30)
 * @returns 종합 점수 계산용 데이터 배열
 */
export async function getCompositeScoreData(days: number = 30) {
  try {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const { data, error } = await supabase
      .from('final_integrated_data')
      .select('*')
      .gte('timestamp', cutoffDate.toISOString())
      .order('timestamp', { ascending: true });
    
    if (error) {
      console.error('Supabase 종합 점수 데이터 조회 오류:', error);
      return [];
    }
    
    return (data || []).map((record: any) => ({
      timestamp: record.timestamp,
      whale_tx_count: parseFloat(record.whale_tx_count) || 0,
      whale_volume_sum: parseFloat(record.whale_volume_sum) || 0,
      btc_close: parseFloat(record.btc_close) || 0,
      btc_change: parseFloat(record.btc_price_change) || 0,
      eth_close: parseFloat(record.eth_close) || 0,
      eth_change: parseFloat(record.eth_price_change) || 0,
      telegram_message_count: parseFloat(record.telegram_message_count) || 0,
      telegram_sentiment: parseFloat(record.telegram_avg_sentiment) || 0,
      twitter_engagement: parseFloat(record.twitter_engagement) || 0,
      twitter_sentiment: parseFloat(record.twitter_sentiment) || 0,
      news_count: parseFloat(record.news_count) || 0,
      news_sentiment: parseFloat(record.news_sentiment_avg) || 0,
    })).filter((item: any) => item.btc_close > 0 || item.eth_close > 0);
  } catch (error) {
    console.error('종합 점수 데이터 조회 중 오류:', error);
    return [];
  }
}

/**
 * 스파이크 포인트 감지를 위한 데이터 조회
 * @param range 시간 범위 ('7d', '30d', '90d')
 * @returns 스파이크 감지용 데이터 배열
 */
export async function getSpikeDetectionData(range: '7d' | '30d' | '90d' = '30d') {
  try {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const { data, error } = await supabase
      .from('final_integrated_data')
      .select('*')
      .gte('timestamp', cutoffDate.toISOString())
      .order('timestamp', { ascending: true });
    
    if (error) {
      console.error('Supabase 스파이크 데이터 조회 오류:', error);
      return [];
    }
    
    return (data || []).map((record: any) => ({
      timestamp: record.timestamp,
      whale_tx_count: parseFloat(record.whale_tx_count) || 0,
      telegram_message_count: parseFloat(record.telegram_message_count) || 0,
      twitter_engagement: parseFloat(record.twitter_engagement) || 0,
      news_count: parseFloat(record.news_count) || 0,
      btc_close: parseFloat(record.btc_close) || 0,
      eth_close: parseFloat(record.eth_close) || 0,
      btc_change: parseFloat(record.btc_price_change) || 0,
      eth_change: parseFloat(record.eth_price_change) || 0,
      telegram_sentiment: parseFloat(record.telegram_avg_sentiment) || 0,
      twitter_sentiment: parseFloat(record.twitter_sentiment) || 0,
      news_sentiment: parseFloat(record.news_sentiment_avg) || 0,
    })).filter((item: any) => item.btc_close > 0 || item.eth_close > 0);
  } catch (error) {
    console.error('스파이크 데이터 조회 중 오류:', error);
    return [];
  }
}

