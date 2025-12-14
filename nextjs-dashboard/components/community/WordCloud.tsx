'use client';

import { useEffect, useState, useMemo } from 'react';
import { DateRangePicker } from 'react-date-range';
import Wordcloud from '@visx/wordcloud/lib/Wordcloud';
import { scaleLog } from '@visx/scale';
import { Text } from '@visx/text';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import { useCommunity } from '../../contexts/CommunityContext';

interface WordData {
  text: string;
  value: number;
  pos: number;
  neg: number;
  neu: number;
}

export default function WordCloud() {
  const { setSelectedKeyword } = useCommunity();

  const [keywords, setKeywords] = useState<WordData[]>([]);
  const [sentiment, setSentiment] = useState('all');
  const [range, setRange] = useState('30d');
  const [mounted, setMounted] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);

  const [customRange, setCustomRange] = useState([
    {
      startDate: new Date(Date.now() - 30 * 86400000),
      endDate: new Date(),
      key: 'selection',
    },
  ]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchData = async () => {
    let url = `/api/community/wordcloud?sentiment=${sentiment}&range=${range}`;
    if (range === 'custom') {
      url += `&from=${customRange[0].startDate.toISOString()}&to=${customRange[0].endDate.toISOString()}`;
    }

    const res = await fetch(url);
    const json = await res.json();

    if (!json.keywords) {
      setKeywords([]);
      return;
    }

    setKeywords(
      json.keywords.map((k: any) => ({
        text: k.word,
        value: k.total_count,
        pos: k.positive,
        neg: k.negative,
        neu: k.neutral,
      }))
    );
  };

  useEffect(() => {
    fetchData();
  }, [sentiment, range, customRange]);

  useEffect(() => {
    if (range === 'custom') {
      setShowCalendar(true);
    }
  }, [range]);

  const getColor = (word: WordData) => {
    if (sentiment === 'positive') return '#22c55e';
    if (sentiment === 'neutral') return '#60a5fa';
    if (sentiment === 'negative') return '#ef4444';

    if (word.pos > word.neg && word.pos > word.neu) return '#22c55e';
    if (word.neg > word.pos && word.neg > word.neu) return '#ef4444';
    return '#60a5fa';
  };

  const fontScale = useMemo(() => {
    const values = keywords.map((w) => w.value);
    const min = Math.min(...values, 1);
    const max = Math.max(...values, 1);
    return scaleLog({
      domain: [min, max],
      range: [14, 42],
    });
  }, [keywords]);

  const fontSizeSetter = (datum: WordData) => fontScale(datum.value);

  const handleApplyDate = () => {
    setShowCalendar(false);
    fetchData();
  };

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 text-gray-200">
      <h2 className="text-xl font-semibold mb-4">Top Trending Keywords</h2>

      {/* 상단 필터 */}
      <div className="flex items-center gap-4 mb-4">
        <select
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white"
          value={sentiment}
          onChange={(e) => setSentiment(e.target.value)}
        >
          <option value="all">전체</option>
          <option value="positive">긍정</option>
          <option value="neutral">중립</option>
          <option value="negative">부정</option>
        </select>

        <select
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white"
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          <option value="7d">최근 7일</option>
          <option value="30d">최근 30일</option>
          <option value="custom">직접 선택</option>
        </select>
      </div>

      {/* 범례 */}
      <div className="flex items-center gap-6 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-green-500"></span>
          <span className="text-slate-300">긍정 (Positive)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-blue-400"></span>
          <span className="text-slate-300">중립 (Neutral)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-red-500"></span>
          <span className="text-slate-300">부정 (Negative)</span>
        </div>
      </div>

      {/* Custom Range */}
      {showCalendar && range === 'custom' && (
        <div className="mb-6 relative z-50">
          <div className="bg-slate-800 rounded-xl shadow-2xl p-5 inline-block border border-slate-700">
            <div className="flex justify-between items-center mb-4">
              <span className="text-white font-semibold text-lg">
                📅 날짜 범위 선택
              </span>
              <button
                onClick={() => {
                  setShowCalendar(false);
                  setRange('30d');
                }}
                className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-700 transition-colors"
                title="닫기"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
            <style jsx global>{`
              .rdrCalendarWrapper {
                background: #1e293b !important;
                color: white !important;
              }
              .rdrDateDisplayWrapper {
                background: #334155 !important;
              }
              .rdrDateDisplayItem {
                background: #475569 !important;
                border-color: #64748b !important;
              }
              .rdrDateDisplayItem input {
                color: white !important;
              }
              .rdrMonthAndYearWrapper {
                background: #1e293b !important;
              }
              .rdrMonthAndYearPickers select {
                color: white !important;
                background: #334155 !important;
              }
              .rdrMonthAndYearPickers select option {
                background: #334155 !important;
              }
              .rdrNextPrevButton {
                background: #334155 !important;
              }
              .rdrNextPrevButton:hover {
                background: #475569 !important;
              }
              .rdrNextPrevButton i {
                border-color: transparent transparent transparent white !important;
              }
              .rdrPprevButton i {
                border-color: transparent white transparent transparent !important;
              }
              .rdrMonth {
                background: #1e293b !important;
              }
              .rdrWeekDays {
                background: #1e293b !important;
              }
              .rdrWeekDay {
                color: #94a3b8 !important;
              }
              .rdrDays {
                background: #1e293b !important;
              }
              .rdrDay {
                color: white !important;
              }
              .rdrDayNumber span {
                color: white !important;
              }
              .rdrDayPassive .rdrDayNumber span {
                color: #64748b !important;
              }
              .rdrDayToday .rdrDayNumber span:after {
                background: #3b82f6 !important;
              }
              .rdrDayHovered {
                background: #334155 !important;
              }
              .rdrDayStartPreview,
              .rdrDayEndPreview,
              .rdrDayInPreview {
                border-color: #3b82f6 !important;
              }
              .rdrDefinedRangesWrapper {
                background: #1e293b !important;
                border-color: #334155 !important;
              }
              .rdrStaticRange {
                background: #1e293b !important;
                border-color: #334155 !important;
              }
              .rdrStaticRange:hover .rdrStaticRangeLabel {
                background: #334155 !important;
              }
              .rdrStaticRangeLabel {
                color: white !important;
              }
              .rdrInputRange {
                background: #1e293b !important;
              }
              .rdrInputRangeInput {
                background: #334155 !important;
                border-color: #475569 !important;
                color: white !important;
              }
              .rdrInputRanges {
                background: #1e293b !important;
              }
              .rdrInputRanges span {
                color: #94a3b8 !important;
              }
            `}</style>
            <DateRangePicker
              ranges={customRange}
              onChange={(v) => setCustomRange([v.selection] as any)}
              rangeColors={['#3b82f6']}
              color="#3b82f6"
            />
            <div className="mt-4 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowCalendar(false);
                  setRange('30d');
                }}
                className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleApplyDate}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors font-medium"
              >
                적용
              </button>
            </div>
          </div>
        </div>
      )}

      {/* WordCloud */}
      <div className="h-[420px] flex items-center justify-center bg-slate-800/50 border border-slate-700 rounded-xl p-4 overflow-hidden">
        {!mounted ? (
          <div className="text-slate-500 text-sm">로딩 중...</div>
        ) : keywords.length > 0 ? (
          <svg width={650} height={380} viewBox="0 0 650 380">
            <rect width={650} height={380} fill="transparent" />
            <Wordcloud
              words={keywords.slice(0, 50)}
              width={650}
              height={380}
              fontSize={fontSizeSetter}
              font="Arial"
              padding={5}
              spiral="archimedean"
              rotate={0}
              random={() => 0.5}
            >
              {(cloudWords) =>
                cloudWords.map((w, i) => {
                  const wordData = keywords.find((k) => k.text === w.text);
                  return (
                    <Text
                      key={`${w.text}-${i}`}
                      fill={wordData ? getColor(wordData) : '#60a5fa'}
                      textAnchor="middle"
                      transform={`translate(${w.x}, ${w.y}) rotate(${w.rotate})`}
                      fontSize={w.size}
                      fontFamily={w.font}
                      fontWeight="bold"
                      style={{
                        textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
                        cursor: 'pointer',
                      }}
                      onClick={() => {
                        setSelectedKeyword(w.text || '');
                        // 스크롤을 TopPosts 섹션으로 이동
                        const topPostsEl = document.querySelector(
                          '[data-section="top-posts"]'
                        );
                        if (topPostsEl) {
                          topPostsEl.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start',
                          });
                        }
                      }}
                    >
                      {w.text}
                    </Text>
                  );
                })
              }
            </Wordcloud>
          </svg>
        ) : (
          <div className="text-slate-500 text-sm">키워드가 없습니다.</div>
        )}
      </div>

      {/* 안내 문구 */}
      <p className="text-center text-slate-500 text-sm mt-3">
        💡 키워드를 클릭하면 해당 단어가 포함된 게시글을 검색합니다
      </p>
    </div>
  );
}
