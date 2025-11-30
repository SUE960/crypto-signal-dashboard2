'use client';

import { useEffect, useState } from 'react';

interface NewsItem {
  timestamp: string;
  title: string;
  content: string;
  link: string;
  sentiment: number;
}

export default function NewsList() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const response = await fetch('/api/news');
      const result = await response.json();
      if (result.success && result.data) {
        setNews(result.data);
      }
    } catch (error) {
      console.error('뉴스 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(hours / 24);

      if (hours < 1) return '방금 전';
      if (hours < 24) return `${hours}시간 전`;
      if (days < 7) return `${days}일 전`;
      
      return date.toLocaleDateString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return timestamp;
    }
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.05) return 'text-green-400';
    if (sentiment < -0.05) return 'text-red-400';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="h-[500px] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gray-700 animate-pulse">
            <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <p className="text-sm text-gray-400">뉴스 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (news.length === 0) {
    return (
      <div className="h-[500px] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gray-700">
            <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
          </div>
          <p className="font-semibold mb-1 text-gray-400">뉴스 데이터 수집 중</p>
          <p className="text-sm text-gray-500">코인니스 API 연결 대기 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[500px] overflow-y-auto">
      <div className="divide-y divide-gray-700/50">
        {news.map((item, index) => (
          <a
            key={index}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="block px-5 py-4 hover:bg-gray-750 transition-colors group"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs text-gray-500">{formatDate(item.timestamp)}</span>
                  <span className={`text-xs font-medium ${getSentimentColor(item.sentiment)}`}>
                    {item.sentiment > 0.05 ? '긍정' : item.sentiment < -0.05 ? '부정' : '중립'}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-gray-200 group-hover:text-white transition-colors line-clamp-2 mb-1">
                  {item.title}
                </h4>
                {item.content && (
                  <p className="text-xs text-gray-400 line-clamp-2">
                    {item.content}
                  </p>
                )}
              </div>
              <svg 
                className="w-4 h-4 text-gray-500 group-hover:text-gray-300 flex-shrink-0 mt-1" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

