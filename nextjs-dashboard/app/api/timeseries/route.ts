import { NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

// 동적 렌더링 강제 (request.url 사용)
export const dynamic = 'force-dynamic';

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

    // CSV 파일 로드
    let whaleData: any[] = [];
    let btcPriceData: any[] = [];
    let ethPriceData: any[] = [];

    try {
      whaleData = loadCSV('whale_transactions_rows_ETH_rev1.csv');
    } catch (e) {
      console.warn('고래 거래 데이터 로드 실패:', e);
    }

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
    const parseTimestamp = (ts: string): Date | null => {
      if (!ts || ts === '#VALUE!' || ts.trim() === '') return null;
      try {
        // "2025-11-01 0:00" 형식 처리 (시간이 한 자리일 수 있음)
        let normalized = ts.toString().trim();
        
        // #VALUE! 같은 오류 값 필터링
        if (normalized.includes('#') || normalized.toLowerCase().includes('value')) {
          return null;
        }
        
        // "2025-11-01 0:00" -> "2025-11-01 00:00:00" 형식으로 변환
        if (normalized.match(/^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}$/)) {
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
    const processedWhale = whaleData
      .map((row: any) => {
        // #VALUE! 같은 오류 값 필터링
        if (!row.Time || row.Time === '#VALUE!' || row.Time === '') {
          return null;
        }
        
        const ts = parseTimestamp(row.Time || row.timestamp);
        if (!ts) return null;

        const txCount = parseFloat(row.frequency || row.tx_frequency || '0') || 0;
        // 거래 횟수가 0이어도 데이터는 포함 (나중에 필터링)
        
        return {
          timestamp: ts,
          tx_count: txCount,
          volume_sum: parseFloat(row.sum_amount_usd || row.tx_amount_usd || '0') || 0,
        };
      })
      .filter((x: any) => x !== null)
      .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());
    
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
    processedWhale.forEach((whale: any) => {
      // 시간을 정규화하여 매칭 (분과 초를 0으로 설정)
      const whaleDate = new Date(whale.timestamp);
      whaleDate.setMinutes(0, 0, 0);
      const hourKey = whaleDate.toISOString();
      const existing = timeMap.get(hourKey);
      
      if (existing) {
        existing.whale_tx_count += whale.tx_count;
        existing.whale_volume_sum += whale.volume_sum;
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
      }
    });

    // BTC 가격 데이터 추가
    processedBtc.forEach((btc: any, idx: number) => {
      // 시간을 정규화하여 매칭 (분과 초를 0으로 설정)
      const btcDate = new Date(btc.timestamp);
      btcDate.setMinutes(0, 0, 0);
      const hourKey = btcDate.toISOString();
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
      // 시간을 정규화하여 매칭 (분과 초를 0으로 설정)
      const ethDate = new Date(eth.timestamp);
      ethDate.setMinutes(0, 0, 0);
      const hourKey = ethDate.toISOString();
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

    // 날짜 필터링 적용 (최신 데이터부터 표시하되, 범위 내 데이터만)
    // 고래 거래 데이터가 있는 항목은 우선 표시
    if (result.length > 0) {
      const latestDate = new Date(result[result.length - 1].timestamp);
      const startDate = new Date(latestDate);
      startDate.setDate(startDate.getDate() - days);
      
      // 고래 거래 데이터가 있는 항목은 필터링에서 제외하지 않음 (최대 7일 범위)
      result = result.filter((point) => {
        const pointDate = new Date(point.timestamp);
        // 고래 거래 데이터가 있으면 최대 7일 범위 내에서 항상 포함
        if (point.whale_tx_count > 0) {
          const maxDaysAgo = new Date(latestDate);
          maxDaysAgo.setDate(maxDaysAgo.getDate() - 7);
          return pointDate >= maxDaysAgo;
        }
        // 고래 거래 데이터가 없으면 날짜 범위 내만 포함
        return pointDate >= startDate;
      });
    }

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

    return NextResponse.json(sortedResult);
  } catch (error: any) {
    console.error('Timeseries 데이터 로딩 오류:', error);
    return NextResponse.json(
      { error: error.message || '데이터 로딩 실패' },
      { status: 500 }
    );
  }
}


