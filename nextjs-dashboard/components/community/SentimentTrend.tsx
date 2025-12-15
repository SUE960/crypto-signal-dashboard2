'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
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

// API 타입
type SentimentRow = {
  post_date: string;
  avg_sentiment: string;
  variance: string;
  total_posts: string;
  pos: string;
  neg: string;
  neu: string;
};

type PriceRow = {
  timestamp: string;
  close_price: string; // ✅ 실제 API 필드명
};

type Point = {
  time: string;
  avg_sentiment: number;
  variance: number;
  price: number | null;
  total_posts: number;
  pos: number;
  neg: number;
  neu: number;
  correlation?: number;
};

// MAX_POINTS 제한 제거 - 전체 데이터 사용

// =============================
// Rolling correlation 계산
// =============================
function computeCorrelation(arrX: number[], arrY: number[]): number {
  const n = arrX.length;
  if (n === 0) return 0;

  const meanX = arrX.reduce((a, b) => a + b, 0) / n;
  const meanY = arrY.reduce((a, b) => a + b, 0) / n;

  let num = 0,
    denX = 0,
    denY = 0;

  for (let i = 0; i < n; i++) {
    const dx = arrX[i] - meanX;
    const dy = arrY[i] - meanY;
    num += dx * dy;
    denX += dx * dx;
    denY += dy * dy;
  }

  return denX * denY === 0 ? 0 : num / Math.sqrt(denX * denY);
}

// =============================
// 날짜 파싱 (API 형식 대응)
// =============================
function robustDateParse(v: string): Date {
  if (!v) return new Date('1970-01-01T00:00:00Z');

  // 공백 기반 날짜 "2024-11-15 13:00:00+00:00" / "2025-05-25 12:00:00+00"
  if (v.includes(' ') && !v.includes('T')) {
    let fixed = v.replace(' ', 'T');

    if (fixed.endsWith('+00')) {
      fixed = fixed + ':00'; // +00 -> +00:00
    }

    if (!fixed.endsWith('Z') && !fixed.includes('+')) {
      fixed = fixed + 'Z';
    }

    return new Date(fixed);
  }

  if (v.endsWith('+00')) {
    return new Date(v + ':00');
  }

  if (!v.endsWith('Z') && !v.includes('+')) {
    return new Date(v + 'Z');
  }

  return new Date(v);
}

// =============================
// timestamp 정규화 (sentiment/price 모두 동일 키로)
// =============================
function normalizeDate(v: string): string {
  const d = robustDateParse(v);

  // 모든 시계열을 UTC 단위 YYYY-MM-DDTHH:00:00Z 로 변환
  return (
    d.getUTCFullYear() +
    '-' +
    String(d.getUTCMonth() + 1).padStart(2, '0') +
    '-' +
    String(d.getUTCDate()).padStart(2, '0') +
    'T' +
    String(d.getUTCHours()).padStart(2, '0') +
    ':00:00Z'
  );
}

// =============================
// 날짜 포맷 (UTC 기준, X축/툴팁 공통 사용)
// =============================
function formatDisplayDate(iso: string): string {
  const d = new Date(iso);
  const month = d.getUTCMonth() + 1;
  const date = d.getUTCDate();
  const hour = d.getUTCHours();

  return `${month}/${date} ${String(hour).padStart(2, '0')}h`;
}

