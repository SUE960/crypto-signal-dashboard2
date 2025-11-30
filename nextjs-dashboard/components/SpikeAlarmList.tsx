'use client';

import React, { useState, useEffect } from 'react';

interface SpikeAlarm {
  timestamp: string;
  date: string;
  priorityScore: number;
  alertLevel: string;
  reasons: string[];
  details: {
    whale_zscore?: number;
    telegram_zscore?: number;
    twitter_zscore?: number;
    news_zscore?: number;
    btc_price?: number;
    eth_price?: number;
    telegram_sentiment?: number;
    twitter_sentiment?: number;
    news_sentiment?: number;
    price_change?: {
      btc: number;
      eth: number;
    };
  };
}

export default function SpikeAlarmList() {
  const [spikes, setSpikes] = useState<SpikeAlarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'medium'>('all');

  useEffect(() => {
    loadSpikeAlarms();
  }, []);

  const loadSpikeAlarms = async () => {
    try {
      const response = await fetch('/api/spike-points?range=30d');
      if (response.ok) {
        const data = await response.json();
        setSpikes(data);
      }
    } catch (error) {
      console.error('Spike 알람 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSpikes = spikes.filter((spike) => {
    if (filter === 'all') return true;
    return spike.alertLevel === filter.toUpperCase();
  });

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('ko-KR', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAlertLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500 text-white';
      case 'HIGH':
        return 'bg-orange-500 text-white';
      case 'MEDIUM':
        return 'bg-yellow-500 text-black';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="h-[500px] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gray-700 animate-pulse">
            <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-sm text-gray-400">Spike 알람 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (filteredSpikes.length === 0) {
    return (
      <div className="h-[500px] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gray-700">
            <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="font-semibold mb-1 text-gray-400">Spike 알람 없음</p>
          <p className="text-sm text-gray-500">현재 구매 시점으로 판단된 Spike가 없습니다</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl">
      {/* 필터 */}
      <div className="px-5 py-4 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-850">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-gray-100">Spike 알람 목록</h3>
          <span className="text-xs text-gray-400">
            총 {filteredSpikes.length}개
          </span>
        </div>
        <div className="flex gap-2">
          {(['all', 'critical', 'high', 'medium'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
            >
              {f === 'all' ? '전체' : f === 'critical' ? '긴급' : f === 'high' ? '높음' : '보통'}
            </button>
          ))}
        </div>
      </div>

      {/* 알람 리스트 */}
      <div className="max-h-[420px] overflow-y-auto">
        {filteredSpikes.map((spike, index) => (
          <div
            key={index}
            className="px-5 py-4 border-b border-gray-700/50 hover:bg-gray-750 transition-colors group"
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">⭐</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-200">
                      {formatDate(spike.timestamp)}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${getAlertLevelColor(spike.alertLevel)}`}>
                      {spike.alertLevel}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    우선순위 점수: {spike.priorityScore}점
                  </div>
                </div>
              </div>
            </div>

            {/* 감지된 이유 */}
            <div className="mt-3 space-y-1">
              {spike.reasons.map((reason, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-gray-300">
                  <span className="text-yellow-400 mt-0.5">•</span>
                  <span>{reason}</span>
                </div>
              ))}
            </div>

            {/* 상세 정보 */}
            <div className="mt-3 pt-3 border-t border-gray-700/50 grid grid-cols-2 gap-2 text-xs">
              {spike.details.whale_zscore && (
                <div className="text-gray-400">
                  고래 Z-score: <span className="text-gray-200 font-medium">{spike.details.whale_zscore.toFixed(2)}</span>
                </div>
              )}
              {spike.details.telegram_zscore && (
                <div className="text-gray-400">
                  텔레그램 Z-score: <span className="text-gray-200 font-medium">{spike.details.telegram_zscore.toFixed(2)}</span>
                </div>
              )}
              {spike.details.twitter_zscore && (
                <div className="text-gray-400">
                  트위터 Z-score: <span className="text-gray-200 font-medium">{spike.details.twitter_zscore.toFixed(2)}</span>
                </div>
              )}
              {spike.details.news_zscore && (
                <div className="text-gray-400">
                  뉴스 Z-score: <span className="text-gray-200 font-medium">{spike.details.news_zscore.toFixed(2)}</span>
                </div>
              )}
              {spike.details.btc_price && (
                <div className="text-gray-400">
                  BTC 가격: <span className="text-gray-200 font-medium">${spike.details.btc_price.toLocaleString()}</span>
                </div>
              )}
              {spike.details.eth_price && (
                <div className="text-gray-400">
                  ETH 가격: <span className="text-gray-200 font-medium">${spike.details.eth_price.toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 하단 버튼 */}
      <div className="border-t border-gray-700">
        <a
          href="https://whale-arbitrage-qwodzy8wpnhpgxaxt23rj8.streamlit.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full flex items-center justify-center gap-2 px-5 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold text-sm transition-all duration-200 hover:shadow-lg"
        >
          <span>바로 거래하기</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>
    </div>
  );
}

