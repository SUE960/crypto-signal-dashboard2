// app/api/community/top-posts/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import papa from 'papaparse';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);

  const sentiment = searchParams.get('sentiment') || 'all';
  const page = Number(searchParams.get('page') || 1);

  const range = searchParams.get('range') || '7d';
  const customFrom = searchParams.get('from');
  const customTo = searchParams.get('to');

  const filePath = path.join(
    process.cwd(),
    '../data/community_top_posts_daily.csv'
  );

  if (!fs.existsSync(filePath)) {
    return NextResponse.json({ error: 'File not found' });
  }

  const file = fs.readFileSync(filePath, 'utf8');
  const parsed = papa.parse(file, { header: true });
  let rows = parsed.data as any[];

  // 날짜 필드 정규화
  rows = rows
    .map((r) => ({
      ...r,
      post_date: r.post_date ? new Date(r.post_date) : null,
      comments: Number(r.comments),
      shares: Number(r.shares),
      likes: Number(r.likes),
      engagement_score: Number(r.engagement_score),
    }))
    .filter((r) => r.post_date);

  // ----------------------
  // 기간 필터링
  // ----------------------
  const now = new Date();
  let from = new Date();

  if (range === '7d') from.setDate(now.getDate() - 7);
  if (range === '30d') from.setDate(now.getDate() - 30);

  if (customFrom && customTo) {
    from = new Date(customFrom);
    now.setTime(new Date(customTo).getTime());
  }

  rows = rows.filter((r) => r.post_date >= from && r.post_date <= now);

  // ----------------------
  // sentiment 필터링
  // ----------------------
  if (sentiment !== 'all') {
    rows = rows.filter((r) => r.sentiment === sentiment);
  }

  // ----------------------
  // 중복 제거 (content + date 기준)
  // ----------------------
  const seen = new Set();
  rows = rows.filter((r) => {
    const key = `${r.post_content}_${r.post_date.toISOString()}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // ----------------------
  // 소팅 (내림차순: 가장 인기 많은 글이 위로)
  // ----------------------
  rows.sort((a, b) => b.engagement_score - a.engagement_score);

  const perPage = 5;
  const start = (page - 1) * perPage;
  const paged = rows.slice(start, start + perPage);

  return NextResponse.json({
    posts: paged,
    total: rows.length,
    page,
    perPage,
    from: from.toISOString(),
    to: now.toISOString(),
  });
}
