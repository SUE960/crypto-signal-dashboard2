'use client';

import { useEffect, useMemo, useState, useRef } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from 'recharts';
import { DateRange } from 'react-date-range';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import { useCommunity } from '../../contexts/CommunityContext';

type RawSpike = {
  timestamp: string;
  normalized_time?: string;
  avg_sentiment: number;
  variance: number;
  total_posts: number;
  pos: number;
  neg: number;
  neu: number;
  diff: number;
  zscore: number;
  threshold: number;
};

type SpikePoint = RawSpike & {
  time: string;
  dateLabel: string;
};

const normalizeDate = (str?: string) => {
  if (!str) return 'Invalid Date';
  const d = new Date(str);
  if (Number.isNaN(d.getTime())) return 'Invalid Date';

  const M = String(d.getUTCMonth() + 1).padStart(2, '0');
  const D = String(d.getUTCDate()).padStart(2, '0');
  const h = String(d.getUTCHours()).padStart(2, '0');

  return `${M}/${D} ${h}h`;
};

export default function SpikeTimeline() {
  const { setSelectedSpikeDate } = useCommunity();

  const [freq, setFreq] = useState<'1h' | '4h' | '1d'>('4h');
  const [coin, setCoin] = useState<'BTC' | 'ETH'>('BTC');
  const [threshold, setThreshold] = useState<number>(3.0);

  const [points, setPoints] = useState<SpikePoint[]>([]);
  const [visibleCount, setVisibleCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [thresholdOptions, setThresholdOptions] = useState<number[]>([]);

  // 그래프에서 선택한 날짜 (상세 표 필터용)
  const [selectedChartDate, setSelectedChartDate] = useState<string | null>(
    null
  );

  // 날짜 범위 필터 - 초기값은 null, 데이터 로드 후 설정
  const [dateRange, setDateRange] = useState<{
    startDate: Date;
    endDate: Date;
    key: string;
  } | null>(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const calendarRef = useRef<HTMLDivElement>(null);

  // -------------------------
  // Load spike data
  // -------------------------
  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/community/spikes?freq=${freq}&coin=${coin}&threshold=${threshold}`
      );
      const json = await res.json();
      const raw: RawSpike[] = json.spikes ?? [];

      const mapped: SpikePoint[] = raw
        .map((r) => {
          const t = r.normalized_time || r.timestamp;
          return {
            ...r,
            time: t,
            dateLabel: normalizeDate(t),
          };
        })
        .filter((r) => r.dateLabel !== 'Invalid Date')
        .sort(
          (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime()
        );

      // 전체 데이터 사용 (제한 없음)
      setPoints(mapped);
      setVisibleCount(5);

      // 데이터 범위에 맞게 dateRange 초기화 (첫 로드시만) - 기본 180일
      if (mapped.length > 0 && !dateRange) {
        const lastDate = new Date(mapped[mapped.length - 1].time);
        const startDate = new Date(lastDate);
        startDate.setDate(startDate.getDate() - 180);
        setDateRange({
          startDate,
          endDate: lastDate,
          key: 'selection',
        });
      }

      const unique: number[] = [];
      mapped.forEach((p) => {
        const v = Math.floor(p.zscore);
        if (!unique.includes(v)) unique.push(v);
      });

      const options = unique
        .filter((v) => v > 0)
        .sort((a, b) => a - b)
        .map((v) => v + 0.0);

      setThresholdOptions(options);
    } catch (err) {
      console.error(err);
      setPoints([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [freq, coin]);

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

  // 날짜 범위로 필터링 (dateRange가 없으면 전체 표시)
  const dateFilteredPoints = useMemo(() => {
    if (!dateRange) return points;
    return points.filter((p) => {
      const pointDate = new Date(p.time);
      return pointDate >= dateRange.startDate && pointDate <= dateRange.endDate;
    });
  }, [points, dateRange]);

  const filteredPoints = useMemo(
    () => dateFilteredPoints.filter((p) => p.zscore >= threshold),
    [dateFilteredPoints, threshold]
  );

  // 2) 상세 리스트는 filteredPoints를 최신순으로 정렬한 것 (그래프 클릭 시 필터 적용)
  const details = useMemo(() => {
    console.log('Filtering details with selectedChartDate:', selectedChartDate);
    const filtered = filteredPoints.filter((p) => {
      if (!selectedChartDate) return true;
      return p.dateLabel === selectedChartDate;
    });
    console.log('Filtered details count:', filtered.length);
    return filtered.sort(
      (a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()
    );
  }, [filteredPoints, selectedChartDate]);

  // 3) 페이지네이션 (상위 5개만)
  const visibleRows = useMemo(
    () => details.slice(0, visibleCount),
    [details, visibleCount]
  );

  const canLoadMore = visibleCount < details.length;

  // 그래프 클릭 핸들러 - activeLabel 사용
  const handleChartClick = (data: any) => {
    console.log('Chart clicked:', data);
    if (data && data.activeLabel) {
      const clickedLabel = data.activeLabel;
      console.log('Clicked label:', clickedLabel);
      if (selectedChartDate === clickedLabel) {
        // 같은 날짜 다시 클릭하면 필터 해제
        setSelectedChartDate(null);
      } else {
        setSelectedChartDate(clickedLabel);
        setVisibleCount(5);
      }
    }
  };

  // 날짜 필터 직접 설정 함수
  const setDateFilter = (dateLabel: string | null) => {
    console.log('Setting date filter to:', dateLabel);
    setSelectedChartDate(dateLabel);
    if (dateLabel) {
      setVisibleCount(5);
    }
  };

  // 커스텀 Tooltip 컴포넌트
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const handleTooltipClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        console.log(
          'Tooltip clicked, label:',
          label,
          'current selectedChartDate:',
          selectedChartDate
        );
        if (selectedChartDate === label) {
          console.log('Clearing filter');
          setDateFilter(null);
        } else {
          console.log('Setting filter to:', label);
          setDateFilter(label);
        }
      };

      return (
        <div
          className="bg-slate-900 border border-slate-600 rounded-xl p-3 shadow-xl cursor-pointer hover:border-cyan-400 transition-colors"
          onClick={handleTooltipClick}
        >
          <p className="text-cyan-400 font-semibold mb-2">📅 {label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(2)}
            </p>
          ))}
          <p className="text-xs text-slate-400 mt-2 border-t border-slate-700 pt-2">
            {selectedChartDate === label
              ? '👆 클릭하여 필터 해제'
              : '👆 클릭하여 이 날짜만 보기'}
          </p>
        </div>
      );
    }
    return null;
  };

  // 날짜 포맷
  const formatDateRange = () => {
    if (!dateRange) return '전체 기간';
    const start = dateRange.startDate.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
    const end = dateRange.endDate.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
    return `${start} ~ ${end}`;
  };

  // DateRange 컴포넌트용 ranges (null 처리)
  const calendarRanges = dateRange
    ? [dateRange]
    : [
        {
          startDate: new Date(),
          endDate: new Date(),
          key: 'selection',
        },
      ];

  return (
    <div className="mt-8 px-6 py-5 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950">
      {/* 제목 */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          커뮤니티 스파이크 분석
          <span
            className="text-xs px-1.5 py-0.5 rounded-full border border-slate-600 text-slate-300 cursor-help"
            title="Z-score ≥ 2 이상이면 급격한 감성 변화로 스파이크로 간주됩니다."
          >
            !
          </span>
        </h2>
        <span className="text-sm text-slate-400">
          {coin} · {freq}
        </span>
      </div>

      {/* 필터 */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        {/* 기간 달력 필터 */}
        <div className="relative" ref={calendarRef}>
          <button
            onClick={() => setShowCalendar(!showCalendar)}
            className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-900/40 border border-slate-700 text-slate-100 text-sm hover:bg-slate-800 transition-colors"
          >
            📅 {formatDateRange()}
          </button>

          {showCalendar && (
            <div className="absolute top-full left-0 mt-2 z-50 rounded-xl overflow-hidden shadow-2xl border border-slate-700">
              <style jsx global>{`
                .spike-calendar .rdrCalendarWrapper,
                .spike-calendar .rdrDateDisplayWrapper,
                .spike-calendar .rdrMonthAndYearWrapper {
                  background: #0f172a !important;
                }
                .spike-calendar .rdrMonthAndYearPickers select {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                  border: 1px solid #334155 !important;
                }
                .spike-calendar .rdrMonthAndYearPickers select option {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                }
                .spike-calendar .rdrNextPrevButton {
                  background: #1e293b !important;
                }
                .spike-calendar .rdrNextPrevButton:hover {
                  background: #334155 !important;
                }
                .spike-calendar .rdrNextPrevButton i {
                  border-color: transparent transparent transparent #94a3b8 !important;
                }
                .spike-calendar .rdrPprevButton i {
                  border-color: transparent #94a3b8 transparent transparent !important;
                }
                .spike-calendar .rdrMonth {
                  background: #0f172a !important;
                }
                .spike-calendar .rdrWeekDay {
                  color: #64748b !important;
                }
                .spike-calendar .rdrDay {
                  color: #e2e8f0 !important;
                }
                .spike-calendar .rdrDayNumber span {
                  color: #e2e8f0 !important;
                }
                .spike-calendar .rdrDayPassive .rdrDayNumber span {
                  color: #475569 !important;
                }
                .spike-calendar .rdrDayToday .rdrDayNumber span:after {
                  background: #8b5cf6 !important;
                }
                .spike-calendar .rdrDayDisabled {
                  background-color: #1e293b !important;
                }
                .spike-calendar .rdrDayDisabled .rdrDayNumber span {
                  color: #475569 !important;
                }
                .spike-calendar .rdrDateDisplayItem {
                  background: #1e293b !important;
                  border-color: #334155 !important;
                }
                .spike-calendar .rdrDateDisplayItem input {
                  color: #e2e8f0 !important;
                }
                .spike-calendar .rdrDateDisplayItemActive {
                  border-color: #8b5cf6 !important;
                }
                .spike-calendar .rdrInRange,
                .spike-calendar .rdrStartEdge,
                .spike-calendar .rdrEndEdge {
                  background: #8b5cf6 !important;
                }
                .spike-calendar .rdrDayStartPreview,
                .spike-calendar .rdrDayInPreview,
                .spike-calendar .rdrDayEndPreview {
                  border-color: #8b5cf6 !important;
                }
              `}</style>
              <div className="spike-calendar">
                <DateRange
                  ranges={calendarRanges}
                  onChange={(item: any) => {
                    setDateRange(item.selection);
                    setSelectedChartDate(null);
                  }}
                  months={1}
                  direction="horizontal"
                  rangeColors={['#8b5cf6']}
                />
              </div>
              <div className="bg-slate-900 p-2 flex justify-end gap-2 border-t border-slate-700">
                <button
                  onClick={() => {
                    // 전체 데이터 범위로 리셋
                    if (points.length > 0) {
                      setDateRange({
                        startDate: new Date(points[0].time),
                        endDate: new Date(points[points.length - 1].time),
                        key: 'selection',
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  전체
                </button>
                <button
                  onClick={() => {
                    if (points.length > 0) {
                      const lastDate = new Date(points[points.length - 1].time);
                      const startDate = new Date(lastDate);
                      startDate.setDate(startDate.getDate() - 7);
                      setDateRange({
                        startDate,
                        endDate: lastDate,
                        key: 'selection',
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  7일
                </button>
                <button
                  onClick={() => {
                    if (points.length > 0) {
                      const lastDate = new Date(points[points.length - 1].time);
                      const startDate = new Date(lastDate);
                      startDate.setDate(startDate.getDate() - 30);
                      setDateRange({
                        startDate,
                        endDate: lastDate,
                        key: 'selection',
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  30일
                </button>
                <button
                  onClick={() => {
                    if (points.length > 0) {
                      const lastDate = new Date(points[points.length - 1].time);
                      const startDate = new Date(lastDate);
                      startDate.setDate(startDate.getDate() - 90);
                      setDateRange({
                        startDate,
                        endDate: lastDate,
                        key: 'selection',
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  90일
                </button>
                <button
                  onClick={() => {
                    // 초기화: 데이터 기준 최근 180일
                    if (points.length > 0) {
                      const lastDate = new Date(points[points.length - 1].time);
                      const startDate = new Date(lastDate);
                      startDate.setDate(startDate.getDate() - 180);
                      setDateRange({
                        startDate,
                        endDate: lastDate,
                        key: 'selection',
                      });
                    }
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  180일(초기화)
                </button>
                <button
                  onClick={() => setShowCalendar(false)}
                  className="px-2 py-1 text-xs rounded bg-violet-600 text-white hover:bg-violet-500"
                >
                  확인
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-300">
          주기
          <select
            className="px-3 py-1 rounded bg-slate-900/40 border border-slate-700 text-slate-100"
            value={freq}
            onChange={(e) => setFreq(e.target.value as any)}
          >
            <option value="1h">1시간</option>
            <option value="4h">4시간</option>
            <option value="1d">1일</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-300">
          코인
          <select
            className="px-3 py-1 rounded bg-slate-900/40 border border-slate-700 text-slate-100"
            value={coin}
            onChange={(e) => setCoin(e.target.value as any)}
          >
            <option value="BTC">BTC</option>
            <option value="ETH">ETH</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-300">
          Spike
          <select
            className="px-3 py-1 rounded bg-slate-900/40 border border-slate-700 text-slate-100"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
          >
            {thresholdOptions.map((t) => (
              <option key={t} value={t}>
                ≥ {t.toFixed(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 차트 */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4">
        <p className="text-sm text-slate-400 mb-2">
          💡 그래프를 클릭하면 해당 시점의 스파이크만 아래 표에 표시됩니다
          {selectedChartDate && (
            <button
              onClick={() => setSelectedChartDate(null)}
              className="ml-3 text-blue-400 hover:text-blue-300"
            >
              [필터 해제: {selectedChartDate}]
            </button>
          )}
        </p>
        <div className="w-full h-[340px]">
          {loading ? (
            <div className="text-center text-slate-400 pt-20">로딩 중...</div>
          ) : filteredPoints.length === 0 ? (
            <div className="text-center text-slate-500 pt-20">
              스파이크 데이터가 없습니다.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={filteredPoints}
                onClick={handleChartClick}
                style={{ cursor: 'pointer' }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />

                <XAxis
                  dataKey="dateLabel"
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  minTickGap={20}
                />

                <YAxis yAxisId="left" stroke="#8b5cf6" />
                <YAxis yAxisId="right" stroke="#f97316" orientation="right" />

                <Tooltip
                  content={<CustomTooltip />}
                  wrapperStyle={{ pointerEvents: 'auto' }}
                />

                <Legend wrapperStyle={{ color: '#CBD5E1' }} />

                {/* 선택된 날짜 표시 */}
                {selectedChartDate && (
                  <ReferenceLine
                    x={selectedChartDate}
                    stroke="#22d3ee"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    label={{
                      value: '선택됨',
                      fill: '#22d3ee',
                      fontSize: 11,
                      position: 'top',
                    }}
                  />
                )}

                <Line
                  yAxisId="left"
                  dataKey="zscore"
                  name="Z-score"
                  type="monotone"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 6,
                    stroke: '#8B5CF6',
                    strokeWidth: 2,
                    fill: '#fff',
                  }}
                />
                <Line
                  yAxisId="right"
                  dataKey="total_posts"
                  name="총 글 수"
                  type="monotone"
                  stroke="#F97316"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 6,
                    stroke: '#F97316',
                    strokeWidth: 2,
                    fill: '#fff',
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* 상세 */}
      <div className="mt-10 bg-slate-900/40 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-white">
            스파이크 상세
            <span className="text-sm font-normal text-slate-400 ml-2">
              {selectedChartDate
                ? `(${selectedChartDate} 필터링 중 - ${details.length}건)`
                : `(클릭하면 해당 날짜의 게시글을 필터링합니다 - 총 ${details.length}건)`}
            </span>
          </h3>
          {selectedChartDate && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-cyan-400 bg-cyan-400/10 px-3 py-1 rounded-full animate-pulse">
                📅 {selectedChartDate} 필터 적용 중
              </span>
              <button
                onClick={() => setDateFilter(null)}
                className="text-sm text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-700 transition-colors"
              >
                ✕ 해제
              </button>
            </div>
          )}
        </div>

        {details.length === 0 ? (
          <div className="text-center text-slate-500 py-8">
            {selectedChartDate
              ? `${selectedChartDate}에 해당하는 스파이크가 없습니다.`
              : '스파이크 데이터가 없습니다.'}
          </div>
        ) : (
          visibleRows.map((p, idx) => (
            <div
              key={idx}
              className="py-4 border-b border-slate-700 last:border-none cursor-pointer hover:bg-slate-800/50 rounded-lg px-3 -mx-3 transition-colors"
              onClick={() => {
                const spikeDate = new Date(p.time);
                setSelectedSpikeDate(spikeDate);
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
              <div className="flex items-center gap-3 mb-2">
                <div className="px-2 py-1 rounded bg-indigo-700 text-slate-50 text-sm font-semibold">
                  Z {p.zscore.toFixed(2)}
                </div>

                <div className="text-slate-200 text-sm font-medium">
                  {p.dateLabel}
                </div>

                <span className="text-xs text-blue-400 ml-auto">
                  📋 게시글 보기
                </span>
              </div>

              <div className="text-slate-300 text-sm leading-relaxed pl-1">
                감성 diff:{' '}
                <span className="text-slate-50">{p.diff.toFixed(3)}</span> ·
                분산:{' '}
                <span className="text-slate-50">{p.variance.toFixed(3)}</span> ·
                총 글: <span className="text-slate-50">{p.total_posts}</span> ·
                긍정:{p.pos} · 부정:{p.neg} · 중립:{p.neu}
              </div>
            </div>
          ))
        )}

        {canLoadMore && (
          <button
            className="w-full mt-4 py-2 rounded-md bg-slate-800 text-slate-200 hover:bg-slate-700"
            onClick={() => setVisibleCount((v) => v + 5)}
          >
            더보기
          </button>
        )}
      </div>
    </div>
  );
}
