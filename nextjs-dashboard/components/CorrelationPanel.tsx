'use client';

import React, { useState } from 'react';
import {
  priceCorrelations,
  whaleCorrelations,
  newsCorrelations,
  getCorrelationPercentage,
  getSignificanceColor,
  getBarColor,
  type CorrelationItem
} from '@/lib/correlationData';
import Tooltip from './Tooltip';

type TabType = 'price' | 'whale' | 'news';

interface CorrelationPanelProps {
  defaultTab?: TabType;
}

const CorrelationPanel: React.FC<CorrelationPanelProps> = ({ defaultTab = 'price' }) => {
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab);

  const getTabData = (): CorrelationItem[] => {
    switch (activeTab) {
      case 'price':
        return priceCorrelations;
      case 'whale':
        return whaleCorrelations;
      case 'news':
        return newsCorrelations;
    }
  };

  const getTabTitle = (): string => {
    switch (activeTab) {
      case 'price':
        return '코인 가격과의 상관관계';
      case 'whale':
        return '고래 거래와의 상관관계';
      case 'news':
        return '뉴스 기반 지표';
    }
  };

  const tabData = getTabData();

  return (
    <div className="rounded-2xl bg-gradient-to-br from-gray-900 to-gray-800 p-6 shadow-2xl border border-gray-700">
      {/* 탭 헤더 */}
      <div className="flex gap-6 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('price')}
          className={`pb-3 px-4 text-base font-medium transition-all ${
            activeTab === 'price'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          코인가격 관계
        </button>
        <button
          onClick={() => setActiveTab('whale')}
          className={`pb-3 px-4 text-base font-medium transition-all ${
            activeTab === 'whale'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          고래지갑 관계
        </button>
        <button
          onClick={() => setActiveTab('news')}
          className={`pb-3 px-4 text-base font-medium transition-all ${
            activeTab === 'news'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          지금 뉴스
        </button>
      </div>

      {/* 제목 */}
      <h3 className="text-xl font-bold text-white mb-6">
        {getTabTitle()}
      </h3>

      {/* 상관관계 리스트 */}
      <div className="space-y-4">
        {tabData.map((item, index) => {
          const percentage = getCorrelationPercentage(item.correlation);
          const dotColor = getSignificanceColor(item.significance);
          const barColor = getBarColor(item.correlation, item.significance);
          const sign = item.correlation >= 0 ? '+' : '';

          return (
            <div key={index} className="group">
              {/* 라벨과 수치 */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  {/* 색상 동그라미 */}
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: dotColor }}
                  />
                  {/* 툴팁 적용된 라벨 */}
                  {item.detailedAnalysis ? (
                    <Tooltip content={item.detailedAnalysis}>
                      <span className="text-gray-200 text-base font-medium hover:text-blue-400 transition-colors cursor-help border-b border-dashed border-gray-600 hover:border-blue-400">
                        {item.label}
                      </span>
                    </Tooltip>
                  ) : (
                    <span className="text-gray-200 text-base font-medium">
                      {item.label}
                    </span>
                  )}
                </div>
                {/* 상관계수 */}
                <span
                  className="text-lg font-bold flex-shrink-0"
                  style={{ color: barColor }}
                >
                  {sign}{(item.correlation * 100).toFixed(1)}%
                </span>
              </div>

              {/* 진행 바 */}
              <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: barColor,
                  }}
                />
              </div>

              {/* 설명 (호버 시 표시) */}
              {item.description && (
                <div className="mt-2 text-sm text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  {item.description}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 하단 버튼 */}
      <button className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl text-white font-medium transition-all flex items-center justify-center gap-2">
        바로 거래하기
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>

      {/* 범례 */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-400">유의미 (p&lt;0.05)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-gray-400">약한 상관</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500" />
            <span className="text-gray-400">관계 없음</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CorrelationPanel;

