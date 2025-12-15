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
  const possiblePaths = [
    path.join(process.cwd(), '..', 'data', relativeFile),
    path.join(process.cwd(), '../../data', relativeFile),
    path.join(process.cwd(), 'data', relativeFile),
  ];

  for (const fullPath of possiblePaths) {
    if (fs.existsSync(fullPath)) {
      const text = fs.readFileSync(fullPath, 'utf-8');
      return parse(text, {
        columns: true,
        skip_empty_lines: true,
      });
    }
  }

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
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

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
      if (!ts) return null;
      try {
        const date = new Date(ts);
        return isNaN(date.getTime()) ? null : date;
      } catch {
        return null;
      }
    };

    // 고래 거래 데이터 처리
    const processedWhale = whaleData
      .map((row: any) => {
        const ts = parseTimestamp(row.Time || row.timestamp);
        if (!ts || ts < cutoffDate) return null;

        return {
          timestamp: ts,
          tx_count: parseFloat(row.frequency || row.tx_frequency || '0') || 0,
          volume_sum: parseFloat(row.sum_amount_usd || row.tx_amount_usd || '0') || 0,
        };
      })
      .filter((x: any) => x !== null)
      .sort((a: any, b: any) => a.timestamp.getTime() - b.timestamp.getTime());

    // BTC 가격 데이터 처리
    const processedBtc = btcPriceData
      .map((row: any) => {
        const ts = parseTimestamp(row.timestamp || row.Time || row.date);
        if (!ts || ts < cutoffDate) return null;

        const price = parseFloat(row.close || row.price || row.Close || '0');
        if (!price || price === 0) return null;

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
        if (!ts || ts < cutoffDate) return null;

        const price = parseFloat(row.close || row.price || row.Close || '0');
        if (!price || price === 0) return null;

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
      const hourKey = new Date(whale.timestamp).toISOString().slice(0, 13) + ':00:00';
      const existing = timeMap.get(hourKey);
      
      if (existing) {
        existing.whale_tx_count += whale.tx_count;
        existing.whale_volume_sum += whale.volume_sum;
      } else {
        const ts = new Date(hourKey);
        timeMap.set(hourKey, {
          timestamp: ts.toISOString(),
          date: ts.toLocaleDateString('ko-KR', {
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
      const hourKey = new Date(btc.timestamp).toISOString().slice(0, 13) + ':00:00';
      const existing = timeMap.get(hourKey);
      const prevPrice = idx > 0 ? processedBtc[idx - 1].close : btc.close;

      if (existing) {
        existing.btc_close = btc.close;
        existing.btc_change = calculateChange(btc.close, prevPrice);
      } else {
        const ts = new Date(hourKey);
        timeMap.set(hourKey, {
          timestamp: ts.toISOString(),
          date: ts.toLocaleDateString('ko-KR', {
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
      const hourKey = new Date(eth.timestamp).toISOString().slice(0, 13) + ':00:00';
      const existing = timeMap.get(hourKey);
      const prevPrice = idx > 0 ? processedEth[idx - 1].close : eth.close;

      if (existing) {
        existing.eth_close = eth.close;
        existing.eth_change = calculateChange(eth.close, prevPrice);
      } else {
        const ts = new Date(hourKey);
        timeMap.set(hourKey, {
          timestamp: ts.toISOString(),
          date: ts.toLocaleDateString('ko-KR', {
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

    // 배열로 변환하고 정렬 (최신 데이터부터)
    const result: ChartDataPoint[] = Array.from(timeMap.values())
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .filter((point) => {
        // 최소한 하나의 데이터가 있어야 함
        return point.whale_tx_count > 0 || point.btc_close > 0 || point.eth_close > 0;
      });

    // 최신 데이터부터 반환 (내림차순 정렬)
    const sortedResult = result.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    console.log(`Timeseries API: ${sortedResult.length}개 데이터 반환 (최신: ${sortedResult[0]?.timestamp}, 최 old: ${sortedResult[sortedResult.length - 1]?.timestamp})`);

    return NextResponse.json(sortedResult);
  } catch (error: any) {
    console.error('Timeseries 데이터 로딩 오류:', error);
    return NextResponse.json(
      { error: error.message || '데이터 로딩 실패' },
      { status: 500 }
    );
  }
}


