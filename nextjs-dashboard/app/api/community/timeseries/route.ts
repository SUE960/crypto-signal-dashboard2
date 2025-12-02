import { NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

function loadCSV(relativeFile: string) {
  // nextjs-dashboard -> 상위 폴더 -> data -> 파일
  const fullPath = path.join(process.cwd(), '..', 'data', relativeFile);

  if (!fs.existsSync(fullPath)) {
    throw new Error(`CSV file not found: ${fullPath}`);
  }

  const text = fs.readFileSync(fullPath, 'utf-8');
  return parse(text, {
    columns: true,
    skip_empty_lines: true,
  });
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const freq = searchParams.get('freq') || '1h';
  const coin = searchParams.get('coin') || 'BTC';

  // 감성 ts 파일 매핑
  const sentimentFiles: Record<string, string> = {
    '1h': 'community_ts_1h.csv',
    '4h': 'community_ts_4h.csv',
    '1d': 'community_ts_1d.csv',
  };

  const sentimentFile = sentimentFiles[freq];
  if (!sentimentFile) {
    return NextResponse.json(
      { error: 'Invalid freq. Use 1h | 4h | 1d' },
      { status: 400 }
    );
  }

  // 가격 파일 선택
  const priceFile =
    coin === 'ETH'
      ? 'price_history_eth_rows.csv'
      : 'price_history_btc_rows.csv';

  try {
    const sentiment = loadCSV(sentimentFile);
    const price = loadCSV(priceFile);

    return NextResponse.json({
      sentiment,
      price,
      meta: {
        freq,
        coin,
        sentimentRows: sentiment.length,
        priceRows: price.length,
      },
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
