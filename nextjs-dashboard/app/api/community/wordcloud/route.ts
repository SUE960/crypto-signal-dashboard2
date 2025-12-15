import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

function parseCSV(filePath: string): Promise<any[]> {
  return new Promise((resolve) => {
    const file = fs.readFileSync(filePath, 'utf-8');
    const { data } = Papa.parse(file, { header: true, skipEmptyLines: true });
    resolve(data);
  });
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const sentiment = searchParams.get('sentiment') || 'all';
  const range = searchParams.get('range') || '7d';
  const fromParam = searchParams.get('from');
  const toParam = searchParams.get('to');

  const dailyPath = path.resolve(
    process.cwd(),
    '..',
    'data',
    'community_keywords_daily.csv'
  );

  let rows = await parseCSV(dailyPath);

  rows = rows.map((r) => ({
    ...r,
    period: new Date(r.period),
    total_count: Number(r.total_count) || 0,
    positive: Number(r.positive) || 0,
    negative: Number(r.negative) || 0,
    neutral: Number(r.neutral) || 0,
  }));

  // 데이터의 가장 최근 날짜를 기준으로 계산
  const latestDate = rows.reduce((max, r) => {
    return r.period > max ? r.period : max;
  }, rows[0]?.period || new Date());

  let from: Date, to: Date;

  if (range === '7d') {
    to = new Date(latestDate);
    from = new Date(latestDate);
    from.setDate(to.getDate() - 7);
  } else if (range === '30d') {
    to = new Date(latestDate);
    from = new Date(latestDate);
    from.setDate(to.getDate() - 30);
  } else if (range === 'custom' && fromParam && toParam) {
    from = new Date(fromParam);
    to = new Date(toParam);
  } else {
    return NextResponse.json({ keywords: [], from: null, to: null });
  }

  const filtered = rows.filter((r) => r.period >= from && r.period <= to);

  let result = filtered;

  if (sentiment !== 'all') {
    result = result.filter((r) => r[sentiment] > 0);
  }

  const keywordMap: Record<
    string,
    { total_count: number; positive: number; negative: number; neutral: number }
  > = {};

  result.forEach((r) => {
    if (!keywordMap[r.word]) {
      keywordMap[r.word] = {
        total_count: 0,
        positive: 0,
        negative: 0,
        neutral: 0,
      };
    }

    keywordMap[r.word].total_count += r.total_count;
    keywordMap[r.word].positive += r.positive;
    keywordMap[r.word].negative += r.negative;
    keywordMap[r.word].neutral += r.neutral;
  });

  const keywords = Object.entries(keywordMap)
    .map(([word, counts]) => ({ word, ...counts }))
    .sort((a, b) => b.total_count - a.total_count)
    .slice(0, 100);

  return NextResponse.json({
    keywords,
    from: from.toISOString(),
    to: to.toISOString(),
  });
}
