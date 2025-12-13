'use client';

import { useState, useEffect } from 'react';
import CompositeScoreHeader from '@/components/CompositeScoreHeader';
import UpbitStyleTabs from '@/components/UpbitStyleTabs';
import CorrelationIndicators from '@/components/CorrelationIndicators';
import NewsList from '@/components/NewsList';

interface Correlation {
  name: string;
  value: number;
}

export default function Home() {
  const [compositeScore, setCompositeScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('코인가격');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      if (result.success && result.data.compositeScore) {
        setCompositeScore(result.data.compositeScore);
      }
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 상관관계 데이터 (예시)
  const priceCorrelations: Correlation[] = [
    { name: '고래 거래 빈도 (ETH)', value: 0.133 },
    { name: '고래 거래 빈도 (BTC)', value: 0.090 },
    { name: '고래 거래 빈도 (ETH 변동성)', value: 0.075 },
    { name: '텔레그램 메시지 수 (ETH)', value: 0.071 },
    { name: '텔레그램 메시지 수 (BTC)', value: 0.068 },
    { name: '트위터 인게이지먼트 (ETH)', value: 0.062 },
    { name: '고래 거래 빈도 (BTC 변동성)', value: 0.042 },
    { name: '트위터 인게이지먼트 (BTC)', value: 0.025 },
    { name: '텔레그램 감정 (BTC 변화율)', value: -0.008 },
    { name: '고래 거래량 (BTC 변화율)', value: 0.008 },
  ];

  const whaleCorrelations: Correlation[] = [
    { name: '텔레그램 메시지 수', value: 0.15 },
    { name: '트위터 인게이지먼트', value: 0.12 },
    { name: 'ETH 가격', value: 0.10 },
    { name: 'BTC 가격', value: 0.08 },
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* 헤더 */}
      <header className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">Crypto Signal Dashboard</h1>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span className="text-sm text-gray-400">Live</span>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* 종합 점수 헤더 */}
        <CompositeScoreHeader score={compositeScore} loading={loading} />

        {/* 탭 네비게이션 */}
        <UpbitStyleTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* 탭 컨텐츠 */}
        <div className="mt-6">
          {activeTab === '코인가격' && (
            <CorrelationIndicators 
              correlations={priceCorrelations} 
              title="코인 가격" 
            />
          )}
          
          {activeTab === '고래지갑' && (
            <CorrelationIndicators 
              correlations={whaleCorrelations} 
              title="고래지갑" 
            />
          )}
          
          {activeTab === '뉴스' && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl">
              <div className="px-5 py-4 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-850">
                <h3 className="text-sm font-bold text-gray-100">최근 뉴스</h3>
              </div>
              <NewsList />
            </div>
          )}
          
          {activeTab === 'spike알람' && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl p-6">
              <p className="text-gray-400 text-center">스파이크 알람 데이터 로딩 중...</p>
            </div>
          )}
          
          {activeTab === '지금뉴스' && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl">
              <div className="px-5 py-4 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-850">
                <h3 className="text-sm font-bold text-gray-100">실시간 뉴스</h3>
              </div>
              <NewsList />
            </div>
          )}
        </div>
      </main>

      {/* 푸터 */}
      <footer className="mt-12 py-6 border-t border-gray-800 text-center text-gray-500 text-sm">
        <p>© 2024 Crypto Signal Dashboard. All rights reserved.</p>
        <p className="mt-2">Powered by Next.js & Vercel</p>
      </footer>
    </div>
  );
}
