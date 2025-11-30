'use client';

// import { useEffect, useState } from 'react';
import CompositeScoreHeader from '../components/CompositeScoreHeader';
import UpbitStyleTabs from '../components/UpbitStyleTabs';
import CorrelationPanel from '../components/CorrelationPanel';
import RealTimeChart from '../components/RealTimeChart';
import NewsListPanel from '../components/NewsListPanel';
import {
  priceCorrelations,
  whaleCorrelations,
  newsCorrelations
} from '../lib/correlationData';

export default function Home() {
  // const [data, setData] = useState<any>(null);
  // const [loading, setLoading] = useState(true);

  // useEffect(() => {
  //   fetchData();
  // }, []);

  // const fetchData = async () => {
  //   try {
  //     const response = await fetch('/api/data');
  //     const result = await response.json();
  //     if (result.success) {
  //       setData(result.data);
  //     }
  //   } catch (error) {
  //     console.error('데이터 로딩 실패:', error);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  // 로딩 제거 - 바로 표시
  // if (loading) {
  //   return (
  //     <div className="flex items-center justify-center min-h-screen bg-gray-900">
  //       <div className="text-center">
  //         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
  //         <div className="text-gray-400">데이터 로딩 중...</div>
  //       </div>
  //     </div>
  //   );
  // }

  const tabs = [
    {
      id: 'price',
      label: '코인가격\n관계',
      content: <CorrelationPanel data={priceCorrelations} title="코인 가격과의 상관관계" />
    },
    {
      id: 'whale',
      label: '고래지갑\n관계',
      content: <CorrelationPanel data={whaleCorrelations} title="고래 거래와의 상관관계" />
    },
    {
      id: 'news-correlation',
      label: '뉴스와의\n관계',
      content: <CorrelationPanel data={newsCorrelations} title="뉴스와의 상관관계" />
    },
    {
      id: 'news',
      label: '지금 뉴스',
      content: <NewsListPanel />
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* 상단 네비게이션 */}
      <div className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 border-b border-gray-700 px-8 py-5 shadow-2xl">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                Crypto Signal Dashboard
              </h1>
              <p className="text-xs text-gray-400 mt-0.5">Real-time Market Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg border border-gray-700">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300 font-medium">Live</span>
          </div>
        </div>
      </div>

      {/* 종합 점수 헤더 */}
      <CompositeScoreHeader />

      {/* 메인 컨텐츠 */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* 왼쪽: 차트 영역 */}
          <div className="lg:col-span-8">
            <RealTimeChart />
          </div>

          {/* 오른쪽: 탭 + 지표 */}
          <div className="lg:col-span-4">
            <UpbitStyleTabs tabs={tabs} />
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="mt-16 py-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-8 text-center">
          <p className="text-gray-500 text-sm">© 2024 Crypto Signal Dashboard. All rights reserved.</p>
          <p className="text-gray-600 text-xs mt-2">Powered by Next.js & Vercel</p>
        </div>
      </div>
    </div>
  );
}
