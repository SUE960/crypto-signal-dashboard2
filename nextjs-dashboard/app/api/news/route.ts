import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET() {
  try {
    // 코인니스 데이터 파일 경로 (프로젝트 루트 기준)
    // Vercel 배포 환경을 고려한 경로들
    const possiblePaths = [
      path.join(process.cwd(), 'data/coinness_data2.csv'),  // nextjs-dashboard/data/ (우선)
      path.join(process.cwd(), '../../data/coinness_data2.csv'),  // 프로젝트 루트/data/
      path.join(process.cwd(), '../data/coinness_data2.csv'),  // 상위 폴더/data/
      path.join(process.cwd(), 'public/data/coinness_data2.csv'),  // public 폴더
    ];
    
    let dataPath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        dataPath = p;
        break;
      }
    }
    
    // 파일이 없으면 빈 배열 반환
    if (!dataPath) {
      console.log('코인니스 데이터 파일을 찾을 수 없습니다.');
      return NextResponse.json({
        success: true,
        data: []
      });
    }

    // CSV 파일 읽기
    const fileContent = fs.readFileSync(dataPath, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      encoding: 'utf-8'
    });

    // 최신 뉴스부터 정렬 (timestamp 기준 내림차순)
    const sortedNews = records
      .filter((record: any) => record.timestamp && record.title && record.link)
      .sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp).getTime();
        const dateB = new Date(b.timestamp).getTime();
        return dateB - dateA; // 최신순
      })
      .slice(0, 20) // 최신 20개만
      .map((record: any) => ({
        timestamp: record.timestamp,
        title: record.title,
        content: record.content ? record.content.substring(0, 100) + '...' : '',
        link: record.link,
        sentiment: parseFloat(record.sentiment_compound) || 0
      }));

    return NextResponse.json({
      success: true,
      data: sortedNews
    });
  } catch (error) {
    console.error('뉴스 데이터 로딩 오류:', error);
    
    // 오류 시 빈 배열 반환
    return NextResponse.json({
      success: true,
      data: []
    });
  }
}

