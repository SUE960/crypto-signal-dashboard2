import { NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

function loadCSV(relativeFile: string) {
  // nextjs-dashboard 기준 상위 폴더의 data 디렉터리
  const fullPath = path.join(process.cwd(), '..', 'data', relativeFile);

  if (!fs.existsSync(fullPath)) {
    throw new Error(`CSV file not found: ${fullPath}`);
  }

  const text = fs.readFileSync(fullPath, 'utf-8');
  return parse(text, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  }) as any[];
}

// '2024-11-15 13:00:00+00:00' 같은 포맷을 ISO로 정규화
function normalizeDate(value: string): string {
  let s = value;
  if (s.includes(' ') && !s.includes('T')) {
    s = s.replace(' ', 'T');
  }
  if (s.endsWith('+00:00')) {
    s = s.replace('+00:00', 'Z');
  }
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) {
    return value;
  }
  return d.toISOString();
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const freq = searchParams.get('freq') || '1h';
    const coin = searchParams.get('coin') || 'BTC';
    const thresholdParam = searchParams.get('threshold') || '2.0';

    const threshold =
      thresholdParam === '2.5' ? 2.5 : thresholdParam === '3.0' ? 3.0 : 2.0;

    const spikeCol =
      threshold === 2.0
        ? 'spike_2_0'
        : threshold === 2.5
        ? 'spike_2_5'
        : 'spike_3_0';

    // 현재는 1h 기준 스파이크만 존재한다고 가정
    const rows = loadCSV('community_spike_events.csv');

    const spikes = rows
      .filter((row) => {
        const flag = row[spikeCol];
        if (flag === undefined || flag === null) return false;
        const s = String(flag).toLowerCase();
        return s === 'true' || s === '1';
      })
      .map((row) => {
        const tsRaw = row['post_date'];
        return {
          timestamp: tsRaw,
          normalized_time: normalizeDate(tsRaw),
          avg_sentiment: Number(row['avg_sentiment'] ?? 0),
          variance: Number(row['variance'] ?? 0),
          total_posts: Number(row['total_posts'] ?? 0),
          pos: Number(row['pos'] ?? 0),
          neg: Number(row['neg'] ?? 0),
          neu: Number(row['neu'] ?? 0),
          diff: Number(row['diff'] ?? 0),
          zscore: Number(row['zscore'] ?? 0),
          threshold,
        };
      });

    return NextResponse.json({
      spikes,
      meta: {
        freq,
        coin,
        threshold,
        count: spikes.length,
      },
    });
  } catch (err: any) {
    console.error('spikes API error', err);
    return NextResponse.json(
      { error: err?.message || 'Internal error' },
      { status: 500 }
    );
  }
}
