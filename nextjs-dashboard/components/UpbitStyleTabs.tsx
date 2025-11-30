'use client';

import { useState, ReactNode } from 'react';

interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
}

interface UpbitStyleTabsProps {
  tabs: TabItem[];
}

export default function UpbitStyleTabs({ tabs }: UpbitStyleTabsProps) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.id || '');

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl">
      {/* 탭 헤더 */}
      <div className="flex border-b border-gray-700 bg-gray-850">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-1 px-4 py-3.5 text-sm font-medium transition-all duration-200
              border-b-2 relative
              ${activeTab === tab.id
                ? 'text-blue-400 border-blue-400 bg-gray-800/50'
                : 'text-gray-400 border-transparent hover:text-gray-200 hover:bg-gray-800/30'
              }
            `}
          >
            <div className="flex flex-col items-center">
              {tab.label.split('\n').map((line, idx) => (
                <span key={idx}>{line}</span>
              ))}
            </div>
            {activeTab === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500" />
            )}
          </button>
        ))}
      </div>

      {/* 탭 컨텐츠 */}
      <div className="p-0">
        {tabs.find(tab => tab.id === activeTab)?.content}
      </div>
    </div>
  );
}

