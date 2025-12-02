'use client';

import { useEffect, useMemo, useState } from 'react';
import { DateRangePicker } from 'react-date-range';
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

  const [range, setRange] = useState<'7d' | '30d' | 'custom'>('30d');
  const [showCalendar, setShowCalendar] = useState(false);
  const [customRange, setCustomRange] = useState([
    {
      startDate: new Date(Date.now() - 30 * 86400000),
      endDate: new Date(),
      key: 'selection',
    },
  ]);

  const [page, setPage] = useState(1);
  const [posts, setPosts] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

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

      setRange('custom');
      setCustomRange([
        {
          startDate,
          endDate,
          key: 'selection',
        },
      ]);
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

    let url = `/api/community/top-posts?sentiment=${sentiment}&page=${page}&range=${range}`;

    if (range === 'custom') {
      url += `&from=${customRange[0].startDate.toISOString()}&to=${customRange[0].endDate.toISOString()}`;
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
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [sentiment, page, range, customRange]);

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

        {/* 기간 */}
        <select
          value={range}
          onChange={(e) => {
            setRange(e.target.value as any);
            if (e.target.value === 'custom') {
              setShowCalendar(true);
            }
            // 스파이크 날짜 선택 초기화
            setSelectedSpikeDate(null);
          }}
          className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white"
        >
          <option value="7d">최근 7일</option>
          <option value="30d">최근 30일</option>
          <option value="custom">직접 선택</option>
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

      {/* 날짜 범위 선택 (다크 테마) */}
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
              onChange={(item) => setCustomRange([item.selection] as any)}
              ranges={customRange}
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
                onClick={() => {
                  setShowCalendar(false);
                  load();
                }}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors font-medium"
              >
                적용
              </button>
            </div>
          </div>
        </div>
      )}

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
