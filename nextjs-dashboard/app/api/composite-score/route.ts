import { NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import * as fs from 'fs';
import * as path from 'path';

// CSV 파일 로드 함수
function loadCSV(relativeFile: string): any[] {
  const possiblePaths = [
    path.join(process.cwd(), 'data', relativeFile),
    path.join(process.cwd(), '..', 'data', relativeFile),
    path.join(process.cwd(), '../../data', relativeFile),
    path.join(process.cwd(), 'public/data', relativeFile),
  ];

  for (const fullPath of possiblePaths) {
    if (fs.existsSync(fullPath)) {
      const text = fs.readFileSync(fullPath, 'utf-8');
      const records = parse(text, {
        columns: true,
        skip_empty_lines: true,
      });
      return records;
    }
  }
  return [];
}

// 시간 정규화 함수 (시간 단위로)
function normalizeHour(timestamp: string): string {
  const date = new Date(timestamp);
  date.setMinutes(0, 0, 0);
  date.setMilliseconds(0);
  return date.toISOString();
}

export async function GET() {
  try {
    // 1. 텔레그램 데이터 로드 (community_ts_1h.csv)
    const telegramData = loadCSV('community_ts_1h.csv');
    
    // 2. 뉴스 데이터 로드 (coinness_data2.csv)
    const newsData = loadCSV('coinness_data2.csv');
    
    // 3. 트위터 데이터 로드 (twitter_influencer_labeled_rows.csv)
    const twitterData = loadCSV('twitter_influencer_labeled_rows.csv');
    
    // 11월 1일~8일 데이터만 필터링
    const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
    const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
    
    // 텔레그램 데이터 처리
    const telegramRecent = telegramData
      .filter((d: any) => {
        const ts = new Date(d.post_date).getTime();
        return ts >= nov1Start && ts <= nov8End;
      })
      .map((d: any) => ({
        timestamp: normalizeHour(d.post_date),
        total_posts: parseInt(d.total_posts) || 0,
        avg_sentiment: parseFloat(d.avg_sentiment) || 0,
        pos: parseInt(d.pos) || 0,
        neg: parseInt(d.neg) || 0,
      }));
    
    // 뉴스 데이터 처리
    const newsRecent = newsData
      .filter((d: any) => {
        const ts = new Date(d.timestamp).getTime();
        return ts >= nov1Start && ts <= nov8End;
      })
      .map((d: any) => ({
        timestamp: normalizeHour(d.timestamp),
        sentiment_compound: parseFloat(d.sentiment_compound) || 0,
        sentiment_positive: parseFloat(d.sentiment_positive) || 0,
        sentiment_negative: parseFloat(d.sentiment_negative) || 0,
      }));
    
    // 트위터 데이터 처리
    const twitterRecent = twitterData
      .filter((d: any) => {
        if (!d.post_date) return false;
        const ts = new Date(d.post_date).getTime();
        return ts >= nov1Start && ts <= nov8End;
      })
      .map((d: any) => ({
        timestamp: normalizeHour(d.post_date),
        likes: parseInt(d.likes) || 0,
        sentiment_score: parseFloat(d.sentiment_score) || 0,
      }));
    
    // 시간별로 집계
    const timeMap = new Map<string, {
      telegram: { posts: number; sentiment: number; pos: number; neg: number };
      news: { count: number; sentiment: number; positive: number; negative: number };
      twitter: { likes: number; sentiment: number; count: number };
    }>();
    
    // 텔레그램 데이터 집계
    telegramRecent.forEach((d: any) => {
      const key = d.timestamp;
      if (!timeMap.has(key)) {
        timeMap.set(key, {
          telegram: { posts: 0, sentiment: 0, pos: 0, neg: 0 },
          news: { count: 0, sentiment: 0, positive: 0, negative: 0 },
          twitter: { likes: 0, sentiment: 0, count: 0 },
        });
      }
      const entry = timeMap.get(key)!;
      entry.telegram.posts += d.total_posts;
      entry.telegram.sentiment += d.avg_sentiment;
      entry.telegram.pos += d.pos;
      entry.telegram.neg += d.neg;
    });
    
    // 뉴스 데이터 집계
    newsRecent.forEach((d: any) => {
      const key = d.timestamp;
      if (!timeMap.has(key)) {
        timeMap.set(key, {
          telegram: { posts: 0, sentiment: 0, pos: 0, neg: 0 },
          news: { count: 0, sentiment: 0, positive: 0, negative: 0 },
          twitter: { likes: 0, sentiment: 0, count: 0 },
        });
      }
      const entry = timeMap.get(key)!;
      entry.news.count += 1;
      entry.news.sentiment += d.sentiment_compound;
      entry.news.positive += d.sentiment_positive;
      entry.news.negative += d.sentiment_negative;
    });
    
    // 트위터 데이터 집계
    twitterRecent.forEach((d: any) => {
      const key = d.timestamp;
      if (!timeMap.has(key)) {
        timeMap.set(key, {
          telegram: { posts: 0, sentiment: 0, pos: 0, neg: 0 },
          news: { count: 0, sentiment: 0, positive: 0, negative: 0 },
          twitter: { likes: 0, sentiment: 0, count: 0 },
        });
      }
      const entry = timeMap.get(key)!;
      entry.twitter.likes += d.likes;
      entry.twitter.sentiment += d.sentiment_score;
      entry.twitter.count += 1;
    });
    
    // 평균 계산
    const aggregated = Array.from(timeMap.entries()).map(([timestamp, data]) => {
      const telegramAvg = data.telegram.posts > 0 
        ? data.telegram.sentiment / data.telegram.posts 
        : 0;
      const newsAvg = data.news.count > 0
        ? data.news.sentiment / data.news.count
        : 0;
      const twitterAvg = data.twitter.count > 0
        ? data.twitter.sentiment / data.twitter.count
        : 0;
      
      return {
        timestamp,
        telegram: {
          posts: data.telegram.posts,
          sentiment: telegramAvg,
          pos: data.telegram.pos,
          neg: data.telegram.neg,
        },
        news: {
          count: data.news.count,
          sentiment: newsAvg,
          positive: data.news.positive / data.news.count || 0,
          negative: data.news.negative / data.news.count || 0,
        },
        twitter: {
          likes: data.twitter.likes,
          sentiment: twitterAvg,
          count: data.twitter.count,
        },
      };
    });
    
    return NextResponse.json({
      success: true,
      data: aggregated.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      ),
    });
  } catch (error: any) {
    console.error('종합 점수 데이터 로드 실패:', error);
    return NextResponse.json({
      success: false,
      error: error.message,
      data: [],
    }, { status: 500 });
  }
}

