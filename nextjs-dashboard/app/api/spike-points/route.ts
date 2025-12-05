// app/api/spike-points/route.ts
import { NextResponse } from 'next/server';
import { getSpikeDetectionData } from '@/lib/supabase';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const range = (searchParams.get('range') || '30d') as '7d' | '30d' | '90d';

    // Supabase에서 스파이크 감지용 데이터 가져오기
    const filteredData = await getSpikeDetectionData(range);

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

