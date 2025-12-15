'use client';

import { useEffect, useState, useMemo, useRef } from 'react';
import { DateRange } from 'react-date-range';
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
  const [mounted, setMounted] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const calendarRef = useRef<HTMLDivElement>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<
    '7d' | '30d' | '90d' | 'custom'
  >('30d');

  // 날짜 범위 필터 - 초기값은 null, 데이터 로드 후 설정
  const [dateRange, setDateRange] = useState<{
    startDate: Date;
    endDate: Date;
    key: string;
  } | null>(null);

  // API에서 반환된 실제 조회 기간
  const [dataFrom, setDataFrom] = useState<Date | null>(null);
  const [dataTo, setDataTo] = useState<Date | null>(null);

  // 전체 데이터 범위
  const [dataEarliest, setDataEarliest] = useState<Date | null>(null);
  const [dataLatest, setDataLatest] = useState<Date | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchData = async () => {
    let url = `/api/community/wordcloud?sentiment=${sentiment}`;

    // dateRange가 있으면 custom, 없으면 기본 30일
    if (dateRange) {
      url += `&range=custom&from=${dateRange.startDate.toISOString()}&to=${dateRange.endDate.toISOString()}`;
    } else {
      url += `&range=30d`;
    }

    const res = await fetch(url);
    const json = await res.json();

    if (!json.keywords) {
      setKeywords([]);
      return;
    }

    // API에서 반환된 실제 조회 기간 저장
    if (json.from) setDataFrom(new Date(json.from));
    if (json.to) setDataTo(new Date(json.to));
    if (json.dataEarliest) setDataEarliest(new Date(json.dataEarliest));
    if (json.dataLatest) setDataLatest(new Date(json.dataLatest));

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
  }, [sentiment, dateRange]);

  // 달력 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        calendarRef.current &&
        !calendarRef.current.contains(event.target as Node)
      ) {
        setShowCalendar(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 text-gray-200">
      <h2 className="text-xl font-semibold mb-4">Top Trending Keywords</h2>

      {/* 상단 필터 */}
      <div className="flex items-center gap-4 mb-4">
        {/* 기간 달력 필터 */}
        <div className="relative" ref={calendarRef}>
          <button
            onClick={() => setShowCalendar(!showCalendar)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm hover:bg-slate-700 transition-colors"
          >
            📅{' '}
            {dataFrom && dataTo
              ? `${dataFrom.toLocaleDateString('ko-KR', {
                  month: 'short',
                  day: 'numeric',
                })} ~ ${dataTo.toLocaleDateString('ko-KR', {
                  month: 'short',
                  day: 'numeric',
                })}`
              : '기간 선택'}
          </button>

          {showCalendar && (
            <div className="absolute top-full left-0 mt-2 z-50 rounded-xl overflow-hidden shadow-2xl border border-slate-700">
              <style jsx global>{`
                .wordcloud-calendar .rdrCalendarWrapper,
                .wordcloud-calendar .rdrDateDisplayWrapper,
                .wordcloud-calendar .rdrMonthAndYearWrapper {
                  background: #0f172a !important;
                }
                .wordcloud-calendar .rdrMonthAndYearPickers select {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                  border: 1px solid #334155 !important;
                }
                .wordcloud-calendar .rdrMonthAndYearPickers select option {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                }
                .wordcloud-calendar .rdrNextPrevButton {
                  background: #1e293b !important;
                }
                .wordcloud-calendar .rdrNextPrevButton:hover {
                  background: #334155 !important;
                }
                .wordcloud-calendar .rdrNextPrevButton i {
                  border-color: transparent transparent transparent #94a3b8 !important;
                }
                .wordcloud-calendar .rdrPprevButton i {
                  border-color: transparent #94a3b8 transparent transparent !important;
                }
                .wordcloud-calendar .rdrMonth {
                  background: #0f172a !important;
                }
                .wordcloud-calendar .rdrWeekDay {
                  color: #64748b !important;
                }
                .wordcloud-calendar .rdrDay {
                  color: #e2e8f0 !important;
                }
                .wordcloud-calendar .rdrDayNumber span {
                  color: #e2e8f0 !important;
                }
                .wordcloud-calendar .rdrDayPassive .rdrDayNumber span {
                  color: #475569 !important;
                }
                .wordcloud-calendar .rdrDayToday .rdrDayNumber span:after {
                  background: #3b82f6 !important;
                }
                .wordcloud-calendar .rdrDayDisabled {
                  background-color: #1e293b !important;
                }
                .wordcloud-calendar .rdrDayDisabled .rdrDayNumber span {
                  color: #475569 !important;
                }
                .wordcloud-calendar .rdrDateDisplayItem {
                  background: #1e293b !important;
                  border-color: #334155 !important;
                }
                .wordcloud-calendar .rdrDateDisplayItem input {
                  color: #e2e8f0 !important;
                }
                .wordcloud-calendar .rdrDateDisplayItemActive {
                  border-color: #3b82f6 !important;
                }
                .wordcloud-calendar .rdrInRange,
                .wordcloud-calendar .rdrStartEdge,
                .wordcloud-calendar .rdrEndEdge {
                  background: #3b82f6 !important;
                }
                .wordcloud-calendar .rdrDayStartPreview,
                .wordcloud-calendar .rdrDayInPreview,
                .wordcloud-calendar .rdrDayEndPreview {
                  border-color: #3b82f6 !important;
                }
              `}</style>
              <div className="wordcloud-calendar">
                <DateRange
                  ranges={
                    dateRange
                      ? [dateRange]
                      : [
                          {
                            startDate: dataFrom || new Date(),
                            endDate: dataTo || new Date(),
                            key: 'selection',
                          },
                        ]
                  }
                  onChange={(item: any) => {
                    setDateRange(item.selection);
                    setSelectedPeriod('custom');
                  }}
                  months={1}
                  direction="horizontal"
                  rangeColors={['#3b82f6']}
                />
              </div>
              <div className="bg-slate-900 p-2 flex justify-end gap-2 border-t border-slate-700">
                <button
                  onClick={() => {
                    // 초기화: 데이터 기준 최근 30일
                    setDateRange(null);
                    setSelectedPeriod('30d');
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedPeriod === '30d'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  30일(초기화)
                </button>
                <button
                  onClick={() => {
                    // 데이터 기준 최근 90일
                    if (dataLatest) {
                      const startDate = new Date(dataLatest);
                      startDate.setDate(startDate.getDate() - 90);
                      setDateRange({
                        startDate,
                        endDate: dataLatest,
                        key: 'selection',
                      });
                    }
                    setSelectedPeriod('90d');
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedPeriod === '90d'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  90일
                </button>
                <button
                  onClick={() => setShowCalendar(false)}
                  className="px-2 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-500"
                >
                  확인
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 감성 필터 */}
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
