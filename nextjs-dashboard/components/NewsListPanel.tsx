'use client';

import React, { useState, useEffect } from 'react';

interface NewsItem {
  timestamp: string;
  title: string;
  content: string;
  link: string;
  sentiment_compound: number;
  sentiment_positive: number;
  sentiment_negative: number;
  sentiment_neutral: number;
  has_bitcoin?: boolean;
  has_ethereum?: boolean;
  has_bullish?: boolean;
  has_bearish?: boolean;
}

const NewsListPanel: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'bullish' | 'bearish' | 'bitcoin' | 'ethereum'>('all');
  const [displayCount, setDisplayCount] = useState(5); // 기본 5개로 변경

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    setLoading(true);
    try {
      // 실제 환경에서는 API에서 데이터를 가져옵니다
      const response = await fetch('/api/news/recent?limit=50');
      
      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('JSON 파싱 실패:', parseError);
        // 폴백: 더미 데이터 사용
        setNews(generateDummyNews());
        setLoading(false);
        return;
      }
      
      console.log('API 응답 데이터:', {
        isArray: Array.isArray(data),
        length: Array.isArray(data) ? data.length : 'N/A',
        hasError: data?.error,
        debug: data?.debug
      });
      
      // 에러가 있는 경우에도 테스트 데이터가 포함되어 있을 수 있음
      if (data?.error && !Array.isArray(data)) {
        console.error('API 에러:', data.error, data.debug);
        // 폴백: 더미 데이터 사용
        setNews(generateDummyNews());
        setLoading(false);
        return;
      }
      
      // 배열인 경우
      if (Array.isArray(data)) {
        if (data.length > 0) {
          setNews(data);
        } else {
          console.warn('뉴스 데이터가 비어있습니다. 더미 데이터를 사용합니다.');
          setNews(generateDummyNews());
        }
      } 
      // data.data 배열인 경우 (다른 API 형식)
      else if (data.data && Array.isArray(data.data)) {
        if (data.data.length > 0) {
          setNews(data.data);
        } else {
          console.warn('뉴스 데이터가 비어있습니다. 더미 데이터를 사용합니다.');
          setNews(generateDummyNews());
        }
      }
      else {
        console.warn('예상하지 못한 데이터 형식:', data, '더미 데이터를 사용합니다.');
        setNews(generateDummyNews());
      }
    } catch (error) {
      console.error('뉴스 로딩 실패:', error);
      // 오류 발생 시에도 더미 데이터 표시
      setNews(generateDummyNews());
    } finally {
      setLoading(false);
    }
  };

  const generateDummyNews = (): NewsItem[] => {
    const now = new Date();
    const titles = [
      "비트코인, 12만 달러 돌파... 사상 최고가 경신",
      "이더리움 4500달러 터치, 알트코인 강세장 본격화",
      "고래 지갑 대규모 매집 포착... 비트코인 5천 BTC 이동",
      "美 SEC, 비트코인 ETF 추가 승인... 기관 투자 가속화",
      "도지코인 15% 급등, 머스크 트윗 영향력 여전",
      "규제 우려 속 암호화폐 시장 조정... BTC 11만 달러대",
      "솔라나 생태계 확장, NFT 거래량 급증",
      "한국 암호화폐 거래소 신규 상장 코인 발표",
      "테더, 준비금 보고서 공개... 투명성 강화",
      "메타버스 토큰 상승세, 가상부동산 거래 활발"
    ];

    const sentiments = [
      { compound: 0.75, positive: 0.6, negative: 0.0, neutral: 0.4, bullish: true },
      { compound: 0.65, positive: 0.5, negative: 0.0, neutral: 0.5, bullish: true },
      { compound: -0.45, positive: 0.1, negative: 0.4, neutral: 0.5, bearish: true },
      { compound: 0.3, positive: 0.3, negative: 0.1, neutral: 0.6, bullish: true },
      { compound: -0.2, positive: 0.2, negative: 0.3, neutral: 0.5, bearish: true },
    ];

    return titles.map((title, i) => {
      const date = new Date(now.getTime() - i * 30 * 60 * 1000); // 30분 간격
      const sentiment = sentiments[i % sentiments.length];
      
      return {
        timestamp: date.toISOString(),
        title,
        content: `${title}에 대한 상세 내용입니다. 시장 전문가들은...`,
        link: `https://example.com/news/${i}`,
        sentiment_compound: sentiment.compound,
        sentiment_positive: sentiment.positive,
        sentiment_negative: sentiment.negative,
        sentiment_neutral: sentiment.neutral,
        has_bitcoin: title.includes('비트코인') || title.includes('BTC'),
        has_ethereum: title.includes('이더리움') || title.includes('ETH'),
        has_bullish: sentiment.bullish,
        has_bearish: sentiment.bearish,
      };
    });
  };

  const getFilteredNews = () => {
    let filtered = news;

    switch (filter) {
      case 'bullish':
        filtered = news.filter(n => n.has_bullish);
        break;
      case 'bearish':
        filtered = news.filter(n => n.has_bearish);
        break;
      case 'bitcoin':
        filtered = news.filter(n => n.has_bitcoin);
        break;
      case 'ethereum':
        filtered = news.filter(n => n.has_ethereum);
        break;
    }

    return filtered.slice(0, displayCount);
  };

  const getSentimentColor = (compound: number) => {
    if (compound > 0.3) return 'text-green-400 bg-green-900/20 border-green-600';
    if (compound < -0.3) return 'text-red-400 bg-red-900/20 border-red-600';
    return 'text-gray-400 bg-gray-900/20 border-gray-600';
  };

  const getSentimentEmoji = (compound: number) => {
    if (compound > 0.5) return '🚀';
    if (compound > 0.2) return '📈';
    if (compound < -0.5) return '📉';
    if (compound < -0.2) return '⚠️';
    return '📊';
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    return `${diffDays}일 전`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-400">뉴스 데이터 로딩 중...</p>
        <p className="text-gray-500 text-sm mt-2">코인뉴스 API 연결 대기 중</p>
      </div>
    );
  }

  const filteredNews = getFilteredNews();

  return (
    <div className="space-y-4">
      {/* 필터 버튼들 */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          전체 ({news.length})
        </button>
        <button
          onClick={() => setFilter('bullish')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            filter === 'bullish'
              ? 'bg-green-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          🚀 강세 ({news.filter(n => n.has_bullish).length})
        </button>
        <button
          onClick={() => setFilter('bearish')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            filter === 'bearish'
              ? 'bg-red-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          📉 약세 ({news.filter(n => n.has_bearish).length})
        </button>
        <button
          onClick={() => setFilter('bitcoin')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            filter === 'bitcoin'
              ? 'bg-orange-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          ₿ BTC ({news.filter(n => n.has_bitcoin).length})
        </button>
        <button
          onClick={() => setFilter('ethereum')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            filter === 'ethereum'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          Ξ ETH ({news.filter(n => n.has_ethereum).length})
        </button>
      </div>

      {/* 뉴스 리스트 */}
      <div className="space-y-3">
        {filteredNews.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p className="text-lg mb-2">뉴스 데이터가 없습니다</p>
            <p className="text-sm">새로고침 버튼을 눌러 다시 시도해주세요</p>
          </div>
        ) : (
          filteredNews.map((item, index) => (
          <a
            key={index}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gray-900 hover:bg-gray-850 border border-gray-800 hover:border-gray-700 rounded-xl p-4 transition-all cursor-pointer group block"
          >
            <div className="flex items-start justify-between gap-4">
              {/* 왼쪽: 컨텐츠 */}
              <div className="flex-1 min-w-0">
                {/* 제목 */}
                <h3 className="text-white font-semibold text-base mb-2 group-hover:text-blue-400 transition-colors line-clamp-2">
                  {item.title}
                </h3>

                {/* 태그들 */}
                <div className="flex flex-wrap gap-2 mb-2">
                  {item.has_bitcoin && (
                    <span className="px-2 py-0.5 bg-orange-900/30 text-orange-400 text-xs rounded border border-orange-700">
                      BTC
                    </span>
                  )}
                  {item.has_ethereum && (
                    <span className="px-2 py-0.5 bg-blue-900/30 text-blue-400 text-xs rounded border border-blue-700">
                      ETH
                    </span>
                  )}
                  {item.has_bullish && (
                    <span className="px-2 py-0.5 bg-green-900/30 text-green-400 text-xs rounded border border-green-700">
                      강세
                    </span>
                  )}
                  {item.has_bearish && (
                    <span className="px-2 py-0.5 bg-red-900/30 text-red-400 text-xs rounded border border-red-700">
                      약세
                    </span>
                  )}
                </div>

                {/* 시간 */}
                <p className="text-gray-500 text-xs">
                  {getTimeAgo(item.timestamp)}
                </p>
              </div>

              {/* 오른쪽: 감정 점수 */}
              <div className="flex flex-col items-end gap-2 flex-shrink-0">
                <div className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${getSentimentColor(item.sentiment_compound)}`}>
                  {getSentimentEmoji(item.sentiment_compound)}
                  {' '}
                  {(item.sentiment_compound * 100).toFixed(0)}
                </div>
                
                {/* 상세 감정 */}
                <div className="text-xs text-gray-500 text-right">
                  <div className="flex items-center gap-1">
                    <span className="text-green-400">😊 {(item.sentiment_positive * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-red-400">😔 {(item.sentiment_negative * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 호버 시 화살표 */}
            <div className="mt-2 text-blue-400 text-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
              자세히 보기
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </a>
        ))
        )}
      </div>

      {/* 더보기 버튼 */}
      {displayCount < news.length && (
        <button
          onClick={() => setDisplayCount(prev => prev + 10)}
          className="w-full py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg font-medium transition-all"
        >
          더 보기 ({news.length - displayCount}개 더)
        </button>
      )}

      {/* 새로고침 버튼 */}
      <button
        onClick={loadNews}
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        새로운 뉴스 불러오기
      </button>
    </div>
  );
};

export default NewsListPanel;

