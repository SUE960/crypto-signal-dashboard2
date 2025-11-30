// API 라우트: /api/timeseries/route.ts
// 실제 데이터를 제공하는 API 엔드포인트

import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = searchParams.get('range') || '7d';

    // CSV 파일 경로
    const csvPath = path.join(process.cwd(), '../data/final_integrated_data.csv');
    
    // CSV 파일 읽기
    const fileContent = fs.readFileSync(csvPath, 'utf-8');
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
        const recordDate = new Date(record.timestamp);
        return recordDate >= cutoffDate;
      })
      .map((record: any) => ({
        timestamp: record.timestamp,
        date: new Date(record.timestamp).toLocaleDateString('ko-KR', {
          month: 'short',
          day: 'numeric'
        }),
        whale_tx_count: parseFloat(record.whale_tx_count) || 0,
        whale_volume_sum: parseFloat(record.whale_volume_sum) || 0,
        btc_close: parseFloat(record.btc_close) || 0,
        eth_close: parseFloat(record.eth_close) || 0,
        btc_change: parseFloat(record.btc_price_change) || 0,
        eth_change: parseFloat(record.eth_price_change) || 0,
      }));

    return NextResponse.json(filteredData);
  } catch (error) {
    console.error('Error loading data:', error);
    return NextResponse.json({ error: 'Failed to load data' }, { status: 500 });
  }
}

