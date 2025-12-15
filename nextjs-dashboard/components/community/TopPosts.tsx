'use client';

import { useEffect, useMemo, useState, useRef } from 'react';
import { DateRange } from 'react-date-range';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import { useCommunity } from '../../contexts/CommunityContext';

function debounce(fn: Function, delay: number) {
  let timer: any;
  return (...args: any[]) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

export default function TopPosts() {
  const {
    selectedSpikeDate,
    setSelectedSpikeDate,
    selectedKeyword,
    setSelectedKeyword,
  } = useCommunity();

  const [sentiment, setSentiment] = useState<
    'all' | 'positive' | 'neutral' | 'negative'
  >('all');

  // 날짜 범위 필터 - 초기값은 null, 데이터 로드 후 설정
  const [dateRange, setDateRange] = useState<{
    startDate: Date;
    endDate: Date;
    key: string;
  } | null>(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const calendarRef = useRef<HTMLDivElement>(null);

  const [page, setPage] = useState(1);
  const [posts, setPosts] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  // API에서 반환된 실제 조회 기간
  const [dataFrom, setDataFrom] = useState<Date | null>(null);
  const [dataTo, setDataTo] = useState<Date | null>(null);

  // 전체 데이터 범위
  const [dataEarliest, setDataEarliest] = useState<Date | null>(null);
  const [dataLatest, setDataLatest] = useState<Date | null>(null);

  // 검색/정렬
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const updateSearch = useMemo(
    () => debounce((v: string) => setDebouncedSearch(v), 300),
    []
  );

  const [sort, setSort] = useState('score_desc');

  // 본문 더보기/접기
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  // 스파이크 날짜 선택 시 자동 필터
  useEffect(() => {
    if (selectedSpikeDate) {
      const startDate = new Date(selectedSpikeDate);
      startDate.setHours(0, 0, 0, 0);
      const endDate = new Date(selectedSpikeDate);
      endDate.setHours(23, 59, 59, 999);

      setDateRange({
        startDate,
        endDate,
        key: 'selection',
      });
      setPage(1);
    }
  }, [selectedSpikeDate]);

  // 워드클라우드 키워드 선택 시 검색어 설정
  useEffect(() => {
    if (selectedKeyword) {
      setSearch(selectedKeyword);
      setDebouncedSearch(selectedKeyword);
    }
  }, [selectedKeyword]);

  const load = async () => {
    setLoading(true);

    let url = `/api/community/top-posts?sentiment=${sentiment}&page=${page}`;

    // dateRange가 있으면 custom, 없으면 기본 30일
    if (dateRange) {
      url += `&range=custom&from=${dateRange.startDate.toISOString()}&to=${dateRange.endDate.toISOString()}`;
    } else {
      url += `&range=30d`;
    }

    const res = await fetch(url);
    const json = await res.json();

    let data = json.posts ?? [];

    // 내용 빈 글 제거
    data = data.filter(
      (p: any) => p.post_content && p.post_content.trim().length > 0
    );

    // 중복 제거
    const seen = new Set();
    data = data.filter((p: any) => {
      const key = `${p.post_content}_${p.post_date}_${p.engagement_score}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });

    setPosts(data);
    setTotal(json.total ?? 0);

    // API에서 반환된 실제 조회 기간 저장
    if (json.from) setDataFrom(new Date(json.from));
    if (json.to) setDataTo(new Date(json.to));
    if (json.dataEarliest) setDataEarliest(new Date(json.dataEarliest));
    if (json.dataLatest) setDataLatest(new Date(json.dataLatest));

    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [sentiment, page, dateRange]);

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

  // 검색/정렬 처리
  const filtered = useMemo(() => {
    let arr = [...posts];

    if (debouncedSearch.trim().length > 0) {
      const q = debouncedSearch.toLowerCase();
      arr = arr.filter(
        (p) =>
          p.post_content?.toLowerCase().includes(q) ||
          p.sentiment?.toLowerCase().includes(q)
      );
    }

    arr.sort((a, b) => {
      if (sort === 'latest')
        return (
          new Date(b.post_date).getTime() - new Date(a.post_date).getTime()
        );
      if (sort === 'oldest')
        return (
          new Date(a.post_date).getTime() - new Date(b.post_date).getTime()
        );
      if (sort === 'score_desc') return b.engagement_score - a.engagement_score;
      if (sort === 'score_asc') return a.engagement_score - b.engagement_score;
      return 0;
    });

    return arr;
  }, [posts, debouncedSearch, sort]);

  const visiblePosts = filtered.slice(0, 5);

  const tagColor = {
    positive: 'bg-green-600/60',
    neutral: 'bg-slate-600/60',
    negative: 'bg-red-600/60',
    all: 'bg-indigo-600/60',
  };

  return (
    <div
      data-section="top-posts"
      className="mt-8 px-6 py-6 rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 text-gray-200"
    >
      {/* 제목 */}
      <h2 className="text-2xl font-bold mb-6">커뮤니티 인기 게시글</h2>

      {/* 점수 로직 설명 */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 mb-6">
        <h3 className="text-lg font-semibold mb-2">📌 점수 계산 로직</h3>
        <p className="text-slate-400 text-sm leading-relaxed">
          🔥 좋아요 × 1 <br />
          💬 댓글 × 3 <br />
          🔁 공유 × 2 <br />
          <br />
          최종 점수 = <b>(댓글×3) + (공유×2) + (좋아요×1)</b>
        </p>
      </div>

      {/* 필터 */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
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
            <span className="text-slate-400 ml-1">({total}건)</span>
          </button>

          {showCalendar && (
            <div className="absolute top-full left-0 mt-2 z-50 rounded-xl overflow-hidden shadow-2xl border border-slate-700">
              <style jsx global>{`
                .toppost-calendar .rdrCalendarWrapper,
                .toppost-calendar .rdrDateDisplayWrapper,
                .toppost-calendar .rdrMonthAndYearWrapper {
                  background: #0f172a !important;
                }
                .toppost-calendar .rdrMonthAndYearPickers select {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                  border: 1px solid #334155 !important;
                }
                .toppost-calendar .rdrMonthAndYearPickers select option {
                  background: #1e293b !important;
                  color: #e2e8f0 !important;
                }
                .toppost-calendar .rdrNextPrevButton {
                  background: #1e293b !important;
                }
                .toppost-calendar .rdrNextPrevButton:hover {
                  background: #334155 !important;
                }
                .toppost-calendar .rdrNextPrevButton i {
                  border-color: transparent transparent transparent #94a3b8 !important;
                }
                .toppost-calendar .rdrPprevButton i {
                  border-color: transparent #94a3b8 transparent transparent !important;
                }
                .toppost-calendar .rdrMonth {
                  background: #0f172a !important;
                }
                .toppost-calendar .rdrWeekDay {
                  color: #64748b !important;
                }
                .toppost-calendar .rdrDay {
                  color: #e2e8f0 !important;
                }
                .toppost-calendar .rdrDayNumber span {
                  color: #e2e8f0 !important;
                }
                .toppost-calendar .rdrDayPassive .rdrDayNumber span {
                  color: #475569 !important;
                }
                .toppost-calendar .rdrDayToday .rdrDayNumber span:after {
                  background: #3b82f6 !important;
                }
                .toppost-calendar .rdrDayDisabled {
                  background-color: #1e293b !important;
                }
                .toppost-calendar .rdrDayDisabled .rdrDayNumber span {
                  color: #475569 !important;
                }
                .toppost-calendar .rdrDateDisplayItem {
                  background: #1e293b !important;
                  border-color: #334155 !important;
                }
                .toppost-calendar .rdrDateDisplayItem input {
                  color: #e2e8f0 !important;
                }
                .toppost-calendar .rdrDateDisplayItemActive {
                  border-color: #3b82f6 !important;
                }
                .toppost-calendar .rdrInRange,
                .toppost-calendar .rdrStartEdge,
                .toppost-calendar .rdrEndEdge {
                  background: #3b82f6 !important;
                }
                .toppost-calendar .rdrDayStartPreview,
                .toppost-calendar .rdrDayInPreview,
                .toppost-calendar .rdrDayEndPreview {
                  border-color: #3b82f6 !important;
                }
              `}</style>
              <div className="toppost-calendar">
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
                    setSelectedSpikeDate(null);
                  }}
                  months={1}
                  direction="horizontal"
                  rangeColors={['#3b82f6']}
                />
              </div>
              <div className="bg-slate-900 p-2 flex justify-end gap-2 border-t border-slate-700">
                <button
                  onClick={() => {
                    // 데이터 기준 최근 7일
                    if (dataLatest) {
                      const startDate = new Date(dataLatest);
                      startDate.setDate(startDate.getDate() - 7);
                      setDateRange({
                        startDate,
                        endDate: dataLatest,
                        key: 'selection',
                      });
                    }
                    setSelectedSpikeDate(null);
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
                >
                  7일
                </button>
                <button
                  onClick={() => {
                    // 초기화: 데이터 기준 최근 30일
                    setDateRange(null);
                    setSelectedSpikeDate(null);
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
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
                    setSelectedSpikeDate(null);
                  }}
                  className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 hover:bg-slate-600"
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

        {/* 감성 */}
        <select
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white"
          value={sentiment}
          onChange={(e) => {
            setPage(1);
            setSentiment(e.target.value as any);
          }}
        >
          <option value="all">전체</option>
          <option value="positive">긍정</option>
          <option value="neutral">중립</option>
          <option value="negative">부정</option>
        </select>

        {/* 검색 */}
        <input
          type="text"
          placeholder="검색..."
          value={search}
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-sm w-52"
          onChange={(e) => {
            setSearch(e.target.value);
            updateSearch(e.target.value);
            setSelectedKeyword('');
          }}
        />

        {/* 정렬 */}
        <select
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="score_desc">점수 높은순</option>
          <option value="score_asc">점수 낮은순</option>
          <option value="latest">최신순</option>
          <option value="oldest">오래된순</option>
        </select>
      </div>

      {/* 리스트 */}
      <div className="flex flex-col gap-6">
        {loading ? (
          <div className="text-center py-10 text-slate-500">로딩 중...</div>
        ) : visiblePosts.length === 0 ? (
          <div className="text-center py-10 text-slate-500">
            게시글이 없습니다.
          </div>
        ) : (
          visiblePosts.map((post, i) => (
            <div
              key={i}
              className="bg-slate-900/40 border border-slate-800 rounded-xl p-6"
            >
              {/* 날짜 + 감성 */}
              <div className="flex justify-between items-center mb-3">
                <span className="text-slate-400 text-sm">
                  {new Date(post.post_date).toLocaleString('ko-KR')}
                </span>

                <span
                  className={`text-xs px-2 py-1 rounded text-white ${
                    tagColor[post.sentiment]
                  }`}
                >
                  {post.sentiment}
                </span>
              </div>

              {/* 내용 */}
              <pre
                className="whitespace-pre-wrap text-[15px] text-slate-200 leading-relaxed mb-4 cursor-pointer"
                onClick={() =>
                  setExpanded((prev) => ({ ...prev, [i]: !prev[i] }))
                }
              >
                {expanded[i]
                  ? post.post_content
                  : post.post_content.slice(0, 200) +
                    (post.post_content.length > 200 ? ' ...더보기' : '')}
              </pre>

              {/* 메트릭 */}
              <div className="flex gap-6 text-sm font-semibold text-slate-300">
                <div>🔥 {Number(post.likes).toLocaleString()}</div>
                <div>💬 {Number(post.comments).toLocaleString()}</div>
                <div>🔁 {Number(post.shares).toLocaleString()}</div>
                <div>
                  🏆 점수 {Number(post.engagement_score).toLocaleString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 페이징 */}
      {!loading && posts.length > 0 && (
        <div className="flex justify-center gap-4 mt-10 text-sm text-slate-300">
          <button
            className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-40"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            이전
          </button>

          <span>
            {page} / {Math.ceil(total / 5)}
          </span>

          <button
            className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-40"
            disabled={page * 5 >= total}
            onClick={() => setPage((p) => p + 1)}
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
