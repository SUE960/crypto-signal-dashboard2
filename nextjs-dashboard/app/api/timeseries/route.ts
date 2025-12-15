import { NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import * as fs from 'fs';
import * as path from 'path';
import { createClient } from '@supabase/supabase-js';

// 캐시 파일 경로
const getCachePath = () => {
  const cacheDir = path.join(process.cwd(), 'data', 'cache');
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }
  return path.join(cacheDir, 'whale_transactions_nov_2025.json');
};

// 캐시 로드 함수
const loadCache = (): { data: any[]; timestamp: number } | null => {
  try {
    const cachePath = getCachePath();
    if (fs.existsSync(cachePath)) {
      const cacheContent = fs.readFileSync(cachePath, 'utf-8');
      const cache = JSON.parse(cacheContent);
      // 캐시 유효기간: 24시간
      const cacheAge = Date.now() - cache.timestamp;
      const cacheMaxAge = 24 * 60 * 60 * 1000; // 24시간
      
      if (cacheAge < cacheMaxAge) {
        console.log(`✅ 캐시에서 데이터 로드: ${cache.data.length}개 (${Math.round(cacheAge / 1000 / 60)}분 전 저장됨)`);
        return cache;
      } else {
        console.log(`⚠️ 캐시가 만료되었습니다 (${Math.round(cacheAge / 1000 / 60 / 60)}시간 전 저장됨)`);
      }
    }
  } catch (error) {
    console.warn('⚠️ 캐시 로드 실패:', error);
  }
  return null;
};

// 캐시 저장 함수
const saveCache = (data: any[]) => {
  try {
    const cachePath = getCachePath();
    const cache = {
      data,
      timestamp: Date.now(),
    };
    fs.writeFileSync(cachePath, JSON.stringify(cache, null, 2), 'utf-8');
    console.log(`💾 캐시에 데이터 저장: ${data.length}개`);
  } catch (error) {
    console.warn('⚠️ 캐시 저장 실패:', error);
  }
};

// 동적 렌더링 강제 (request.url 사용)
export const dynamic = 'force-dynamic';

// Supabase 클라이언트 초기화
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://goeqmhurrhgwmazaxfpm.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_secret_76GYGaZUX0TNR9qgO4QcIA_XkYC8oqZ';

// 연결 상태 로깅 추가
console.log('🔗 Supabase 연결 설정:');
console.log(`  URL: ${supabaseUrl}`);
console.log(`  Key 사용: ${supabaseKey ? '설정됨' : '없음'}`);

const supabase = createClient(supabaseUrl, supabaseKey);

interface ChartDataPoint {
  timestamp: string;
  date: string;
  whale_tx_count: number;
  whale_volume_sum: number;
  btc_close: number;
  eth_close: number;
  btc_change: number;
  eth_change: number;
  btc_volatility?: number;
  eth_volatility?: number;
}

function loadCSV(relativeFile: string): any[] {
  // nextjs-dashboard -> 상위 폴더 -> data -> 파일
  // Vercel 배포 환경을 고려한 경로들
  const possiblePaths = [
    path.join(process.cwd(), 'data', relativeFile),  // nextjs-dashboard/data/ (우선)
    path.join(process.cwd(), '..', 'data', relativeFile),  // 상위 폴더/data/
    path.join(process.cwd(), '../../data', relativeFile),  // 프로젝트 루트/data/
    path.join(process.cwd(), 'public/data', relativeFile),  // public/data/
  ];

  for (const fullPath of possiblePaths) {
    if (fs.existsSync(fullPath)) {
      console.log(`✅ CSV 파일 발견: ${fullPath}`);
      const text = fs.readFileSync(fullPath, 'utf-8');
      const records = parse(text, {
        columns: true,
        skip_empty_lines: true,
      });
      console.log(`   로드된 레코드 수: ${records.length}`);
      return records;
    }
  }

  // 모든 경로 시도 실패
  console.error(`❌ CSV 파일을 찾을 수 없습니다: ${relativeFile}`);
  console.error(`   시도한 경로들:`, possiblePaths);
  throw new Error(`CSV file not found: ${relativeFile}`);
}