export default function SentimentTrend() {
  // 필터 상태
  const [freq, setFreq] = useState<'1h' | '4h' | '1d'>('4h');
  const [coin, setCoin] = useState<'BTC' | 'ETH'>('BTC');

  // 날짜 범위 필터
  const [dateRange, setDateRange] = useState<{
    startDate: Date;
    endDate: Date;
    key: string;
  } | null>(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const calendarRef = useRef<HTMLDivElement>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<
    '7d' | '30d' | '90d' | 'custom'
  >('30d');

  // 그래프 클릭으로 선택된 시점
  const [selectedPoint, setSelectedPoint] = useState<string | null>(null);

  const [points, setPoints] = useState<Point[]>([]);
  const [loading, setLoading] = useState(true);

  // Line Visibility
  const [showSent, setShowSent] = useState(true);
  const [showPrice, setShowPrice] = useState(true);
  const [showPosts, setShowPosts] = useState(false);
  const [showCorr, setShowCorr] = useState(false);

  // ========================
  // 데이터 불러오기
  // ========================
  useEffect(() => {
    async function load() {
      try {
        setLoading(true);

        const res = await fetch(
          `/api/community/timeseries?freq=${freq}&coin=${coin}`
        );
        const json = await res.json();

        const sentiment: SentimentRow[] = json.sentiment || [];
        const prices: PriceRow[] = json.price || [];

        // ✅ price timestamp map (정규화 + close_price 사용)
        const priceMap = new Map<string, number>();
        prices.forEach((p) => {
          const key = normalizeDate(p.timestamp);
          const v = Number(p.close_price);
          if (Number.isFinite(v)) {
            priceMap.set(key, v);
          }
        });

        const merged: Point[] = sentiment.map((s) => {
          const t = normalizeDate(s.post_date);

          return {
            time: t,
            avg_sentiment: Number(s.avg_sentiment) || 0,
            variance: Number(s.variance) || 0,
            price: priceMap.get(t) ? Math.round(priceMap.get(t)!) : null,
            total_posts: Number(s.total_posts) || 0,
            pos: Number(s.pos) || 0,
            neg: Number(s.neg) || 0,
            neu: Number(s.neu) || 0,
          };
        });

        // rolling correlation
        const windowSize = 30;
        for (let i = 0; i < merged.length; i++) {
          const slice = merged.slice(Math.max(0, i - windowSize), i + 1);
          merged[i].correlation = computeCorrelation(
            slice.map((v) => v.avg_sentiment),
            slice.map((v) => v.price ?? 0)
          );
        }

        setPoints(merged);

        // 데이터 범위에 맞게 dateRange 초기화 (첫 로드시만)
        // 기본값: 데이터의 최근 30일
        if (merged.length > 0 && !dateRange) {
          const lastDate = new Date(merged[merged.length - 1].time);
          const firstDate = new Date(merged[0].time);

          // 30일 전 날짜 계산
          const thirtyDaysAgo = new Date(lastDate);
          thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

          // 데이터 시작일과 30일 전 중 더 늦은 날짜를 시작일로 사용
          const startDate =
            thirtyDaysAgo > firstDate ? thirtyDaysAgo : firstDate;

          setDateRange({
            startDate: startDate,
            endDate: lastDate,
            key: 'selection',
          });
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

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

  // 날짜 범위로 필터링
  const filteredPoints = useMemo(() => {
    if (!dateRange) return points;
    return points.filter((p) => {
      const pointDate = new Date(p.time);
      return pointDate >= dateRange.startDate && pointDate <= dateRange.endDate;
    });
  }, [points, dateRange]);

  // ========================
  // 상단 Metric 카드 계산 (선택된 포인트가 있으면 해당 시점, 없으면 전체 기간)
  // ========================
  const metrics = useMemo(() => {
    if (filteredPoints.length === 0) return null;

    // 선택된 포인트가 있으면 해당 시점 데이터만 사용
    if (selectedPoint) {
      const point = filteredPoints.find(
        (p) => formatDisplayDate(p.time) === selectedPoint
      );
      if (point) {
        const total = point.pos + point.neg + point.neu;
        return {
          avgSent: point.avg_sentiment,
          avgVar: point.variance,
          totalPosts: point.total_posts,
          posRate: total ? point.pos / total : 0,
          negRate: total ? point.neg / total : 0,
          neuRate: total ? point.neu / total : 0,
          globalCorr: point.correlation ?? 0,
          price: point.price,
          isPointData: true,
        };
      }
    }

    // 전체 기간 평균
    const avgSent =
      filteredPoints.reduce((a, b) => a + b.avg_sentiment, 0) /
      filteredPoints.length;

    const avgVar =
      filteredPoints.reduce((a, b) => a + b.variance, 0) /
      filteredPoints.length;

    const totalPosts = filteredPoints.reduce((a, b) => a + b.total_posts, 0);
    const totalPos = filteredPoints.reduce((a, b) => a + b.pos, 0);
    const totalNeg = filteredPoints.reduce((a, b) => a + b.neg, 0);
    const totalNeu = filteredPoints.reduce((a, b) => a + b.neu, 0);

    const globalCorr = computeCorrelation(
      filteredPoints.map((p) => p.avg_sentiment),
      filteredPoints.map((p) => p.price ?? 0)
    );

    return {
      avgSent,
      avgVar,
      totalPosts,
      posRate: totalPosts ? totalPos / totalPosts : 0,
      negRate: totalPosts ? totalNeg / totalPosts : 0,
      neuRate: totalPosts ? totalNeu / totalPosts : 0,
      globalCorr,
      price: null as number | null,
      isPointData: false,
    };
  }, [filteredPoints, selectedPoint]);

  // 날짜 범위 포맷
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

  // DateRange 컴포넌트용 ranges
  const calendarRanges = dateRange
    ? [dateRange]
    : [
        {
          startDate: new Date(),
          endDate: new Date(),
          key: 'selection',
        },
      ];

  // 그래프 클릭 핸들러
  const handleChartClick = (data: any) => {
    if (data && data.activeLabel) {
      const clickedLabel = formatDisplayDate(data.activeLabel);
      if (selectedPoint === clickedLabel) {
        setSelectedPoint(null);
      } else {
        setSelectedPoint(clickedLabel);
      }
    }
  };

  // 커스텀 Tooltip 컴포넌트
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const displayLabel = formatDisplayDate(label);
      const handleTooltipClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (selectedPoint === displayLabel) {
          setSelectedPoint(null);
        } else {
          setSelectedPoint(displayLabel);
        }
      };

      return (
        <div
          className="bg-slate-900 border border-slate-600 rounded-xl p-3 shadow-xl cursor-pointer hover:border-cyan-400 transition-colors"
          onClick={handleTooltipClick}
        >
          <p className="text-cyan-400 font-semibold mb-2">📅 {displayLabel}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}:{' '}
              {entry.name.includes('가격')
                ? `$${Math.round(Number(entry.value)).toLocaleString()}`
                : typeof entry.value === 'number'
                ? entry.value.toFixed(3)
                : entry.value}
            </p>
          ))}
          <p className="text-xs text-slate-400 mt-2 border-t border-slate-700 pt-2">
            {selectedPoint === displayLabel
              ? '👆 클릭하여 필터 해제'
              : '👆 클릭하여 이 시점만 보기'}
          </p>
        </div>
      );
    }
    return null;
  };

  // ========================
  // 렌더링
  // ========================
  if (loading)
    return (
      <div className="h-64 flex items-center justify-center text-slate-400">
        데이터 로딩 중...
      </div>
    );

  if (points.length === 0 || !metrics)
    return (
      <div className="h-64 flex items-center justify-center text-slate-500">
        표시할 데이터 없음
      </div>
    );

  return (
    <div className="px-6 py-5 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950">
      {/* 제목 */}
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">커뮤니티 감성 트렌드</h2>
        <span className="text-sm text-slate-400">
          {coin} · {freq === '1h' ? '1시간' : freq === '4h' ? '4시간' : '1일'}
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
                .sentiment-calendar .rdrCalendarWrapper,
                .sentiment-calendar .rdrDateDisplayWrapper,
                .sentiment-calendar .rdrMonthAndYearWrapper {
                  background: #0f172a !important;
                }
                .sentiment-calendar .rdrMonthAndYearPickers select {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                  border: 1px solid #334155 !important;
                }
                .sentiment-calendar .rdrNextPrevButton {
                  background: #1e293b !important;
                }
                .sentiment-calendar .rdrNextPrevButton:hover {
                  background: #334155 !important;
                }
                .sentiment-calendar .rdrMonth {
                  background: #0f172a !important;
                }
                .sentiment-calendar .rdrWeekDay {
                  color: #64748b !important;
                }
                .sentiment-calendar .rdrDayNumber span {
                  color: #e2e8f0 !important;
                }
                .sentiment-calendar .rdrDayPassive .rdrDayNumber span {
                  color: #475569 !important;
                }
                .sentiment-calendar .rdrDayToday .rdrDayNumber span:after {
                  background: #8b5cf6 !important;
                }
                .sentiment-calendar .rdrDateDisplayItem {
                  background: #1e293b !important;
                  border-color: #334155 !important;
                }
                .sentiment-calendar .rdrDateDisplayItem input {
                  color: #e2e8f0 !important;
                }
                .sentiment-calendar .rdrDateDisplayItemActive {
                  border-color: #8b5cf6 !important;
                }
                .sentiment-calendar .rdrInRange,
                .sentiment-calendar .rdrStartEdge,
                .sentiment-calendar .rdrEndEdge {
                  background: #8b5cf6 !important;
                }
              `}</style>
              <div className="sentiment-calendar">
                <DateRange
                  ranges={calendarRanges}
                  onChange={(item: any) => {
                    setDateRange(item.selection);
                    setSelectedPoint(null);
                    setSelectedPeriod('custom');
                  }}
                  months={1}
                  direction="horizontal"
                  rangeColors={['#8b5cf6']}
                />
              </div>
              <div className="bg-slate-900 p-2 flex justify-end gap-2 border-t border-slate-700">
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
                    setSelectedPeriod('30d');
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedPeriod === '30d'
                      ? 'bg-violet-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  30일(초기화)
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
                    setSelectedPeriod('90d');
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedPeriod === '90d'
                      ? 'bg-violet-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  90일
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
            onChange={(e) => {
              setFreq(e.target.value as any);
              setDateRange(null);
              setSelectedPoint(null);
            }}
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
            onChange={(e) => {
              setCoin(e.target.value as any);
              setDateRange(null);
              setSelectedPoint(null);
            }}
          >
            <option value="BTC">BTC</option>
            <option value="ETH">ETH</option>
          </select>
        </div>
      </div>

      {/* 🔥 Metric Cards */}
      <div className="mb-2">
        {selectedPoint && (
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm text-cyan-400 bg-cyan-400/10 px-3 py-1 rounded-full animate-pulse">
              📅 {selectedPoint} 시점 데이터
            </span>
            <button
              onClick={() => setSelectedPoint(null)}
              className="text-sm text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-700 transition-colors"
            >
              ✕ 전체 보기
            </button>
          </div>
        )}
      </div>
      {/* 상단 행: 전체 글 수, 평균 감성, 상관계수 */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <MetricCard
          title={metrics.isPointData ? '글 수' : '전체 글 수'}
          value={metrics.totalPosts.toLocaleString()}
          highlight={metrics.isPointData}
        />
        <MetricCard
          title={metrics.isPointData ? '감성' : '평균 감성'}
          value={metrics.avgSent.toFixed(3)}
          tooltip="감성값은 -1~1 범위. 0은 중립, +는 긍정, -는 부정이며 절대값이 클수록 감정 강도가 큽니다."
          highlight={metrics.isPointData}
        />
        <MetricCard
          title={metrics.isPointData ? 'Rolling Corr' : '상관계수'}
          value={metrics.globalCorr.toFixed(3)}
          tooltip="상관계수는 -1~1. 0은 관계 없음, +는 같은 방향, -는 반대 방향. |0.5| 이상이면 의미 있는 상관으로 볼 수 있습니다."
          highlight={metrics.isPointData}
        />
      </div>
      {/* 하단 행: 감정 분산, 긍정 비율, 부정 비율 */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <MetricCard
          title={metrics.isPointData ? '분산' : '감정 분산'}
          value={metrics.avgVar.toFixed(3)}
          tooltip="분산은 감정이 얼마나 흩어져 있는지. 0~0.1 낮음, 0.1~0.3 보통, 0.3 이상이면 감정 스펙트럼이 넓은 상태입니다."
          highlight={metrics.isPointData}
        />
        <MetricCard
          title="긍정 비율"
          value={(metrics.posRate * 100).toFixed(1) + '%'}
          highlight={metrics.isPointData}
        />
        <MetricCard
          title="부정 비율"
          value={(metrics.negRate * 100).toFixed(1) + '%'}
          highlight={metrics.isPointData}
        />
      </div>

      {/* 🔥 Toggle Buttons */}
      <div className="mb-4 flex flex-wrap gap-2">
        <ToggleButton
          label="감성지수"
          active={showSent}
          onClick={() => setShowSent(!showSent)}
        />
        <ToggleButton
          label="가격"
          active={showPrice}
          onClick={() => setShowPrice(!showPrice)}
        />
        <ToggleButton
          label="글 수"
          active={showPosts}
          onClick={() => setShowPosts(!showPosts)}
        />
        <ToggleButton
          label="corr"
          active={showCorr}
          onClick={() => setShowCorr(!showCorr)}
        />
      </div>

      {/* 차트 안내 */}
      <p className="text-sm text-slate-400 mb-2">
        💡 그래프를 클릭하면 해당 시점의 데이터만 위 카드에 표시됩니다
      </p>

      {/* 🔥 Chart */}
      <div style={{ width: '100%', height: 420 }}>
        <ResponsiveContainer>
          <LineChart
            data={filteredPoints}
            margin={{ top: 20, right: 60, bottom: 20, left: 20 }}
            onClick={handleChartClick}
            style={{ cursor: 'pointer' }}
          >
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />

            <XAxis
              dataKey="time"
              stroke="#64748b"
              tickFormatter={formatDisplayDate}
              minTickGap={20}
            />

            <YAxis yAxisId="left" stroke="#8b5cf6" />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#f97316"
              tickFormatter={(v) => `$${Number(v).toLocaleString()}`}
            />

            <Tooltip
              content={<CustomTooltip />}
              wrapperStyle={{ pointerEvents: 'auto' }}
            />

            <Legend />

            {/* 선택된 시점 표시 */}
            {selectedPoint &&
              filteredPoints.find(
                (p) => formatDisplayDate(p.time) === selectedPoint
              ) && (
                <ReferenceLine
                  x={
                    filteredPoints.find(
                      (p) => formatDisplayDate(p.time) === selectedPoint
                    )?.time
                  }
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

            {showPrice && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="price"
                name={`${coin} 가격`}
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                activeDot={{
                  r: 6,
                  stroke: '#f97316',
                  strokeWidth: 2,
                  fill: '#fff',
                }}
              />
            )}

            {showSent && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="avg_sentiment"
                name="평균 감성지수"
                stroke="#818cf8"
                strokeWidth={2}
                dot={false}
                activeDot={{
                  r: 6,
                  stroke: '#818cf8',
                  strokeWidth: 2,
                  fill: '#fff',
                }}
              />
            )}

            {showPosts && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="total_posts"
                name="글 수"
                stroke="#22d3ee"
                strokeWidth={1.5}
                dot={false}
                activeDot={{
                  r: 6,
                  stroke: '#22d3ee',
                  strokeWidth: 2,
                  fill: '#fff',
                }}
              />
            )}

            {showCorr && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="correlation"
                name="Rolling Corr"
                stroke="#34d399"
                strokeWidth={1.5}
                dot={false}
                activeDot={{
                  r: 6,
                  stroke: '#34d399',
                  strokeWidth: 2,
                  fill: '#fff',
                }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// =============================
// Metric Card Component (+ tooltip + highlight)
// =============================
function MetricCard({
  title,
  value,
  tooltip,
  highlight,
}: {
  title: string;
  value: string;
  tooltip?: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`relative p-4 rounded-xl border ${
        highlight
          ? 'border-cyan-500 bg-cyan-500/10'
          : 'border-slate-800 bg-slate-900/40'
      } transition-colors`}
    >
      <div className="flex items-center gap-1 text-xs text-slate-400">
        {title}
        {tooltip && (
          <span className="relative group cursor-help">
            <span className="text-slate-500 text-[10px] font-bold">!</span>
            <div className="absolute z-10 hidden w-56 rounded-md border border-slate-700 bg-slate-800 p-2 text-[11px] text-slate-200 shadow-xl group-hover:block top-4 left-0">
              {tooltip}
            </div>
          </span>
        )}
      </div>
      <div
        className={`mt-1 text-lg font-semibold ${
          highlight ? 'text-cyan-400' : 'text-white'
        }`}
      >
        {value}
      </div>
    </div>
  );
}

// =============================
// Toggle Button Component
// =============================
function ToggleButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded-md text-sm font-medium border ${
        active
          ? 'bg-blue-500/20 border-blue-400 text-blue-300'
          : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
      }`}
    >
      {label}
    </button>
  );
}
