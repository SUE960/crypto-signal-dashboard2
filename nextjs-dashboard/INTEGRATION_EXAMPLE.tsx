// app/page.tsx에 추가할 내용 (예제)

import CorrelationPanel from '@/components/CorrelationPanel';
import { priceCorrelations } from '@/lib/correlationData';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            암호화폐 시장 분석 대시보드
          </h1>
          <p className="text-gray-400">
            실시간 상관관계 분석 및 시장 신호
          </p>
        </div>

        {/* 그리드 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 상관관계 패널 - 필수 props 전달 */}
          <CorrelationPanel 
            data={priceCorrelations} 
            title="코인 가격과의 상관관계" 
          />

          {/* 여기에 다른 컴포넌트들 추가 가능 */}
          {/* 예: 가격 차트, 뉴스 피드 등 */}
        </div>
      </div>
    </main>
  );
}

