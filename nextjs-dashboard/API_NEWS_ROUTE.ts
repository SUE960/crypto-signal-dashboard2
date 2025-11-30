// API 라우트: app/api/news/recent/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');

    // CSV 파일 경로
    const csvPath = path.join(process.cwd(), '../data/coinness_data2_preprocessed.csv');
    
    // CSV 파일 읽기
    const fileContent = fs.readFileSync(csvPath, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });

    // 최신순으로 정렬
    const sortedRecords = records
      .sort((a: any, b: any) => {
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      })
      .slice(0, limit)
      .map((record: any) => ({
        timestamp: record.timestamp,
        title: record.title,
        content: record.content,
        link: record.link,
        sentiment_compound: parseFloat(record.sentiment_compound) || 0,
        sentiment_positive: parseFloat(record.sentiment_positive) || 0,
        sentiment_negative: parseFloat(record.sentiment_negative) || 0,
        sentiment_neutral: parseFloat(record.sentiment_neutral) || 0,
        has_bitcoin: record.has_bitcoin === 'True' || record.has_bitcoin === '1',
        has_ethereum: record.has_ethereum === 'True' || record.has_ethereum === '1',
        has_bullish: record.has_bullish === 'True' || record.has_bullish === '1',
        has_bearish: record.has_bearish === 'True' || record.has_bearish === '1',
      }));

    return NextResponse.json(sortedRecords);
  } catch (error) {
    console.error('Error loading news:', error);
    return NextResponse.json({ error: 'Failed to load news' }, { status: 500 });
  }
}

