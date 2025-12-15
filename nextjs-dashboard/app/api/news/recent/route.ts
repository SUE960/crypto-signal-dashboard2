import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    // URL 파라미터에서 limit 추출
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50', 10);

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
    
    // 파일이 없으면 빈 배열 반환 (디버깅 정보 포함)
    if (!dataPath) {
      const debugInfo = {
        error: '코인니스 데이터 파일을 찾을 수 없습니다',
        triedPaths: possiblePaths.map(p => ({
          path: p,
          exists: fs.existsSync(p),
          cwd: process.cwd()
        })),
        env: process.env.NODE_ENV
      };
      console.error('뉴스 데이터 파일 찾기 실패:', JSON.stringify(debugInfo, null, 2));
      
      // 디버깅 정보를 응답에 포함 (개발 환경에서만)
      return NextResponse.json({
        error: '데이터 파일을 찾을 수 없습니다',
        debug: process.env.NODE_ENV === 'development' ? debugInfo : undefined,
        data: []
      });
    }

    console.log('뉴스 데이터 파일 경로:', dataPath);
    console.log('현재 작업 디렉토리:', process.cwd());
    console.log('환경:', process.env.NODE_ENV);

    // CSV 파일 읽기
    let fileContent;
    try {
      fileContent = fs.readFileSync(dataPath, 'utf-8');
      console.log('파일 읽기 성공, 크기:', fileContent.length, 'bytes');
    } catch (readError) {
      console.error('파일 읽기 실패:', readError);
      return NextResponse.json({
        error: '파일 읽기 실패',
        message: readError instanceof Error ? readError.message : 'Unknown error',
        data: []
      });
    }
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      encoding: 'utf-8'
    });

    console.log(`총 ${records.length}개의 뉴스 레코드를 읽었습니다.`);

    // 최신 뉴스부터 정렬 (timestamp 기준 내림차순)
    const sortedNews = records
      .filter((record: any) => record.timestamp && record.title && record.link)
      .sort((a: any, b: any) => {
        const dateA = new Date(a.timestamp).getTime();
        const dateB = new Date(b.timestamp).getTime();
        return dateB - dateA; // 최신순
      })
      .slice(0, limit) // limit 개수만큼
      .map((record: any) => {
        const title = record.title || '';
        const content = record.content || '';
        
        // 비트코인/이더리움 키워드 감지
        const hasBitcoin = /비트코인|BTC|bitcoin/i.test(title + content);
        const hasEthereum = /이더리움|ETH|ethereum/i.test(title + content);
        
        // 감정 분석 결과
        const sentiment_compound = parseFloat(record.sentiment_compound) || 0;
        const sentiment_positive = parseFloat(record.sentiment_positive) || 0;
        const sentiment_negative = parseFloat(record.sentiment_negative) || 0;
        const sentiment_neutral = parseFloat(record.sentiment_neutral) || 0;
        
        // 강세/약세 판단
        const hasBullish = sentiment_compound > 0.05;
        const hasBearish = sentiment_compound < -0.05;
        
        return {
          timestamp: record.timestamp,
          title,
          content: content.substring(0, 200) + (content.length > 200 ? '...' : ''),
          link: record.link,
          sentiment_compound,
          sentiment_positive,
          sentiment_negative,
          sentiment_neutral,
          has_bitcoin: hasBitcoin,
          has_ethereum: hasEthereum,
          has_bullish: hasBullish,
          has_bearish: hasBearish,
        };
      });

    return NextResponse.json(sortedNews);
  } catch (error) {
    console.error('뉴스 데이터 로딩 오류:', error);
    
    // 오류 시 빈 배열 반환
    return NextResponse.json([]);
  }
}

