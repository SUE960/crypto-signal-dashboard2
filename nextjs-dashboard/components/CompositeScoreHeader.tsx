'use client';

import { useState, useEffect } from 'react';
import Tooltip from './Tooltip';

interface CompositeScoreHeaderProps {
  score?: number;
}

interface CalculationLogic {
  components: Array<{
    name: string;
    weight: number;
    score: number;
    details?: string;
  }>;
  finalScore: number;
  formula: string;
}

export default function CompositeScoreHeader({ 
  score: propScore
}: CompositeScoreHeaderProps) {
  const [score, setScore] = useState<number>(propScore || 0);
  const [calculationLogic, setCalculationLogic] = useState<CalculationLogic | null>(null);
  const [loading, setLoading] = useState(true);

  // 시그널 점수 계산 함수
  const calculateSignalScore = async () => {
    try {
      // timeseries API에서 데이터 가져오기
      const response = await fetch('/api/timeseries');
      const data = await response.json();
      
      if (!Array.isArray(data) || data.length === 0) {
        throw new Error('데이터가 없습니다');
      }

      // 11월 1일~8일 데이터 필터링
      const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
      const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
      
      const recentData = data.filter((d: any) => {
        const timestamp = new Date(d.timestamp).getTime();
        return timestamp >= nov1Start && timestamp <= nov8End;
      });

      if (recentData.length === 0) {
        // 11월 데이터가 없으면 전체 데이터 사용
        const latest = data[data.length - 1];
        recentData.push(latest);
      }

      // 1. 고래 거래 점수 계산 (30% 가중치)
      // 11/1-8일 데이터를 일별로 집계
      const dailyWhaleMap = new Map<string, number>();
      recentData.forEach((d: any) => {
        const date = new Date(d.timestamp);
        const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        const current = dailyWhaleMap.get(dateKey) || 0;
        dailyWhaleMap.set(dateKey, current + (d.whale_tx_count || 0));
      });
      
      const dailyWhaleCounts = Array.from(dailyWhaleMap.values()).filter(count => count > 0);
      
      let whaleScore = 50; // 기본값
      if (dailyWhaleCounts.length > 0) {
        const avgWhale = dailyWhaleCounts.reduce((a: number, b: number) => a + b, 0) / dailyWhaleCounts.length;
        const maxWhale = Math.max(...dailyWhaleCounts);
        const minWhale = Math.min(...dailyWhaleCounts);
        
        // 정규화: 평균 대비 현재 거래량
        if (maxWhale > minWhale) {
          whaleScore = Math.min(100, Math.max(0, ((avgWhale - minWhale) / (maxWhale - minWhale)) * 100));
        } else if (avgWhale > 0) {
          // 모든 값이 같으면 평균값 기준으로 점수 계산
          whaleScore = Math.min(100, Math.max(50, (avgWhale / 1000) * 10)); // 1000건당 10점
        }
      }
      const whaleWeight = 0.3;

      // 2. 가격 변화 점수 계산 (25% 가중치)
      const latestPrice = recentData[recentData.length - 1]?.btc_close || 0;
      const previousPrice = recentData.length > 1 
        ? recentData[recentData.length - 2]?.btc_close || latestPrice
        : latestPrice;
      
      let priceScore = 50; // 기본값
      if (latestPrice > 0 && previousPrice > 0) {
        const priceChange = ((latestPrice - previousPrice) / previousPrice) * 100;
        // 가격 변화율을 0-100 점수로 변환 (-5% = 0점, 0% = 50점, +5% = 100점)
        priceScore = Math.min(100, Math.max(0, 50 + (priceChange * 10)));
      }
      const priceWeight = 0.25;

      // 3. 가격 변화율 점수 계산 (20% 가중치)
      const priceChanges = recentData
        .map((d: any) => d.btc_change || 0)
        .filter((change: number) => change !== 0);
      
      let changeScore = 50; // 기본값
      if (priceChanges.length > 0) {
        const avgChange = priceChanges.reduce((a: number, b: number) => a + b, 0) / priceChanges.length;
        // 변화율을 0-100 점수로 변환
        changeScore = Math.min(100, Math.max(0, 50 + (avgChange * 2)));
      }
      const changeWeight = 0.2;

      // 4. 거래량 추세 점수 계산 (25% 가중치)
      // 11/1-8일 고래 거래량의 추세를 분석
      const sortedDailyCounts = Array.from(dailyWhaleMap.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([_, count]) => count);
      
      const whaleTrend = sortedDailyCounts.length > 1 && sortedDailyCounts[0] > 0
        ? (sortedDailyCounts[sortedDailyCounts.length - 1] - sortedDailyCounts[0]) / sortedDailyCounts[0]
        : 0;
      
      let trendScore = 50; // 기본값
      if (whaleTrend !== 0) {
        // 추세를 0-100 점수로 변환 (11/1 대비 11/8의 변화율)
        trendScore = Math.min(100, Math.max(0, 50 + (whaleTrend * 50)));
      }
      const trendWeight = 0.25;

      // 최종 점수 계산 (가중 평균)
      const finalScore = 
        whaleScore * whaleWeight +
        priceScore * priceWeight +
        changeScore * changeWeight +
        trendScore * trendWeight;

      // 계산 로직 저장
      const logic: CalculationLogic = {
        components: [
          {
            name: '고래 거래 활동',
            weight: whaleWeight,
            score: whaleScore,
            details: `11/1-8일 평균: ${dailyWhaleCounts.length > 0 ? Math.round(dailyWhaleCounts.reduce((a: number, b: number) => a + b, 0) / dailyWhaleCounts.length) : 0}건/일`
          },
          {
            name: 'BTC 가격 수준',
            weight: priceWeight,
            score: priceScore,
            details: `현재 가격: $${latestPrice.toLocaleString('ko-KR', { maximumFractionDigits: 0 })}`
          },
          {
            name: '가격 변화율',
            weight: changeWeight,
            score: changeScore,
            details: `평균 변화율: ${priceChanges.length > 0 ? (priceChanges.reduce((a: number, b: number) => a + b, 0) / priceChanges.length).toFixed(2) : 0}%`
          },
          {
            name: '거래량 추세',
            weight: trendWeight,
            score: trendScore,
            details: `11/1-8일 추세: ${(whaleTrend * 100).toFixed(1)}%`
          }
        ],
        finalScore: finalScore,
        formula: `${whaleScore.toFixed(1)} × ${(whaleWeight * 100).toFixed(0)}% + ${priceScore.toFixed(1)} × ${(priceWeight * 100).toFixed(0)}% + ${changeScore.toFixed(1)} × ${(changeWeight * 100).toFixed(0)}% + ${trendScore.toFixed(1)} × ${(trendWeight * 100).toFixed(0)}%`
      };

      setScore(finalScore);
      setCalculationLogic(logic);
      setLoading(false);
    } catch (error) {
      console.error('시그널 점수 계산 실패:', error);
      // 기본값 설정
      setScore(50);
      setCalculationLogic({
        components: [
          { name: '고래 거래 활동', weight: 0.3, score: 50 },
          { name: 'BTC 가격 수준', weight: 0.25, score: 50 },
          { name: '가격 변화율', weight: 0.2, score: 50 },
          { name: '거래량 추세', weight: 0.25, score: 50 }
        ],
        finalScore: 50,
        formula: '50 × 30% + 50 × 25% + 50 × 20% + 50 × 25%'
      });
      setLoading(false);
    }
  };

  useEffect(() => {
    if (propScore !== undefined) {
      // propScore가 제공되면 사용
      setScore(propScore);
      setCalculationLogic({
        components: [
          { name: '고래 거래 활동', weight: 0.3, score: 50 },
          { name: 'BTC 가격 수준', weight: 0.25, score: 50 },
          { name: '가격 변화율', weight: 0.2, score: 50 },
          { name: '거래량 추세', weight: 0.25, score: 50 }
        ],
        finalScore: propScore,
        formula: '50 × 30% + 50 × 25% + 50 × 20% + 50 × 25%'
      });
      setLoading(false);
    } else {
      // API에서 계산
      calculateSignalScore();
    }
  }, [propScore]);

  const tooltipContent = calculationLogic ? `
📊 크립토 시그널 지수 계산 로직

🎯 종합 점수 구성:
${calculationLogic.components.map((c) => 
  `• ${c.name}: ${c.score.toFixed(1)}점 (가중치 ${(c.weight * 100).toFixed(0)}%)
  ${c.details ? `  └ ${c.details}` : ''}`
).join('\n')}

📈 최종 점수 계산:
= ${calculationLogic.formula}
= ${calculationLogic.finalScore.toFixed(1)}점

💡 점수 의미:
• 75점 이상: 강한 매수 신호 🚀
• 60-75점: 매수 고려 📈
• 40-60점: 중립 ⚖️
• 25-40점: 매도 고려 📉
• 25점 미만: 강한 매도 신호 ⚠️

📐 계산 방법 (11월 1일~8일 데이터 기준):
1. 고래 거래 활동 (30%): 11/1-8일 고래 거래량을 정규화하여 계산
2. BTC 가격 수준 (25%): 11/1-8일 기간의 가격 변화율 기반
3. 가격 변화율 (20%): 11/1-8일 평균 가격 변화율 분석
4. 거래량 추세 (25%): 11/1-8일 고래 거래량의 추세 분석

📅 데이터 기간: 2025년 11월 1일 00:00 ~ 11월 8일 23:59
  `.trim() : '데이터 로딩 중...';

  if (loading) {
    return (
      <div className="px-8 py-8 bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto">
          <div className="text-center text-gray-400">점수 계산 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-8 py-8 bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-baseline gap-6">
          <div>
            <div className="text-xs text-gray-400 font-semibold mb-3 uppercase tracking-wider">
              크립토 시그널 지수
            </div>
            <div className="flex items-baseline gap-4">
              <Tooltip content={tooltipContent}>
                <span className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent cursor-help border-b border-dashed border-transparent hover:border-blue-400 transition-colors">
                  {score.toLocaleString('ko-KR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                </span>
              </Tooltip>
              <span className="text-xl text-gray-400 font-medium">SCORE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

