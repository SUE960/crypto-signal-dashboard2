'use client';

interface CompositeScoreHeaderProps {
  score: number | null;
  loading: boolean;
}

export default function CompositeScoreHeader({ score, loading }: CompositeScoreHeaderProps) {
  if (loading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
        <div className="text-center">
          <p className="text-gray-400">점수 계산 중...</p>
        </div>
      </div>
    );
  }

  const displayScore = score ?? 50;
  const scoreColor = displayScore >= 75 ? 'text-green-400' : 
                     displayScore >= 60 ? 'text-blue-400' : 
                     displayScore >= 40 ? 'text-gray-400' : 
                     displayScore >= 25 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
      <div className="text-center">
        <div className="text-sm text-gray-400 mb-2">크립토 시그널 지수</div>
        <div className={`text-5xl font-bold ${scoreColor} mb-2`}>
          {displayScore.toFixed(1)}
        </div>
        <div className="text-xs text-gray-500">SCORE</div>
      </div>
    </div>
  );
}
