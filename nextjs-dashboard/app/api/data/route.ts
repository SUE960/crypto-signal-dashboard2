import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // 모의 데이터 반환 (실제 파일이 없을 경우를 대비)
    const mockData = {
      processed: Array.from({ length: 50 }, (_, i) => ({
        timestamp: new Date(Date.now() - (50 - i) * 3600000).toISOString(),
        composite_score: (Math.random() * 30 + 60).toFixed(1),
        message_count: Math.floor(Math.random() * 100),
        tx_frequency: Math.floor(Math.random() * 50),
        eth_price: (Math.random() * 1000 + 3000).toFixed(2),
      })),
    };
    
    // 최신 데이터로 종합 점수 계산
    const latestData = mockData.processed[mockData.processed.length - 1];
    const compositeScore = parseFloat(latestData.composite_score);
    
    return NextResponse.json({
      success: true,
      data: {
        processed: mockData.processed,
        compositeScore: compositeScore,
        lastUpdate: new Date().toISOString(),
      }
    });
  } catch (error) {
    console.error('데이터 로딩 오류:', error);
    
    // 오류 시에도 기본 데이터 반환
    return NextResponse.json({
      success: true,
      data: {
        processed: [],
        compositeScore: 75.3,
        lastUpdate: new Date().toISOString(),
      }
    });
  }
}

