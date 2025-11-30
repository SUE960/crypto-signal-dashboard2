// app/api/spike-points/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = searchParams.get('range') || '30d';

    // CSV 파일 경로 찾기
    const possiblePaths = [
      path.join(process.cwd(), '../../data/final_integrated_data.csv'),
      path.join(process.cwd(), '../data/final_integrated_data.csv'),
      path.join(process.cwd(), 'data/final_integrated_data.csv'),
    ];
    
    let dataPath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        dataPath = p;
        break;
      }
    }
    
    if (!dataPath) {
      return NextResponse.json([]);
    }

    // CSV 파일 읽기
    const fileContent = fs.readFileSync(dataPath, 'utf-8');
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });

    // 시간 범위 필터링
    const now = new Date();
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

    const filteredData = records
      .filter((record: any) => {
        if (!record.timestamp) return false;
        const recordDate = new Date(record.timestamp);
        return recordDate >= cutoffDate;
      })
      .map((record: any) => ({
        timestamp: record.timestamp,
        whale_tx_count: parseFloat(record.whale_tx_count) || 0,
        telegram_message_count: parseFloat(record.telegram_message_count) || 0,
        twitter_engagement: parseFloat(record.twitter_engagement) || 0,
        news_count: parseFloat(record.news_count) || 0,
        btc_close: parseFloat(record.btc_close) || 0,
        eth_close: parseFloat(record.eth_close) || 0,
        btc_change: parseFloat(record.btc_price_change) || 0,
        eth_change: parseFloat(record.eth_price_change) || 0,
        telegram_sentiment: parseFloat(record.telegram_avg_sentiment) || 0,
        twitter_sentiment: parseFloat(record.twitter_sentiment) || 0,
        news_sentiment: parseFloat(record.news_sentiment_avg) || 0,
      }))
      .filter((item: any) => item.btc_close > 0 || item.eth_close > 0);

    if (filteredData.length < 24) {
      return NextResponse.json([]);
    }

    // Z-score 계산 함수
    const calculateZScore = (values: number[], window: number = 24) => {
      const zscores: number[] = [];
      for (let i = 0; i < values.length; i++) {
        const windowStart = Math.max(0, i - window + 1);
        const windowValues = values.slice(windowStart, i + 1);
        const mean = windowValues.reduce((a, b) => a + b, 0) / windowValues.length;
        const std = Math.sqrt(
          windowValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / windowValues.length
        );
        zscores.push(std > 0 ? (values[i] - mean) / std : 0);
      }
      return zscores;
    };

    // 각 지표의 Z-score 계산
    const whaleZ = calculateZScore(filteredData.map((d: any) => d.whale_tx_count));
    const telegramZ = calculateZScore(filteredData.map((d: any) => d.telegram_message_count));
    const twitterZ = calculateZScore(filteredData.map((d: any) => d.twitter_engagement));
    const newsZ = calculateZScore(filteredData.map((d: any) => d.news_count));

    // Spike 감지 (구매 시점)
    const spikePoints: any[] = [];
    const threshold = 2.0; // Z-score 임계값

    for (let i = 0; i < filteredData.length; i++) {
      const data = filteredData[i];
      let priorityScore = 0;
      const reasons: string[] = [];
      const details: any = {};

      // 1. 고래 거래 스파이크
      if (whaleZ[i] > threshold) {
        priorityScore += 3;
        reasons.push(`고래 거래 급증 (z=${whaleZ[i].toFixed(2)})`);
        details.whale_zscore = whaleZ[i];
        details.whale_tx_count = data.whale_tx_count;
      }

      // 2. 텔레그램 스파이크
      if (telegramZ[i] > threshold) {
        priorityScore += 2;
        reasons.push(`텔레그램 활동 급증 (z=${telegramZ[i].toFixed(2)})`);
        details.telegram_zscore = telegramZ[i];
        details.telegram_message_count = data.telegram_message_count;
      }

      // 3. 트위터 스파이크
      if (twitterZ[i] > threshold) {
        priorityScore += 2;
        reasons.push(`트위터 인게이지먼트 급증 (z=${twitterZ[i].toFixed(2)})`);
        details.twitter_zscore = twitterZ[i];
        details.twitter_engagement = data.twitter_engagement;
      }

      // 4. 뉴스 스파이크
      if (newsZ[i] > threshold) {
        priorityScore += 2;
        reasons.push(`뉴스 급증 (z=${newsZ[i].toFixed(2)})`);
        details.news_zscore = newsZ[i];
        details.news_count = data.news_count;
      }

      // 5. 복합 스파이크 보너스
      const whaleSpike = whaleZ[i] > threshold;
      const telegramSpike = telegramZ[i] > threshold;
      const twitterSpike = twitterZ[i] > threshold;

      if (whaleSpike && telegramSpike) {
        priorityScore += 5;
        reasons.push('⚠️ 텔레그램+고래 동시 급증');
      }

      if (whaleSpike && twitterSpike) {
        priorityScore += 4;
        reasons.push('⚠️ 트위터+고래 동시 급증');
      }

      if (whaleSpike && telegramSpike && twitterSpike) {
        priorityScore += 10;
        reasons.push('🚨 3개 소스 모두 급증 (CRITICAL)');
      }

      // 6. 가격 급변 보너스
      if (Math.abs(data.btc_change) > 2 || Math.abs(data.eth_change) > 2) {
        priorityScore += 2;
        reasons.push(`가격 급변 (BTC ${data.btc_change.toFixed(2)}%, ETH ${data.eth_change.toFixed(2)}%)`);
        details.price_change = { btc: data.btc_change, eth: data.eth_change };
      }

      // 구매 시점 판단 (priority >= 5 이상)
      if (priorityScore >= 5) {
        const alertLevel = priorityScore >= 10 ? 'CRITICAL' : priorityScore >= 7 ? 'HIGH' : 'MEDIUM';
        
        spikePoints.push({
          timestamp: data.timestamp,
          date: new Date(data.timestamp).toLocaleDateString('ko-KR', {
            month: 'numeric',
            day: 'numeric',
            ...(range === '90d' ? {} : { hour: '2-digit' })
          }),
          priorityScore,
          alertLevel,
          reasons,
          details: {
            ...details,
            btc_price: data.btc_close,
            eth_price: data.eth_close,
            telegram_sentiment: data.telegram_sentiment,
            twitter_sentiment: data.twitter_sentiment,
            news_sentiment: data.news_sentiment,
          }
        });
      }
    }

    return NextResponse.json(spikePoints);
  } catch (error) {
    console.error('Error detecting spike points:', error);
    return NextResponse.json([]);
  }
}

