'use client';

interface UpbitStyleTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function UpbitStyleTabs({ activeTab, onTabChange }: UpbitStyleTabsProps) {
  const tabs = ['코인가격', '고래지갑', '뉴스', 'spike알람', '지금뉴스'];

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-t-xl overflow-hidden">
      <div className="flex border-b border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={`px-6 py-4 text-sm font-semibold transition-colors ${
              activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-800'
                : 'text-gray-400 hover:text-gray-300 hover:bg-gray-750'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>
    </div>
  );
}
