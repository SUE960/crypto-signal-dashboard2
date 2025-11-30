'use client';

interface CompositeScoreHeaderProps {
  score: number;
  change: number;
  changePercent: number;
}

export default function CompositeScoreHeader({ score, change, changePercent }: CompositeScoreHeaderProps) {
  const isPositive = change >= 0;
  
  return (
    <div className="px-8 py-8 bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-baseline gap-6">
          <div>
            <div className="text-xs text-gray-400 font-semibold mb-3 uppercase tracking-wider">
              크립토 시그널 지수
            </div>
            <div className="flex items-baseline gap-4">
              <span className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                {score.toLocaleString('ko-KR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
              </span>
              <span className="text-xl text-gray-400 font-medium">SCORE</span>
              <div className={`flex items-center gap-2 text-sm font-bold px-3 py-1.5 rounded-lg ${
                isPositive 
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                <span className="text-lg">{isPositive ? '↑' : '↓'}</span>
                <span>{Math.abs(change).toFixed(1)} ({Math.abs(changePercent).toFixed(2)}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

