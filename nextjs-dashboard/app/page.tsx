'use client';

// import { useEffect, useState } from 'react';
import CompositeScoreHeader from '../components/CompositeScoreHeader';
import UpbitStyleTabs from '../components/UpbitStyleTabs';
import CorrelationIndicators from '../components/CorrelationIndicators';
import NewsList from '../components/NewsList';

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

  // 모의 상관관계 데이터
  const priceCorrelations = [
    { name: '텔레그램 게시글 수', value: 0.65 },
    { name: '텔레그램 감성', value: 0.42 },
    { name: '코인니스 뉴스 수', value: 0.58 },
    { name: '코인니스 감성', value: 0.31 },
    { name: '트위터 게시글 수', value: 0.72 },
    { name: '트위터 감성', value: 0.54 },
  ];

  const whaleCorrelations = [
    { name: '텔레그램 게시글 수', value: 0.48 },
    { name: '텔레그램 감성', value: 0.23 },
    { name: '코인니스 뉴스 수', value: 0.67 },
    { name: '코인니스 감성', value: 0.45 },
    { name: '트위터 게시글 수', value: 0.55 },
    { name: '트위터 감성', value: 0.38 },
  ];

  const tabs = [
    {
      id: 'price',
      label: '코인가격 관계',
      content: <CorrelationIndicators correlations={priceCorrelations} title="코인 가격" />
    },
    {
      id: 'whale',
      label: '고래지갑 관계',
      content: <CorrelationIndicators correlations={whaleCorrelations} title="고래 거래" />
    },
    {
      id: 'news',
      label: '지금 뉴스',
      content: <NewsList />
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
      <CompositeScoreHeader
        score={75.3}
        change={5.2}
        changePercent={8.45}
      />

      {/* 메인 컨텐츠 */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* 왼쪽: 차트 영역 */}
          <div className="lg:col-span-8">
            <div className="bg-gradient-to-br from-gray-800 to-gray-850 border border-gray-700 rounded-xl p-8 h-[500px] flex items-center justify-center shadow-2xl">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
                  <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <p className="text-lg font-semibold text-gray-200 mb-2">시계열 차트</p>
                <p className="text-sm text-gray-400">데이터 시각화 준비 중...</p>
                <div className="mt-6 flex gap-3 justify-center">
                  <div className="px-4 py-2 bg-gray-700 rounded-lg text-xs text-gray-400">실시간 업데이트</div>
                  <div className="px-4 py-2 bg-gray-700 rounded-lg text-xs text-gray-400">AI 분석</div>
                </div>
              </div>
            </div>
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
