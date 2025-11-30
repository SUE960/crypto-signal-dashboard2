'use client';

interface Correlation {
  name: string;
  value: number;
}

interface CorrelationIndicatorsProps {
  correlations: Correlation[];
  title: string;
}

export default function CorrelationIndicators({ correlations, title }: CorrelationIndicatorsProps) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl">
      <div className="px-5 py-4 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-850">
        <h3 className="text-sm font-bold text-gray-100">{title}과의 상관관계</h3>
      </div>
      
      <div className="max-h-[420px] overflow-y-auto">
        {correlations.map((corr, index) => {
          const absValue = Math.abs(corr.value);
          const strength = absValue > 0.7 ? 'strong' : absValue > 0.4 ? 'medium' : 'weak';
          
          return (
            <div 
              key={index}
              className="flex justify-between items-center px-5 py-4 border-b border-gray-700/50 hover:bg-gray-750 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  strength === 'strong' ? 'bg-green-400' :
                  strength === 'medium' ? 'bg-yellow-400' : 'bg-gray-400'
                }`} />
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                  {corr.name}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${corr.value > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.abs(corr.value) * 100}%` }}
                  />
                </div>
                <span className={`text-sm font-bold tabular-nums min-w-[70px] text-right ${
                  corr.value > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {corr.value > 0 ? '+' : ''}{(corr.value * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
        
        {correlations.length === 0 && (
          <div className="px-5 py-12 text-center text-gray-500 text-sm">
            데이터가 없습니다
          </div>
        )}
      </div>
    </div>
  );
}

