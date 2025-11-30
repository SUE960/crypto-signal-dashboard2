import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');

    // CSV 파일 경로 찾기
    const possiblePaths = [
      path.join(process.cwd(), '../../data/coinness_data2_preprocessed.csv'),
      path.join(process.cwd(), '../../data/coinness_data2.csv'),
      path.join(process.cwd(), '../data/coinness_data2_preprocessed.csv'),
      path.join(process.cwd(), '../data/coinness_data2.csv'),
      path.join(process.cwd(), 'data/coinness_data2.csv'),
    ];
    
    let dataPath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        dataPath = p;
        break;
      }
    }
    
    if (!dataPath) {
      console.log('뉴스 데이터 파일을 찾을 수 없습니다.');
      return NextResponse.json([]);
    }

    // CSV 파일 읽기
    const fileContent = fs.readFileSync(dataPath, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      encoding: 'utf-8'
    });

    // 최신순으로 정렬
    const sortedRecords = records
      .filter((record: any) => record.timestamp && record.title)
      .sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp).getTime();
        const dateB = new Date(b.timestamp).getTime();
        return dateB - dateA; // 최신순
      })
      .slice(0, limit)
      .map((record: any) => ({
        timestamp: record.timestamp,
        title: record.title,
        content: record.content || '',
        link: record.link || '#',
        sentiment_compound: parseFloat(record.sentiment_compound) || 0,
        sentiment_positive: parseFloat(record.sentiment_positive) || 0,
        sentiment_negative: parseFloat(record.sentiment_negative) || 0,
        sentiment_neutral: parseFloat(record.sentiment_neutral) || 0,
        has_bitcoin: record.has_bitcoin === 'True' || record.has_bitcoin === '1' || 
                     (record.title && (record.title.includes('비트코인') || record.title.includes('BTC'))),
        has_ethereum: record.has_ethereum === 'True' || record.has_ethereum === '1' ||
                      (record.title && (record.title.includes('이더리움') || record.title.includes('ETH'))),
        has_bullish: record.has_bullish === 'True' || record.has_bullish === '1' ||
                     (record.title && (record.title.includes('급등') || record.title.includes('상승') || record.title.includes('강세'))),
        has_bearish: record.has_bearish === 'True' || record.has_bearish === '1' ||
                     (record.title && (record.title.includes('급락') || record.title.includes('하락') || record.title.includes('약세'))),
      }));

    return NextResponse.json(sortedRecords);
  } catch (error) {
    console.error('Error loading news:', error);
    return NextResponse.json({ error: 'Failed to load news' }, { status: 500 });
  }
}