function calculateChange(current: number, previous: number): number {
  if (!previous || previous === 0) return 0;
  return ((current - previous) / previous) * 100;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = searchParams.get('range') || '30d';

    // 범위에 따른 일수 계산
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    // 날짜 필터링을 나중에 적용하므로 cutoffDate는 사용하지 않음
    // 대신 최신 데이터부터 표시

    // Supabase에서 고래 거래 데이터 로드
    // 11월 1일~8일 데이터를 직접 필터링해서 가져오기
    let whaleData: any[] = [];
    try {
      // 먼저 캐시 확인
      const cache = loadCache();
      if (cache && cache.data.length > 0) {
        whaleData = cache.data;
        console.log(`✅ 캐시에서 11월 1일~8일 데이터 ${whaleData.length}개 로드 완료`);
      } else {
        console.log('🔄 Supabase에서 고래 거래 데이터 로드 중...');
        
        // 11월 1일~8일 데이터를 직접 필터링해서 가져오기
        // "2025-11-01" ~ "2025-11-08" 형식과 "2025.11.1" ~ "2025.11.8" 형식 모두 포함
        // 두 개의 쿼리로 분리해서 실행 (Supabase의 .or() 문법이 불안정할 수 있음)
        
        // 11월 1일~8일 데이터를 페이지네이션으로 모두 가져오기
        const novDates = ['2025-11-01', '2025-11-02', '2025-11-03', '2025-11-04', '2025-11-05', '2025-11-06', '2025-11-07', '2025-11-08'];
        const allNovData: any[] = [];
        
        // 각 날짜별로 모든 데이터 가져오기 (페이지네이션)
        for (const date of novDates) {
          let hasMore = true;
          let page = 0;
          const pageSize = 1000;
          
          // "2025-11-01" 형식으로 모든 페이지 가져오기
          while (hasMore) {
            const { data: dashData, error: dashError } = await supabase
              .from('whale_transactions')
              .select('block_timestamp, amount_usd, coin_symbol')
              .like('block_timestamp', `${date}%`)
              .range(page * pageSize, (page + 1) * pageSize - 1);
            
            if (dashError) {
              console.warn(`⚠️ ${date} 대시 형식 데이터 로드 오류 (페이지 ${page}):`, dashError);
              hasMore = false;
            } else if (dashData && dashData.length > 0) {
              allNovData.push(...dashData);
              hasMore = dashData.length === pageSize; // 더 많은 데이터가 있을 수 있음
              page++;
              console.log(`  ${date} 대시 형식: ${dashData.length}개 로드 (총 ${allNovData.length}개)`);
            } else {
              hasMore = false;
            }
          }
          
          // "2025.11.1" 형식 (날짜를 점 형식으로 변환)
          const dotDate = date.replace(/-/g, '.').replace(/\.0([1-8])/, '.$1'); // "2025.11.1" 형식
          hasMore = true;
          page = 0;
          
          while (hasMore) {
            const { data: dotData, error: dotError } = await supabase
              .from('whale_transactions')
              .select('block_timestamp, amount_usd, coin_symbol')
              .like('block_timestamp', `${dotDate}%`)
              .range(page * pageSize, (page + 1) * pageSize - 1);
            
            if (dotError) {
              console.warn(`⚠️ ${dotDate} 점 형식 데이터 로드 오류 (페이지 ${page}):`, dotError);
              hasMore = false;
            } else if (dotData && dotData.length > 0) {
              allNovData.push(...dotData);
              hasMore = dotData.length === pageSize;
              page++;
              console.log(`  ${dotDate} 점 형식: ${dotData.length}개 로드 (총 ${allNovData.length}개)`);
            } else {
              hasMore = false;
            }
          }
        }
        
        if (allNovData.length > 0) {
          // 중복 제거 (tx_hash나 고유 키가 있다면 사용, 없으면 block_timestamp + amount_usd 조합 사용)
          const uniqueData = Array.from(
            new Map(allNovData.map((row, idx) => {
              // 고유 키 생성 (block_timestamp + amount_usd + 인덱스)
              const key = `${row.block_timestamp}_${row.amount_usd}_${idx}`;
              return [key, row];
            })).values()
          );
          
          whaleData = uniqueData;
          
          console.log(`✅ Supabase에서 11월 1일~8일 데이터 ${whaleData.length}개 로드 완료 (중복 제거 전: ${allNovData.length}개)`);
          
          // 캐시에 저장
          saveCache(whaleData);
        } else {
          // 폴백: 전체 데이터 가져오기 (최신부터)
          console.log('⚠️ 11월 데이터가 없어 전체 데이터 로드 시도...');
          const { data, error } = await supabase
            .from('whale_transactions')
            .select('block_timestamp, amount_usd, coin_symbol')
            .order('id', { ascending: false })
            .limit(100000);
          
          if (error) {
            console.error('❌ Supabase 데이터 로드 오류:', error);
            throw error;
          }
          
          if (data && data.length > 0) {
            whaleData = data;
            console.log(`✅ Supabase에서 전체 데이터 ${whaleData.length}개 로드 완료`);
          } else {
            console.warn('⚠️ Supabase에 고래 거래 데이터가 없습니다. CSV 폴백 시도...');
            // 폴백: CSV 파일 사용
            try {
              whaleData = loadCSV('whale_transactions_rows.csv');
            } catch (e) {
              console.warn('고래 거래 데이터 CSV 로드 실패:', e);
              try {
                whaleData = loadCSV('whale_transactions_rows_ETH_rev1.csv');
              } catch (e2) {
                console.warn('고래 거래 데이터 폴백 로드 실패:', e2);
              }
            }
          }
        }
      }
    } catch (e) {
      console.warn('고래 거래 데이터 로드 실패:', e);
      // 폴백: CSV 파일 사용
      try {
        whaleData = loadCSV('whale_transactions_rows.csv');
      } catch (e2) {
        console.warn('고래 거래 데이터 CSV 로드 실패:', e2);
        try {
          whaleData = loadCSV('whale_transactions_rows_ETH_rev1.csv');
        } catch (e3) {
          console.warn('고래 거래 데이터 폴백 로드 실패:', e3);
        }
      }
    }

    // CSV 파일 로드 (BTC, ETH 가격 데이터)
    let btcPriceData: any[] = [];
    let ethPriceData: any[] = [];

    try {
      btcPriceData = loadCSV('price_history_btc_rows.csv');
    } catch (e) {
      console.warn('BTC 가격 데이터 로드 실패:', e);
    }

    try {
      ethPriceData = loadCSV('price_history_eth_rows.csv');
    } catch (e) {
      console.warn('ETH 가격 데이터 로드 실패:', e);
    }

    // 타임스탬프 파싱 및 필터링
    const parseTimestamp = (ts: string | number): Date | null => {
      if (!ts || ts === '#VALUE!' || (typeof ts === 'string' && ts.trim() === '')) return null;
      try {
        // Unix timestamp (숫자 형식) 처리
        if (typeof ts === 'number' || (typeof ts === 'string' && /^\d+$/.test(ts.toString().trim()))) {
          const timestamp = typeof ts === 'number' ? ts : parseInt(ts.toString().trim(), 10);
          // Unix timestamp는 초 단위이므로 밀리초로 변환
          // 10자리 숫자는 초 단위, 13자리는 밀리초 단위
          const date = timestamp.toString().length === 10 
            ? new Date(timestamp * 1000) 
            : new Date(timestamp);
          if (isNaN(date.getTime())) {
            console.warn(`Unix timestamp 파싱 실패: ${ts}`);
            return null;
          }
          return date;
        }
        
        // 문자열 형식 처리
        let normalized = ts.toString().trim();
        
        // #VALUE! 같은 오류 값 필터링
        if (normalized.includes('#') || normalized.toLowerCase().includes('value')) {
          return null;
        }
        
        // "2025.11.7 19:28" 형식 처리 (Supabase에서 발견된 형식)
        if (normalized.match(/^\d{4}\.\d{1,2}\.\d{1,2} \d{1,2}:\d{2}$/)) {
          const [datePart, timePart] = normalized.split(' ');
          const [year, month, day] = datePart.split('.');
          const [hour, minute] = timePart.split(':');
          normalized = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hour.padStart(2, '0')}:${minute}:00`;
        }
        // "2025-11-01 00:01:11" 형식 (초까지 포함) - 그대로 사용
        else if (normalized.match(/^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}$/)) {
          // 이미 올바른 형식이므로 그대로 사용
          const [datePart, timePart] = normalized.split(' ');
          const [hour, minute, second] = timePart.split(':');
          normalized = `${datePart} ${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:${second.padStart(2, '0')}`;
        }
        // "2025-11-01 0:00" -> "2025-11-01 00:00:00" 형식으로 변환
        else if (normalized.match(/^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}$/)) {
          const [datePart, timePart] = normalized.split(' ');
          const [hour, minute] = timePart.split(':');
          normalized = `${datePart} ${hour.padStart(2, '0')}:${minute}:00`;
        }
        
        const date = new Date(normalized);
        if (isNaN(date.getTime())) {
          console.warn(`날짜 파싱 실패: ${ts} -> ${normalized}`);
          return null;
        }
        return date;
      } catch (error) {
        console.warn(`날짜 파싱 오류: ${ts}`, error);
        return null;
      }
    };

    // 고래 거래 데이터 처리
    console.log(`고래 거래 원본 데이터: ${whaleData.length}개 행`);
    if (whaleData.length > 0) {
      console.log(`  첫 번째 행 샘플:`, whaleData[0]);
      console.log(`  컬럼명:`, Object.keys(whaleData[0]));
    }
    
    // Supabase 데이터인지 CSV 데이터인지 확인
    const isSupabaseData = whaleData.length > 0 && whaleData[0].block_timestamp !== undefined;
    
    let processedWhale: any[] = [];
    
    if (isSupabaseData) {
      // Supabase 데이터 처리: 각 거래를 시간별로 집계
      console.log('📊 Supabase 데이터를 시간별로 집계 중...');
      
      // 먼저 각 거래를 파싱
      const transactions = whaleData
        .map((row: any) => {
          if (!row.block_timestamp && row.block_timestamp !== 0) return null;
          
          // block_timestamp가 숫자 또는 문자열일 수 있음
          const ts = parseTimestamp(row.block_timestamp);
          if (!ts) return null;
          
          const amountUsd = parseFloat(row.amount_usd || '0') || 0;
          
          return {
            timestamp: ts,
            amount_usd: amountUsd,
          };
        })
        .filter((x: any) => x !== null);
      
      console.log(`  파싱된 거래: ${transactions.length}개`);
      
      // 11월 1일~8일 거래만 필터링하여 확인
      const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
      const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
      const novTransactions = transactions.filter((tx: any) => {
        const ts = tx.timestamp.getTime();
        return ts >= nov1Start && ts <= nov8End;
      });
      console.log(`  📅 11월 1일~8일 거래: ${novTransactions.length}개`);
      
      // 시간별로 그룹화하여 집계
      const hourlyMap = new Map<string, { count: number; volume: number }>();
      
      transactions.forEach((tx: any) => {
        const txDate = new Date(tx.timestamp);
        txDate.setMinutes(0, 0, 0);
        txDate.setSeconds(0, 0);
        txDate.setMilliseconds(0);
        const hourKey = txDate.toISOString();
        
        const existing = hourlyMap.get(hourKey);
        if (existing) {
          existing.count += 1;
          existing.volume += tx.amount_usd;
        } else {
          hourlyMap.set(hourKey, {
            count: 1,
            volume: tx.amount_usd,
          });
        }
      });
      
      // 11월 1일~8일 시간대별 집계 확인
      const novHourlyMap = new Map<string, { count: number; volume: number }>();
      novTransactions.forEach((tx: any) => {
        const txDate = new Date(tx.timestamp);
        txDate.setMinutes(0, 0, 0);
        txDate.setSeconds(0, 0);
        txDate.setMilliseconds(0);
        const hourKey = txDate.toISOString();
        
        const existing = novHourlyMap.get(hourKey);
        if (existing) {
          existing.count += 1;
          existing.volume += tx.amount_usd;
        } else {
          novHourlyMap.set(hourKey, {
            count: 1,
            volume: tx.amount_usd,
          });
        }
      });
      
      // 일별 집계 확인
      const novDailyMap = new Map<string, number>();
      novTransactions.forEach((tx: any) => {
        const date = new Date(tx.timestamp);
        const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        novDailyMap.set(dateKey, (novDailyMap.get(dateKey) || 0) + 1);
      });
      console.log(`  📊 11월 1일~8일 일별 거래 건수:`);
      Array.from(novDailyMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .forEach(([date, count]) => {
          console.log(`    ${date}: ${count}건`);
        });
      
      // 집계된 데이터를 processedWhale 형식으로 변환
      processedWhale = Array.from(hourlyMap.entries())
        .map(([hourKey, stats]) => ({
          timestamp: new Date(hourKey),
          tx_count: stats.count,
          volume_sum: stats.volume,
        }))
        .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());
      
      console.log(`  시간별 집계 완료: ${processedWhale.length}개 시간대`);
      const novProcessedWhale = processedWhale.filter((w: any) => {
        const ts = w.timestamp.getTime();
        return ts >= nov1Start && ts <= nov8End;
      });
      console.log(`  📅 11월 1일~8일 시간별 집계: ${novProcessedWhale.length}개 시간대, 총 ${novProcessedWhale.reduce((sum, w) => sum + w.tx_count, 0)}건`);
    } else {
      // CSV 데이터 처리 (기존 로직)
      processedWhale = whaleData
      .map((row: any) => {
          // #VALUE! 같은 오류 값 필터링
          if (!row.Time || row.Time === '#VALUE!' || row.Time === '') {
            return null;
          }
          
        const ts = parseTimestamp(row.Time || row.timestamp);
          if (!ts) {
            return null;
          }

          // frequency 컬럼명 확인 (대소문자 구분 없이)
          const txCount = parseFloat(row.frequency || row.Frequency || row.tx_frequency || '0') || 0;

        return {
          timestamp: ts,
            tx_count: txCount,
            volume_sum: parseFloat(row.sum_amount_usd || row.sum_amount_USD || row.tx_amount_usd || '0') || 0,
        };
      })
      .filter((x: any) => x !== null)
      .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());
    }
    
    // 11월 1일~8일 데이터만 필터링하여 확인
    const novWhale = processedWhale.filter((w: any) => {
      const ts = w.timestamp.getTime();
      const nov1 = new Date('2025-11-01T00:00:00.000Z').getTime();
      const nov8 = new Date('2025-11-08T23:59:59.999Z').getTime();
      return ts >= nov1 && ts <= nov8;
    });
    console.log(`고래 거래 데이터 처리: ${processedWhale.length}개 (원본: ${whaleData.length}개)`);
    console.log(`  11월 1일~8일 고래 거래 데이터: ${novWhale.length}개`);
    if (novWhale.length > 0) {
      console.log(`  첫 번째: ${novWhale[0].timestamp.toISOString()} - ${novWhale[0].tx_count}건`);
      console.log(`  마지막: ${novWhale[novWhale.length - 1].timestamp.toISOString()} - ${novWhale[novWhale.length - 1].tx_count}건`);
    }
    
    console.log(`고래 거래 데이터 처리: ${processedWhale.length}개 (원본: ${whaleData.length}개)`);

    // BTC 가격 데이터 처리
    const processedBtc = btcPriceData
      .map((row: any) => {
        const ts = parseTimestamp(row.timestamp || row.Time || row.date);
        if (!ts) return null;

        // close_price 컬럼명 추가 (실제 CSV 파일 컬럼명)
        const price = parseFloat(row.close_price || row.close || row.price || row.Close || '0');
        if (!price || price === 0) return null;

        // 날짜 필터링은 나중에 적용 (데이터가 있으면 최신부터 표시)
        return {
          timestamp: ts,
          close: price,
        };
      })
      .filter((x: any) => x !== null)
      .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());

    // ETH 가격 데이터 처리
    const processedEth = ethPriceData
      .map((row: any) => {
        const ts = parseTimestamp(row.timestamp || row.Time || row.date);
        if (!ts) return null;

        // close_price 컬럼명 추가 (실제 CSV 파일 컬럼명)
        const price = parseFloat(row.close_price || row.close || row.price || row.Close || '0');
        if (!price || price === 0) return null;

        // 날짜 필터링은 나중에 적용 (데이터가 있으면 최신부터 표시)
        return {
          timestamp: ts,
          close: price,
        };
      })
      .filter((x: any) => x !== null)
      .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());

    // 시간별로 그룹화 (1시간 단위)
    const timeMap = new Map<string, ChartDataPoint>();

    // 고래 거래 데이터 추가
    let whaleAddedCount = 0;
    processedWhale.forEach((whale: any) => {
      // 시간을 정규화하여 매칭 (BTC/ETH와 동일한 형식으로)
      const whaleDate = new Date(whale.timestamp);
      whaleDate.setMinutes(0, 0, 0);
      whaleDate.setSeconds(0, 0);
      whaleDate.setMilliseconds(0);
      // BTC/ETH와 동일한 형식: "YYYY-MM-DDTHH:00:00.000Z"
      const hourKey = whaleDate.toISOString().slice(0, 13) + ':00:00.000Z';
      const existing = timeMap.get(hourKey);
      
      if (existing) {
        existing.whale_tx_count += whale.tx_count;
        existing.whale_volume_sum += whale.volume_sum;
        whaleAddedCount++;
      } else {
        timeMap.set(hourKey, {
          timestamp: hourKey,
          date: whaleDate.toLocaleDateString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            ...(range === '90d' ? {} : { hour: '2-digit' }),
          }),
          whale_tx_count: whale.tx_count,
          whale_volume_sum: whale.volume_sum,
          btc_close: 0,
          eth_close: 0,
          btc_change: 0,
          eth_change: 0,
        });
        whaleAddedCount++;
      }
    });
    
    console.log(`고래 거래 데이터 timeMap 추가: ${whaleAddedCount}개 항목 추가됨`);
    console.log(`  timeMap 총 항목: ${timeMap.size}개, 고래 데이터 있는 항목: ${Array.from(timeMap.values()).filter(p => p.whale_tx_count > 0).length}개`);
    if (processedWhale.length > 0 && processedWhale.length <= 5) {
      processedWhale.forEach((w, i) => {
        const d = new Date(w.timestamp);
        d.setMinutes(0, 0, 0);
        d.setSeconds(0, 0);
        d.setMilliseconds(0);
        const key = d.toISOString().slice(0, 13) + ':00:00.000Z';
        console.log(`  샘플 ${i+1}: ${w.timestamp.toISOString()} -> ${key}, ${w.tx_count}건`);
      });
    }

    // BTC 가격 데이터 추가
    processedBtc.forEach((btc: any, idx: number) => {
      // 시간을 정규화하여 매칭 (고래 거래와 동일한 형식)
      const btcDate = new Date(btc.timestamp);
      btcDate.setMinutes(0, 0, 0);
      btcDate.setSeconds(0, 0);
      const hourKey = btcDate.toISOString().slice(0, 13) + ':00:00.000Z';
      const existing = timeMap.get(hourKey);
      const prevPrice = idx > 0 ? processedBtc[idx - 1].close : btc.close;

      if (existing) {
        existing.btc_close = btc.close;
        existing.btc_change = calculateChange(btc.close, prevPrice);
      } else {
        timeMap.set(hourKey, {
          timestamp: hourKey,
          date: btcDate.toLocaleDateString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            ...(range === '90d' ? {} : { hour: '2-digit' }),
          }),
          whale_tx_count: 0,
          whale_volume_sum: 0,
          btc_close: btc.close,
          eth_close: 0,
          btc_change: calculateChange(btc.close, prevPrice),
          eth_change: 0,
        });
      }
    });

    // ETH 가격 데이터 추가
    processedEth.forEach((eth: any, idx: number) => {
      // 시간을 정규화하여 매칭 (고래 거래와 동일한 형식)
      const ethDate = new Date(eth.timestamp);
      ethDate.setMinutes(0, 0, 0);
      ethDate.setSeconds(0, 0);
      const hourKey = ethDate.toISOString().slice(0, 13) + ':00:00.000Z';
      const existing = timeMap.get(hourKey);
      const prevPrice = idx > 0 ? processedEth[idx - 1].close : eth.close;

      if (existing) {
        existing.eth_close = eth.close;
        existing.eth_change = calculateChange(eth.close, prevPrice);
      } else {
        timeMap.set(hourKey, {
          timestamp: hourKey,
          date: ethDate.toLocaleDateString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            ...(range === '90d' ? {} : { hour: '2-digit' }),
          }),
          whale_tx_count: 0,
          whale_volume_sum: 0,
          btc_close: 0,
          eth_close: eth.close,
          btc_change: 0,
          eth_change: calculateChange(eth.close, prevPrice),
        });
      }
    });

    // 배열로 변환하고 정렬
    let result: ChartDataPoint[] = Array.from(timeMap.values())
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .filter((point) => {
        // 최소한 하나의 데이터가 있어야 함
        return point.whale_tx_count > 0 || point.btc_close > 0 || point.eth_close > 0;
      });

    // 날짜 필터링 적용
    // 11월 1일~8일 데이터를 기본으로 포함하도록 설정
    if (result.length > 0) {
      // 11월 1일~8일 범위 정의
      const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
      const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
      
      // 고래 거래 데이터가 있는 항목과 11월 1일~8일 데이터는 항상 포함
      const whalePoints = result.filter(p => p.whale_tx_count > 0);
      const novRangePoints = result.filter((point) => {
        const pointDate = new Date(point.timestamp).getTime();
        return pointDate >= nov1Start && pointDate <= nov8End;
      });
      
      // 나머지 데이터는 날짜 필터링 적용
      const latestDate = new Date(result[result.length - 1].timestamp);
      const startDate = new Date(latestDate);
      startDate.setDate(startDate.getDate() - days);
      
      const otherPoints = result.filter((point) => {
        const pointDate = new Date(point.timestamp).getTime();
        // 이미 포함된 항목은 제외
        const isWhale = point.whale_tx_count > 0;
        const isNovRange = pointDate >= nov1Start && pointDate <= nov8End;
        if (isWhale || isNovRange) return false;
        // 나머지는 날짜 필터링 적용
        return pointDate >= startDate.getTime();
      });
      
      // 모든 데이터 합치기 (중복 제거)
      const allPoints = [...whalePoints, ...novRangePoints, ...otherPoints];
      const uniquePoints = Array.from(
        new Map(allPoints.map(p => [p.timestamp, p])).values()
      );
      
      result = uniquePoints.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    }
    
    console.log(`날짜 필터링 후: ${result.length}개 항목, 고래 거래 데이터 있는 항목: ${result.filter(p => p.whale_tx_count > 0).length}개`);
    const novDataCheck = result.filter(p => {
      const ts = new Date(p.timestamp).getTime();
      return ts >= new Date('2025-11-01T00:00:00.000Z').getTime() && 
             ts <= new Date('2025-11-08T23:59:59.999Z').getTime();
    });
    console.log(`  11월 1일~8일 데이터: ${novDataCheck.length}개`);

    // 최신 데이터부터 반환 (내림차순 정렬)
    const sortedResult = result.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    // 고래 거래 데이터가 포함된 항목 개수 확인
    const whaleDataCount = sortedResult.filter(p => p.whale_tx_count > 0).length;
    
    console.log(`Timeseries API: ${sortedResult.length}개 데이터 반환`);
    console.log(`  고래 데이터: ${processedWhale.length}개 (병합 후 ${whaleDataCount}개 시간대에 포함)`);
    console.log(`  BTC 데이터: ${processedBtc.length}개`);
    console.log(`  ETH 데이터: ${processedEth.length}개`);
    if (sortedResult.length > 0) {
      console.log(`  최신: ${sortedResult[0]?.timestamp}`);
      console.log(`  최 old: ${sortedResult[sortedResult.length - 1]?.timestamp}`);
      // 샘플 데이터 확인
      const sampleWithWhale = sortedResult.find(p => p.whale_tx_count > 0);
      if (sampleWithWhale) {
        console.log(`  고래 거래 샘플: ${sampleWithWhale.timestamp} - ${sampleWithWhale.whale_tx_count}건`);
      } else {
        console.warn(`  ⚠️ 고래 거래 데이터가 포함된 항목이 없습니다!`);
      }
    }

    // 11월 1일~8일 데이터가 있으면 원본 거래 데이터로부터 일별 집계
    const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
    const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
    
    const novData = sortedResult.filter(p => {
      const ts = new Date(p.timestamp).getTime();
      return ts >= nov1Start && ts <= nov8End;
    });
    
    if (novData.length > 0 && isSupabaseData) {
      console.log(`📅 11월 1일~8일 데이터 발견: ${novData.length}개 시간대, 원본 거래 데이터로 일별 집계 시작...`);
      
      // 원본 거래 데이터에서 11월 1일~8일 데이터를 일별로 직접 집계
      const novTransactions = whaleData
        .map((row: any) => {
          if (!row.block_timestamp && row.block_timestamp !== 0) return null;
          const ts = parseTimestamp(row.block_timestamp);
          if (!ts) return null;
          const tsTime = ts.getTime();
          if (tsTime < nov1Start || tsTime > nov8End) return null;
          
          const amountUsd = parseFloat(row.amount_usd || '0') || 0;
          return {
            timestamp: ts,
            amount_usd: amountUsd,
          };
        })
        .filter((x: any) => x !== null);
      
      console.log(`  원본 거래 데이터에서 11월 1일~8일: ${novTransactions.length}개 거래 발견`);
      
      // 일별로 그룹화
      const dailyMap = new Map<string, {
        whale_tx_count: number;
        whale_volume_sum: number;
        btc_close: number;
        eth_close: number;
        btc_change: number;
        eth_change: number;
        btc_samples: number[];
        eth_samples: number[];
      }>();
      
      novTransactions.forEach((tx: any) => {
        const date = new Date(tx.timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateKey = `${year}-${month}-${day}`;
        
        const existing = dailyMap.get(dateKey);
        if (existing) {
          existing.whale_tx_count += 1;
          existing.whale_volume_sum += tx.amount_usd;
        } else {
          dailyMap.set(dateKey, {
            whale_tx_count: 1,
            whale_volume_sum: tx.amount_usd,
            btc_close: 0,
            eth_close: 0,
            btc_change: 0,
            eth_change: 0,
            btc_samples: [],
            eth_samples: [],
          });
        }
      });
      
      // BTC/ETH 가격 데이터를 일별로 매칭
      novData.forEach(p => {
        const date = new Date(p.timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateKey = `${year}-${month}-${day}`;
        
        const daily = dailyMap.get(dateKey);
        if (daily) {
          if (p.btc_close > 0) daily.btc_samples.push(p.btc_close);
          if (p.eth_close > 0) daily.eth_samples.push(p.eth_close);
          daily.btc_change = p.btc_change || daily.btc_change;
          daily.eth_change = p.eth_change || daily.eth_change;
        }
      });
      
      // 일별 데이터를 ChartDataPoint 형식으로 변환
      const dailyResult: ChartDataPoint[] = Array.from(dailyMap.entries())
        .map(([dateKey, stats]) => {
          const [year, month, day] = dateKey.split('-');
          return {
            timestamp: `${dateKey}T12:00:00.000Z`,
            date: `${parseInt(month)}/${parseInt(day)}`,
            whale_tx_count: stats.whale_tx_count,
            whale_volume_sum: stats.whale_volume_sum,
            btc_close: stats.btc_samples.length > 0 
              ? stats.btc_samples.reduce((a, b) => a + b, 0) / stats.btc_samples.length 
              : 0,
            eth_close: stats.eth_samples.length > 0 
              ? stats.eth_samples.reduce((a, b) => a + b, 0) / stats.eth_samples.length 
              : 0,
            btc_change: stats.btc_change,
            eth_change: stats.eth_change,
          };
        })
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      console.log(`✅ 원본 거래 데이터로 일별 집계 완료: ${dailyResult.length}일`);
      dailyResult.forEach(d => {
        console.log(`  ${d.date}: ${d.whale_tx_count}건`);
      });
      
      // 나머지 데이터와 합치기 (11월 1일~8일 제외)
      const otherData = sortedResult.filter(p => {
        const ts = new Date(p.timestamp).getTime();
        return ts < nov1Start || ts > nov8End;
      });
      
      // 일별 데이터를 최신순으로 정렬하고 나머지 데이터와 합치기
      const finalResult = [
        ...dailyResult.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()),
        ...otherData
      ];
      
      return NextResponse.json(finalResult);
    } else if (novData.length > 0) {
      // CSV 데이터인 경우 기존 로직 사용
      console.log(`📅 11월 1일~8일 데이터 발견: ${novData.length}개 시간대, 일별 집계 시작...`);
      
      // 일별로 그룹화
      const dailyMap = new Map<string, ChartDataPoint>();
      
      novData.forEach(p => {
        const date = new Date(p.timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateKey = `${year}-${month}-${day}`;
        
        const existing = dailyMap.get(dateKey);
        if (existing) {
          existing.whale_tx_count += p.whale_tx_count;
          existing.whale_volume_sum += p.whale_volume_sum;
          existing.btc_close = p.btc_close || existing.btc_close;
          existing.eth_close = p.eth_close || existing.eth_close;
          existing.btc_change = p.btc_change || existing.btc_change;
          existing.eth_change = p.eth_change || existing.eth_change;
        } else {
          dailyMap.set(dateKey, {
            timestamp: `${dateKey}T12:00:00.000Z`,
            date: `${date.getMonth() + 1}/${date.getDate()}`,
            whale_tx_count: p.whale_tx_count,
            whale_volume_sum: p.whale_volume_sum,
            btc_close: p.btc_close,
            eth_close: p.eth_close,
            btc_change: p.btc_change,
            eth_change: p.eth_change,
          });
        }
      });
      
      const dailyResult = Array.from(dailyMap.values())
        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      
      console.log(`✅ 일별 집계 완료: ${dailyResult.length}일`);
      dailyResult.forEach(d => {
        console.log(`  ${d.date}: ${d.whale_tx_count}건`);
      });
      
      // 나머지 데이터와 합치기 (11월 1일~8일 제외)
      const otherData = sortedResult.filter(p => {
        const ts = new Date(p.timestamp).getTime();
        return ts < nov1Start || ts > nov8End;
      });
      
      // 일별 데이터를 최신순으로 정렬하고 나머지 데이터와 합치기
      const finalResult = [
        ...dailyResult.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()),
        ...otherData
      ];
      
      return NextResponse.json(finalResult);
    }

    return NextResponse.json(sortedResult);
  } catch (error: any) {
    console.error('Timeseries 데이터 로딩 오류:', error);
    return NextResponse.json(
      { error: error.message || '데이터 로딩 실패' },
      { status: 500 }
    );
  }
}


