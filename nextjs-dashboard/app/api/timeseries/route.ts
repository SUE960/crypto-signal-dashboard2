import { NextResponse } from 'next/server';
import { getTimeseriesData } from '@/lib/supabase';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = (searchParams.get('range') || '30d') as '7d' | '30d' | '90d';

    // Supabase에서 타임시리즈 데이터 가져오기
    const filteredData = await getTimeseriesData(range);

    return NextResponse.json(filteredData);
  } catch (error) {
    console.error('Error loading timeseries data:', error);
    return NextResponse.json({ error: 'Failed to load data' }, { status: 500 });
  }
}

