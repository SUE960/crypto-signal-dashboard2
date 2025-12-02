'use client';

import { useEffect, useState, useMemo } from 'react';
import { DateRangePicker } from 'react-date-range';
import Wordcloud from '@visx/wordcloud/lib/Wordcloud';
import { scaleLog } from '@visx/scale';
import { Text } from '@visx/text';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';
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

export default function KeywordAnalysis() {
  const { setSelectedKeyword } = useCommunity();

  const [keywords, setKeywords] = useState<WordData[]>([]);
  const [sentiment, setSentiment] = useState('all');
  const [range, setRange] = useState('30d');
  const [mounted, setMounted] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);

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

  // Bar Chart용 데이터 (선택된 단어가 있으면 해당 단어만, 없으면 상위 10개)
  const barChartData = useMemo(() => {
    if (selectedWord) {
      const word = keywords.find((k) => k.text === selectedWord);
      if (word) {
        return [
          {
            word: word.text,
            긍정: word.pos,
            부정: word.neg,
            중립: word.neu,
            total: word.value,
          },
        ];
      }
    }
    return keywords.slice(0, 10).map((k) => ({
      word: k.text,
      긍정: k.pos,
      부정: k.neg,
      중립: k.neu,
      total: k.value,
    }));
  }, [keywords, selectedWord]);

  // 전체 감성 통계
  const overallStats = useMemo(() => {
    const data = selectedWord
      ? keywords.filter((k) => k.text === selectedWord)
      : keywords;

    const totalPos = data.reduce((a, b) => a + b.pos, 0);
    const totalNeg = data.reduce((a, b) => a + b.neg, 0);
    const totalNeu = data.reduce((a, b) => a + b.neu, 0);
    const total = totalPos + totalNeg + totalNeu;

    return {
      total,
      posRate: total ? ((totalPos / total) * 100).toFixed(1) : '0',
      negRate: total ? ((totalNeg / total) * 100).toFixed(1) : '0',
      neuRate: total ? ((totalNeu / total) * 100).toFixed(1) : '0',
    };
  }, [keywords, selectedWord]);

  const handleWordClick = (wordText: string) => {
    if (selectedWord === wordText) {
      setSelectedWord(null);
    } else {
      setSelectedWord(wordText);
    }
  };

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 text-gray-200">
      <h2 className="text-2xl font-bold mb-4">키워드 감성 분석</h2>

      {/* 상단 필터 */}
      <div className="flex flex-wrap items-center gap-4 mb-4">
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

        {selectedWord && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-cyan-400 bg-cyan-400/10 px-3 py-1 rounded-full">
              🔍 "{selectedWord}" 선택됨
            </span>
            <button
              onClick={() => setSelectedWord(null)}
              className="text-sm text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-700 transition-colors"
            >
              ✕ 해제
            </button>
          </div>
        )}
      </div>

      {/* 범례 */}
      <div className="flex items-center gap-6 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-green-500"></span>
          <span className="text-slate-300">긍정 ({overallStats.posRate}%)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-blue-400"></span>
          <span className="text-slate-300">중립 ({overallStats.neuRate}%)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-red-500"></span>
          <span className="text-slate-300">부정 ({overallStats.negRate}%)</span>
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
                ✕
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
                border-color: transparent transparent transparent #94a3b8 !important;
              }
              .rdrPprevButton i {
                border-color: transparent #94a3b8 transparent transparent !important;
              }
              .rdrMonth {
                background: #1e293b !important;
              }
              .rdrWeekDay {
                color: #64748b !important;
              }
              .rdrDay {
                color: #e2e8f0 !important;
              }
              .rdrDayNumber span {
                color: #e2e8f0 !important;
              }
              .rdrDayPassive .rdrDayNumber span {
                color: #475569 !important;
              }
              .rdrDayToday .rdrDayNumber span:after {
                background: #3b82f6 !important;
              }
              .rdrDayDisabled {
                background-color: #1e293b !important;
              }
              .rdrDayDisabled .rdrDayNumber span {
                color: #475569 !important;
              }
              .rdrSelected,
              .rdrInRange,
              .rdrStartEdge,
              .rdrEndEdge {
                background: #3b82f6 !important;
              }
              .rdrDayStartPreview,
              .rdrDayInPreview,
              .rdrDayEndPreview {
                border-color: #60a5fa !important;
              }
              .rdrDefinedRangesWrapper {
                display: none !important;
              }
            `}</style>
            <DateRangePicker
              ranges={customRange}
              onChange={(item: any) => setCustomRange([item.selection])}
              months={1}
              direction="horizontal"
              rangeColors={['#3b82f6']}
              showDateDisplay={true}
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

      {/* 메인 컨텐츠: WordCloud + Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: WordCloud */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-slate-300">
            📊 Word Cloud
          </h3>
          <div className="h-[380px] flex items-center justify-center bg-slate-800/50 border border-slate-700 rounded-xl p-4 overflow-hidden">
            {!mounted ? (
              <div className="text-slate-500 text-sm">로딩 중...</div>
            ) : keywords.length > 0 ? (
              <svg width={450} height={340} viewBox="0 0 450 340">
                <rect width={450} height={340} fill="transparent" />
                <Wordcloud
                  words={keywords.slice(0, 50)}
                  width={450}
                  height={340}
                  fontSize={fontSizeSetter}
                  font="Arial"
                  padding={4}
                  spiral="archimedean"
                  rotate={0}
                  random={() => 0.5}
                >
                  {(cloudWords) =>
                    cloudWords.map((w, i) => {
                      const wordData = keywords.find((k) => k.text === w.text);
                      const isSelected = selectedWord === w.text;
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
                            textShadow: isSelected
                              ? '0 0 10px #22d3ee, 0 0 20px #22d3ee'
                              : '2px 2px 4px rgba(0,0,0,0.5)',
                            cursor: 'pointer',
                            opacity: selectedWord && !isSelected ? 0.4 : 1,
                            transition: 'opacity 0.2s',
                          }}
                          onClick={() => handleWordClick(w.text || '')}
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
          <p className="text-center text-slate-500 text-xs mt-2">
            💡 키워드 클릭 시 오른쪽 차트에서 감성 비율 확인
          </p>
        </div>

        {/* Right: Sentiment Breakdown Bar Chart */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-slate-300">
            📈 Sentiment Breakdown
            {selectedWord && (
              <span className="text-cyan-400 text-sm font-normal ml-2">
                - "{selectedWord}"
              </span>
            )}
          </h3>
          <div className="h-[380px] bg-slate-800/50 border border-slate-700 rounded-xl p-4">
            {barChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={barChartData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
                >
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis
                    type="category"
                    dataKey="word"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    width={80}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: '12px',
                      color: '#fff',
                    }}
                    formatter={(value: number, name: string) => [
                      `${value}건`,
                      name,
                    ]}
                  />
                  <Legend wrapperStyle={{ color: '#CBD5E1' }} />
                  <Bar dataKey="긍정" stackId="a" fill="#22c55e" />
                  <Bar dataKey="중립" stackId="a" fill="#60a5fa" />
                  <Bar dataKey="부정" stackId="a" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">
                데이터가 없습니다.
              </div>
            )}
          </div>
          <p className="text-center text-slate-500 text-xs mt-2">
            {selectedWord
              ? `"${selectedWord}" 키워드의 감성 분포`
              : '상위 10개 키워드의 감성 분포 (Stacked Bar)'}
          </p>
        </div>
      </div>

      {/* 하단: TopPosts 검색 버튼 */}
      {selectedWord && (
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setSelectedKeyword(selectedWord);
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
            className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-500 hover:to-blue-500 transition-all font-medium shadow-lg"
          >
            🔍 "{selectedWord}" 포함 게시글 검색하기
          </button>
        </div>
      )}
    </div>
  );
}
