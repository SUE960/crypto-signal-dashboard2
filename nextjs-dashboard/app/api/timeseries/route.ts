import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = searchParams.get('range') || '30d';

    // CSV 파일 경로 찾기
    const possiblePaths = [
      path.join(process.cwd(), '../../data/final_integrated_data.csv'),
      path.join(process.cwd(), '../data/final_integrated_data.csv'),
      path.join(process.cwd(), 'data/final_integrated_data.csv'),
    ];
    
    let dataPath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        dataPath = p;
        break;
      }
    }
    
    if (!dataPath) {
      console.log('통합 데이터 파일을 찾을 수 없습니다.');
      return NextResponse.json([]);
    }

    // CSV 파일 읽기
    const fileContent = fs.readFileSync(dataPath, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });

    // 시간 범위에 따라 필터링
    const now = new Date();
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

    const filteredData = records
      .filter((record: any) => {
        if (!record.timestamp) return false;
        const recordDate = new Date(record.timestamp);
        return recordDate >= cutoffDate;
      })
      .map((record: any) => ({
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
      }))
      .filter((item: any) => item.btc_close > 0 || item.eth_close > 0); // 유효한 데이터만

    return NextResponse.json(filteredData);
  } catch (error) {
    console.error('Error loading timeseries data:', error);
    return NextResponse.json({ error: 'Failed to load data' }, { status: 500 });
  }
}

