'use client';

import { useState, useEffect } from 'react';
import Tooltip from './Tooltip';

interface CompositeScoreHeaderProps {
  score?: number;
  change?: number;
  changePercent?: number;
  predictionAccuracy?: number;
}

export default function CompositeScoreHeader({ 
  score: propScore, 
  change: propChange, 
  changePercent: propChangePercent,
  predictionAccuracy: propAccuracy
}: CompositeScoreHeaderProps) {
  const [score, setScore] = useState(propScore || 75.3);
  const [change, setChange] = useState(propChange || 5.2);
  const [changePercent, setChangePercent] = useState(propChangePercent || 8.45);
  const [predictionAccuracy, setPredictionAccuracy] = useState(propAccuracy || 68.5);
  const [calculationLogic, setCalculationLogic] = useState<any>(null);
  const [loading, setLoading] = useState(!propScore);

  useEffect(() => {
    if (!propScore) {
      // API에서 데이터 가져오기
      fetch('/api/composite-score')
        .then(res => res.json())
        .then(data => {
          setScore(data.score);
          setChange(data.change);
          setChangePercent(data.changePercent);
          setPredictionAccuracy(data.predictionAccuracy);
          setCalculationLogic(data.calculationLogic);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load composite score:', err);
          setLoading(false);
        });
    } else {
      setCalculationLogic({
        components: [
          { name: '텔레그램 활동', weight: 0.2, score: 72.5 },
          { name: '고래 거래', weight: 0.3, score: 78.2 },
          { name: '트위터 인게이지먼트', weight: 0.2, score: 70.1 },
          { name: '뉴스 감정', weight: 0.3, score: 73.8 }
        ],
        predictionMethod: '고래 거래와 가격 상관관계 기반 예측',
        accuracyMethod: '실제 가격 변화와 예측 비교'
      });
    }
  }, [propScore]);

  const isPositive = change >= 0;
  
  const tooltipContent = calculationLogic ? `
📊 크립토 시그널 지수 계산 로직

🎯 종합 점수 구성:
${calculationLogic.components.map((c: any) => 
  `• ${c.name}: ${c.score.toFixed(1)}점 (가중치 ${(c.weight * 100).toFixed(0)}%)`
).join('\n')}

📈 최종 점수:
= ${calculationLogic.components.map((c: any) => 
  `${c.score.toFixed(1)} × ${(c.weight * 100).toFixed(0)}%`
).join(' + ')}
= ${score.toFixed(1)}점

💡 점수 의미:
• 75점 이상: 강한 매수 신호 🚀
• 60-75점: 매수 고려 📈
• 40-60점: 중립 ⚖️
• 25-40점: 매도 고려 📉
• 25점 미만: 강한 매도 신호 ⚠️

🔮 예측 정확도 (${predictionAccuracy.toFixed(1)}%):
${calculationLogic.accuracyMethod}
${calculationLogic.accuracyDetails ? `\n${calculationLogic.accuracyDetails}` : ''}

📐 예측 방법:
${calculationLogic.predictionMethod}
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
              <span className="text-lg text-gray-500 font-medium">
                ({predictionAccuracy.toFixed(1)}%)
              </span>
              <div className={`flex items-center gap-2 text-sm font-bold px-3 py-1.5 rounded-lg ${
                isPositive 
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                <span className="text-lg">{isPositive ? '↑' : '↓'}</span>
                <Tooltip content={`직전 일자 대비 ${Math.abs(change).toFixed(1)}점 ${isPositive ? '상승' : '하락'}\n변화율: ${Math.abs(changePercent).toFixed(2)}%`}>
                  <span className="cursor-help border-b border-dashed border-transparent hover:border-current">
                    {Math.abs(change).toFixed(1)} ({Math.abs(changePercent).toFixed(2)}%)
                  </span>
                </Tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

