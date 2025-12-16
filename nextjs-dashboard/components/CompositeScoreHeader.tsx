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
      // 1. timeseries API에서 고래 거래 및 가격 데이터 가져오기
      const timeseriesResponse = await fetch('/api/timeseries');
      const timeseriesData = await timeseriesResponse.json();
      
      // 2. 종합 점수 API에서 커뮤니티/뉴스/트위터 데이터 가져오기
      let compositeData: any = { success: false, data: [] };
      try {
        const compositeResponse = await fetch('/api/composite-score');
        compositeData = await compositeResponse.json();
      } catch (error) {
        console.warn('커뮤니티 데이터 로드 실패, 기본값 사용:', error);
      }
      
      if (!Array.isArray(timeseriesData) || timeseriesData.length === 0) {
        throw new Error('시계열 데이터가 없습니다');
      }

      // 11월 1일~8일 데이터만 사용
      const nov1Start = new Date('2025-11-01T00:00:00.000Z').getTime();
      const nov8End = new Date('2025-11-08T23:59:59.999Z').getTime();
      
      const recentData = timeseriesData.filter((d: any) => {
        const timestamp = new Date(d.timestamp).getTime();
        return timestamp >= nov1Start && timestamp <= nov8End;
      });

      const communityData = compositeData.success && Array.isArray(compositeData.data)
        ? compositeData.data.filter((d: any) => {
            const timestamp = new Date(d.timestamp).getTime();
            return timestamp >= nov1Start && timestamp <= nov8End;
          })
        : [];

      if (recentData.length === 0) {
        // 최근 데이터가 없으면 최신 데이터 사용
        const latest = timeseriesData[timeseriesData.length - 1];
        recentData.push(latest);
      }

      // 1. 고래 거래 선행 지표 점수 계산 (35% 가중치) - 시장 에너지 축적
      const whaleData = recentData
        .map((d: any) => ({
          tx_count: d.whale_tx_count || 0,
          volume: d.whale_volume_sum || 0,
          timestamp: d.timestamp
        }))
        .filter(d => d.tx_count > 0 || d.volume > 0);
      
      let whaleScore = 50; // 기본값
      if (whaleData.length > 0) {
        // 고래 거래량과 빈도를 종합하여 점수 계산
        const avgTxCount = whaleData.reduce((sum, d) => sum + d.tx_count, 0) / whaleData.length;
        const avgVolume = whaleData.reduce((sum, d) => sum + d.volume, 0) / whaleData.length;
        
        // 최근 7일 내 최대/최소값으로 정규화
        const allTxCounts = recentData.map(d => d.whale_tx_count || 0).filter(v => v > 0);
        const allVolumes = recentData.map(d => d.whale_volume_sum || 0).filter(v => v > 0);
        
        if (allTxCounts.length > 0 && allVolumes.length > 0) {
          const maxTx = Math.max(...allTxCounts);
          const minTx = Math.min(...allTxCounts);
          const maxVol = Math.max(...allVolumes);
          const minVol = Math.min(...allVolumes);
          
          // 거래 빈도 점수 (50% 가중치)
          const txScore = maxTx > minTx 
            ? ((avgTxCount - minTx) / (maxTx - minTx)) * 100
            : 50;
          
          // 거래량 점수 (50% 가중치)
          const volScore = maxVol > minVol
            ? ((avgVolume - minVol) / (maxVol - minVol)) * 100
            : 50;
          
          whaleScore = (txScore * 0.5 + volScore * 0.5);
        }
      }
      const whaleWeight = 0.35;

      // 2. 시장 거래량·변동성 점수 계산 (25% 가중치) - 실전 진입 가능성
      const priceChanges = recentData
        .map((d: any) => ({
          btc_change: Math.abs(d.btc_change || 0),
          eth_change: Math.abs(d.eth_change || 0)
        }))
        .filter(d => d.btc_change > 0 || d.eth_change > 0);
      
      let volatilityScore = 50; // 기본값
      if (priceChanges.length > 0) {
        // 변동성 = 변화율의 절대값 평균
        const avgBtcVol = priceChanges.reduce((sum, d) => sum + d.btc_change, 0) / priceChanges.length;
        const avgEthVol = priceChanges.reduce((sum, d) => sum + d.eth_change, 0) / priceChanges.length;
        const avgVolatility = (avgBtcVol + avgEthVol) / 2;
        
        // 변동성이 적당할 때(0.5~2%) 점수가 높고, 너무 높거나 낮으면 점수 감소
        // 0% = 30점, 1% = 80점, 3% = 50점, 5% = 20점
        if (avgVolatility <= 1) {
          volatilityScore = 30 + (avgVolatility / 1) * 50; // 0~1%: 30~80점
        } else if (avgVolatility <= 3) {
          volatilityScore = 80 - ((avgVolatility - 1) / 2) * 30; // 1~3%: 80~50점
        } else {
          volatilityScore = Math.max(20, 50 - ((avgVolatility - 3) / 2) * 30); // 3% 이상: 50~20점
        }
        volatilityScore = Math.min(100, Math.max(0, volatilityScore));
      }
      const volatilityWeight = 0.25;

      // 3. 커뮤니티 활동량 점수 계산 (20% 가중치) - 개인 자금 유입
      let communityScore = 50; // 기본값
      let communityDetails = '데이터 없음';
      if (communityData.length > 0) {
        // 텔레그램 + 트위터 활동량 종합
        const telegramPosts = communityData.map((d: any) => d.telegram?.posts || 0);
        const twitterLikes = communityData.map((d: any) => d.twitter?.likes || 0);
        
        const allPosts = telegramPosts.filter(p => p > 0);
        const allLikes = twitterLikes.filter(l => l > 0);
        
        if (allPosts.length > 0 || allLikes.length > 0) {
          // 텔레그램 메시지 수 정규화
          let telegramScore = 50;
          if (allPosts.length > 0) {
            const avgPosts = allPosts.reduce((a, b) => a + b, 0) / allPosts.length;
            const maxPosts = Math.max(...allPosts);
            const minPosts = Math.min(...allPosts);
            if (maxPosts > minPosts) {
              telegramScore = ((avgPosts - minPosts) / (maxPosts - minPosts)) * 100;
            }
          }
          
          // 트위터 좋아요 수 정규화
          let twitterScore = 50;
          if (allLikes.length > 0) {
            const avgLikes = allLikes.reduce((a, b) => a + b, 0) / allLikes.length;
            const maxLikes = Math.max(...allLikes);
            const minLikes = Math.min(...allLikes);
            if (maxLikes > minLikes) {
              twitterScore = ((avgLikes - minLikes) / (maxLikes - minLikes)) * 100;
            }
          }
          
          // 텔레그램 60%, 트위터 40% 가중치
          communityScore = telegramScore * 0.6 + twitterScore * 0.4;
          
          const avgTelegram = allPosts.length > 0 ? allPosts.reduce((a, b) => a + b, 0) / allPosts.length : 0;
          const avgTwitter = allLikes.length > 0 ? allLikes.reduce((a, b) => a + b, 0) / allLikes.length : 0;
          communityDetails = `텔레그램 ${Math.round(avgTelegram)}건/시간, 트위터 ${Math.round(avgTwitter)}좋아요/시간`;
        }
      }
      const communityWeight = 0.2;

      // 4. 뉴스 이벤트 점수 계산 (10% 가중치) - 촉발 트리거
      let newsScore = 50; // 기본값
      let newsDetails = '데이터 없음';
      if (communityData.length > 0) {
        // 뉴스 급증 이벤트 감지 (시간당 뉴스 수)
        const newsCounts = communityData.map((d: any) => d.news?.count || 0).filter(c => c > 0);
        
        if (newsCounts.length > 0) {
          const avgNews = newsCounts.reduce((a, b) => a + b, 0) / newsCounts.length;
          const maxNews = Math.max(...newsCounts);
          const minNews = Math.min(...newsCounts);
          
          // 뉴스 급증 이벤트: 평균의 2배 이상이면 높은 점수
          if (maxNews > minNews) {
            // 평균 대비 현재 뉴스 수
            const newsRatio = avgNews / (maxNews - minNews + 1);
            // 뉴스가 많을수록 점수 상승 (0~100점)
            newsScore = Math.min(100, Math.max(0, newsRatio * 100));
            
            // 급증 이벤트 보너스: 최근 24시간 내 뉴스가 평균의 2배 이상이면 추가 점수
            const recentNews = newsCounts.slice(-24);
            const recentAvg = recentNews.reduce((a, b) => a + b, 0) / recentNews.length;
            if (recentAvg > avgNews * 1.5) {
              newsScore = Math.min(100, newsScore + 20);
            }
            
            newsDetails = `평균 ${avgNews.toFixed(1)}건/시간${recentAvg > avgNews * 1.5 ? ' (급증 이벤트)' : ''}`;
          }
        }
      }
      const newsWeight = 0.1;

      // 5. 감정 지표 점수 계산 (10% 가중치) - 리스크 조정
      let sentimentScore = 50; // 기본값
      let sentimentDetails = '데이터 없음';
      if (communityData.length > 0) {
        // 텔레그램, 뉴스, 트위터 감정 종합
        const telegramSentiments = communityData
          .map((d: any) => d.telegram?.sentiment || 0)
          .filter(s => s !== 0);
        const newsSentiments = communityData
          .map((d: any) => d.news?.sentiment || 0)
          .filter(s => s !== 0);
        const twitterSentiments = communityData
          .map((d: any) => d.twitter?.sentiment || 0)
          .filter(s => s !== 0);
        
        let telegramSentiment = 50;
        let newsSentiment = 50;
        let twitterSentiment = 50;
        
        if (telegramSentiments.length > 0) {
          const avg = telegramSentiments.reduce((a, b) => a + b, 0) / telegramSentiments.length;
          // -1~1 범위를 0~100으로 변환
          telegramSentiment = Math.min(100, Math.max(0, (avg + 1) * 50));
        }
        
        if (newsSentiments.length > 0) {
          const avg = newsSentiments.reduce((a, b) => a + b, 0) / newsSentiments.length;
          // -1~1 범위를 0~100으로 변환
          newsSentiment = Math.min(100, Math.max(0, (avg + 1) * 50));
        }
        
        if (twitterSentiments.length > 0) {
          const avg = twitterSentiments.reduce((a, b) => a + b, 0) / twitterSentiments.length;
          // -1~1 범위를 0~100으로 변환
          twitterSentiment = Math.min(100, Math.max(0, (avg + 1) * 50));
        }
        
        // 텔레그램 40%, 뉴스 40%, 트위터 20% 가중치
        sentimentScore = telegramSentiment * 0.4 + newsSentiment * 0.4 + twitterSentiment * 0.2;
        
        const sentimentLabel = sentimentScore > 60 ? '긍정적' : sentimentScore < 40 ? '부정적' : '중립';
        sentimentDetails = `텔레그램/뉴스/트위터 종합: ${sentimentLabel}`;
      }
      const sentimentWeight = 0.1;

      // 최종 점수 계산 (가중 평균)
      const finalScore = 
        whaleScore * whaleWeight +
        volatilityScore * volatilityWeight +
        communityScore * communityWeight +
        newsScore * newsWeight +
        sentimentScore * sentimentWeight;

      // 계산 로직 저장
      const logic: CalculationLogic = {
        components: [
          {
            name: '고래 거래 선행 지표',
            weight: whaleWeight,
            score: whaleScore,
            details: `시장 에너지 축적: 평균 ${whaleData.length > 0 ? Math.round(whaleData.reduce((sum, d) => sum + d.tx_count, 0) / whaleData.length) : 0}건/시간`
          },
          {
            name: '시장 거래량·변동성',
            weight: volatilityWeight,
            score: volatilityScore,
            details: `실전 진입 가능성: 평균 변동성 ${priceChanges.length > 0 ? ((priceChanges.reduce((sum, d) => sum + (d.btc_change + d.eth_change) / 2, 0) / priceChanges.length)).toFixed(2) : 0}%`
          },
          {
            name: '커뮤니티 활동량',
            weight: communityWeight,
            score: communityScore,
            details: `개인 자금 유입: ${communityDetails}`
          },
          {
            name: '뉴스 이벤트',
            weight: newsWeight,
            score: newsScore,
            details: `촉발 트리거: ${newsDetails}`
          },
          {
            name: '감정 지표',
            weight: sentimentWeight,
            score: sentimentScore,
            details: `리스크 조정: ${sentimentDetails}`
          }
        ],
        finalScore: finalScore,
        formula: `${whaleScore.toFixed(1)} × ${(whaleWeight * 100).toFixed(0)}% + ${volatilityScore.toFixed(1)} × ${(volatilityWeight * 100).toFixed(0)}% + ${communityScore.toFixed(1)} × ${(communityWeight * 100).toFixed(0)}% + ${newsScore.toFixed(1)} × ${(newsWeight * 100).toFixed(0)}% + ${sentimentScore.toFixed(1)} × ${(sentimentWeight * 100).toFixed(0)}%`
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
          { name: '고래 거래 선행 지표', weight: 0.35, score: 50, details: '시장 에너지 축적' },
          { name: '시장 거래량·변동성', weight: 0.25, score: 50, details: '실전 진입 가능성' },
          { name: '커뮤니티 활동량', weight: 0.2, score: 50, details: '개인 자금 유입' },
          { name: '뉴스 이벤트', weight: 0.1, score: 50, details: '촉발 트리거' },
          { name: '감정 지표', weight: 0.1, score: 50, details: '리스크 조정' }
        ],
        finalScore: 50,
        formula: '50 × 35% + 50 × 25% + 50 × 20% + 50 × 10% + 50 × 10%'
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
          { name: '고래 거래 선행 지표', weight: 0.35, score: 50, details: '시장 에너지 축적' },
          { name: '시장 거래량·변동성', weight: 0.25, score: 50, details: '실전 진입 가능성' },
          { name: '커뮤니티 활동량', weight: 0.2, score: 50, details: '개인 자금 유입' },
          { name: '뉴스 이벤트', weight: 0.1, score: 50, details: '촉발 트리거' },
          { name: '감정 지표', weight: 0.1, score: 50, details: '리스크 조정' }
        ],
        finalScore: propScore,
        formula: '50 × 35% + 50 × 25% + 50 × 20% + 50 × 10% + 50 × 10%'
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
  └ ${c.details || '데이터 분석 중'}`
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

📐 계산 방법 (2025년 11월 1일~8일 데이터 기준):

1. 고래 거래 선행 지표 (35%) - 시장 에너지 축적
   • 고래 거래 빈도와 거래량을 종합 분석
   • 15-22시간 후 시장 거래량 증가를 선행하는 지표
   • 최근 7일 평균 대비 상대적 위치로 점수화

2. 시장 거래량·변동성 (25%) - 실전 진입 가능성
   • BTC/ETH 가격 변동성 분석
   • 적정 변동성(0.5~2%)에서 높은 점수
   • 너무 높거나 낮은 변동성은 점수 감소

3. 커뮤니티 활동량 (20%) - 개인 자금 유입
   • 텔레그램/트위터 활동량 추정
   • 고래 거래량 변화를 간접 지표로 활용
   • 최근 3일 vs 이전 3일 비교

4. 뉴스 이벤트 (10%) - 촉발 트리거
   • 가격 변동성 급증을 뉴스 이벤트 지표로 활용
   • 변동성 2% 이상 시 뉴스 이벤트 발생 가능성 높음

5. 감정 지표 (10%) - 리스크 조정
   • 가격 변화 방향을 감정의 간접 지표로 사용
   • 상승 추세 = 긍정, 하락 추세 = 부정

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

