'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ComposedChart,
  Bar,
  ReferenceLine,
  Cell
} from 'recharts';

interface RealTimeChartProps {
  dataPath?: string; // CSV 파일 경로
}

interface ChartDataPoint {
  timestamp: string;
  date: string;
  whale_tx_count: number;
  whale_volume_sum: number;
  btc_close: number;
  eth_close: number;
  btc_change: number;
  eth_change: number;
  btc_volatility?: number;
  eth_volatility?: number;
}

interface SpikePoint {
  timestamp: string;
  date: string;
  priorityScore: number;
  alertLevel: string;
  reasons: string[];
  details: any;
}

const RealTimeChart: React.FC<RealTimeChartProps> = ({ dataPath }) => {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [spikePoints, setSpikePoints] = useState<SpikePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');
  const [chartType, setChartType] = useState<'line' | 'area' | 'composed'>('composed');
  const [selectedCoin, setSelectedCoin] = useState<'btc' | 'eth' | 'both'>('both');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState<number>(0);
  const [viewStartIndex, setViewStartIndex] = useState<number>(0);

  useEffect(() => {
    const loadData = async () => {
      await loadRealData();
      await loadSpikePoints();
      setViewStartIndex(0); // 범위 변경 시 리셋
      setSelectedDate(''); // 날짜 선택도 리셋하여 최신 데이터 표시
    };
    loadData();
  }, [timeRange]);

  const loadSpikePoints = async () => {
    try {
      const response = await fetch(`/api/spike-points?range=${timeRange}`);
      if (response.ok) {
        const spikes = await response.json();
        setSpikePoints(spikes);
      }
    } catch (error) {
      console.error('Spike points 로딩 실패:', error);
    }
  };

  const loadRealData = async () => {
    setLoading(true);
    try {
      // API에서 실제 데이터 로드
      const response = await fetch(`/api/timeseries?range=${timeRange}`);
      
      if (!response.ok) {
        throw new Error(`데이터 로딩 실패: ${response.status} ${response.statusText}`);
      }
      
      const jsonData = await response.json();
      console.log('API에서 받은 데이터:', {
        개수: Array.isArray(jsonData) ? jsonData.length : 0,
        첫번째데이터: Array.isArray(jsonData) && jsonData.length > 0 ? jsonData[0] : null,
        마지막데이터: Array.isArray(jsonData) && jsonData.length > 0 ? jsonData[jsonData.length - 1] : null
      });
      
      if (Array.isArray(jsonData) && jsonData.length > 0) {
        // 실제 데이터 사용
        setData(jsonData);
        console.log('✅ 실제 데이터 로드 완료:', jsonData.length, '개');
      } else {
        console.error('❌ API에서 빈 데이터를 받았습니다.');
        setData([]); // 빈 배열로 설정 (더미 데이터 사용 안 함)
      }
    } catch (error) {
      console.error('❌ 데이터 로딩 중 오류:', error);
      setData([]); // 에러 시에도 빈 배열로 설정 (더미 데이터 사용 안 함)
    } finally {
      setLoading(false);
    }
  };

  // 선택된 날짜 또는 드래그 위치에 따라 데이터 필터링
  const getFilteredData = () => {
    if (data.length === 0) return [];
    
    // API에서 이미 최신 데이터부터 정렬되어 오므로, 그대로 사용
    // 필요시 시간순으로 재정렬 (오름차순)
    const sortedData = [...data].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    // 날짜가 선택된 경우
    if (selectedDate) {
      const selectedTimestamp = new Date(selectedDate).getTime();
      const selectedIndex = sortedData.findIndex(
        (d) => new Date(d.timestamp).getTime() >= selectedTimestamp
      );
      if (selectedIndex >= 0) {
        return sortedData.slice(selectedIndex);
      }
    }
    
    // 드래그로 이동한 경우
    if (viewStartIndex > 0) {
      return sortedData.slice(viewStartIndex);
    }
    
    // 기본값: 가장 최신 데이터부터 표시 (7일 범위)
    // 최신 날짜 기준으로 7일 전까지의 데이터만 표시
    if (sortedData.length > 0) {
      const latestDate = new Date(sortedData[sortedData.length - 1].timestamp);
      const sevenDaysAgo = new Date(latestDate);
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      sevenDaysAgo.setHours(0, 0, 0, 0);
      
      const sevenDaysAgoTime = sevenDaysAgo.getTime();
      const startIndex = sortedData.findIndex(
        (d) => new Date(d.timestamp).getTime() >= sevenDaysAgoTime
      );
      
      // 7일 범위를 찾은 경우
      if (startIndex >= 0 && startIndex < sortedData.length) {
        return sortedData.slice(startIndex);
      }
      
      // 7일 범위를 찾지 못한 경우, 최신 데이터부터 최대 200개 표시
      // 또는 데이터가 적으면 전체 표시
      return sortedData.slice(-Math.min(200, sortedData.length));
    }
    
    // 정렬 실패한 경우, 원본 데이터 반환
    return data;
  };

  const filteredData = getFilteredData();
  
  // 디버깅: 데이터 상태 확인
  useEffect(() => {
    console.log('차트 데이터 상태:', {
      원본데이터개수: data.length,
      필터링된데이터개수: filteredData.length,
      timeRange,
      selectedDate,
      viewStartIndex,
      첫번째데이터: filteredData.length > 0 ? filteredData[0] : null,
      마지막데이터: filteredData.length > 0 ? filteredData[filteredData.length - 1] : null
    });
  }, [data.length, filteredData.length, timeRange, selectedDate, viewStartIndex]);

  // 필터링된 데이터가 없으면 원본 데이터 사용 (더미 데이터 사용 안 함)
  let displayData = filteredData.length > 0 ? filteredData : data;

  // 데이터와 Spike 포인트 매칭
  const dataWithSpikes = displayData.map((point) => {
    const spike = spikePoints.find(
      (sp) => new Date(sp.timestamp).getTime() === new Date(point.timestamp).getTime()
    );
    return {
      ...point,
      isSpike: !!spike,
      spikeInfo: spike || null,
    };
  });

  // 차트 드래그 핸들러
  const handleChartMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStartX(e.clientX);
  };

  const handleChartMouseMove = (e: React.MouseEvent) => {
    if (isDragging && data.length > 0) {
      const deltaX = e.clientX - dragStartX;
      const pixelsPerDataPoint = 800 / data.length; // 대략적인 픽셀당 데이터 포인트
      const deltaIndex = Math.round(deltaX / pixelsPerDataPoint);
      const newStartIndex = Math.max(0, Math.min(data.length - 1, viewStartIndex - deltaIndex));
      setViewStartIndex(newStartIndex);
      setDragStartX(e.clientX);
    }
  };

  const handleChartMouseUp = () => {
    setIsDragging(false);
  };

  // 날짜 선택 핸들러
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
    setViewStartIndex(0); // 날짜 선택 시 드래그 위치 리셋
  };

  const generateDummyData = (range: string): ChartDataPoint[] => {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const dataPoints: ChartDataPoint[] = [];
    const now = new Date();

    // 시간별 데이터 생성 (더 많은 데이터 포인트)
    const hours = days * 24;
    for (let i = hours; i >= 0; i -= 1) { // 시간별 데이터
      const date = new Date(now);
      date.setHours(date.getHours() - i);

      const baseWhale = 30 + Math.random() * 80;
      const baseBtc = 105000 + Math.sin(i / 50) * 15000;
      const baseEth = 3800 + Math.sin(i / 50) * 800;

      dataPoints.push({
        timestamp: date.toISOString(),
        date: date.toLocaleDateString('ko-KR', { 
          month: 'numeric', 
          day: 'numeric',
          hour: '2-digit'
        }),
        whale_tx_count: Math.round(baseWhale + Math.random() * 40),
        whale_volume_sum: Math.round((baseWhale + Math.random() * 50) * 150),
        btc_close: Math.round(baseBtc + Math.random() * 3000),
        eth_close: Math.round(baseEth + Math.random() * 200),
        btc_change: (Math.random() - 0.5) * 5,
        eth_change: (Math.random() - 0.5) * 7,
        btc_volatility: Math.random() * 2000 + 500,
        eth_volatility: Math.random() * 100 + 20,
      });
    }

    return dataPoints;
  };

  const CustomTooltip = ({ active, payload, label, spikePoints }: any) => {
    if (!active || !payload || !payload.length) return null;

    // 고래 거래 중복 제거 (Area와 Bar가 모두 있을 경우 하나만 표시)
    const seenNames = new Set<string>();
    const uniquePayload = payload.filter((entry: any) => {
      if (entry.name === '고래 거래') {
        if (seenNames.has('고래 거래')) {
          return false; // 이미 표시된 고래 거래는 제외
        }
        seenNames.add('고래 거래');
      }
      return true;
    });

    // 해당 시점의 Spike 정보 찾기
    const spike = spikePoints?.find((sp: any) => sp.date === label);

    return (
      <div className="bg-gray-950 border-2 border-gray-700 rounded-xl p-4 shadow-2xl backdrop-blur-sm max-w-md">
        <p className="text-gray-300 font-semibold mb-3 text-sm border-b border-gray-700 pb-2">
          📅 {label}
        </p>
        
        {/* Spike 알람 표시 */}
        {spike && (
          <div className="mb-4 p-3 bg-gradient-to-r from-yellow-900/40 to-orange-900/40 border border-yellow-500/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">⭐</span>
              <span className="text-yellow-400 font-bold text-sm">SPIKE! 구매 시점</span>
              <span className={`ml-auto px-2 py-0.5 rounded text-xs font-bold ${
                spike.alertLevel === 'CRITICAL' ? 'bg-red-500 text-white' :
                spike.alertLevel === 'HIGH' ? 'bg-orange-500 text-white' :
                'bg-yellow-500 text-black'
              }`}>
                {spike.alertLevel}
              </span>
            </div>
            <div className="text-xs text-gray-300 space-y-1">
              <div className="font-semibold text-yellow-300 mb-2">📊 Spike 감지 로직:</div>
              {spike.reasons.map((reason: string, idx: number) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-yellow-400">•</span>
                  <span>{reason}</span>
                </div>
              ))}
              <div className="mt-2 pt-2 border-t border-yellow-500/30">
                <div className="text-yellow-300 font-semibold">우선순위 점수: {spike.priorityScore}점</div>
                {spike.details.whale_zscore && (
                  <div className="text-gray-400">고래 Z-score: {spike.details.whale_zscore.toFixed(2)}</div>
                )}
                {spike.details.telegram_zscore && (
                  <div className="text-gray-400">텔레그램 Z-score: {spike.details.telegram_zscore.toFixed(2)}</div>
                )}
                {spike.details.twitter_zscore && (
                  <div className="text-gray-400">트위터 Z-score: {spike.details.twitter_zscore.toFixed(2)}</div>
                )}
              </div>
            </div>
          </div>
        )}
        
        <div className="space-y-2">
          {uniquePayload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-gray-400 text-xs">{entry.name}:</span>
              </div>
              <span className="text-white font-bold text-sm">
                {entry.name.includes('가격')
                  ? `$${entry.value.toLocaleString()}`
                  : entry.name.includes('변화')
                  ? `${entry.value > 0 ? '+' : ''}${entry.value.toFixed(2)}%`
                  : `${entry.value.toFixed(0)}건`}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin absolute top-0 left-0" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
        <p className="text-gray-300 mt-6 text-lg font-medium">데이터 시각화 준비 중...</p>
        <p className="text-gray-500 mt-2 text-sm">고래 지갑과 가격 데이터 로딩 중</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 & 컨트롤 */}
      <div className="flex flex-wrap gap-4 items-center justify-between bg-gray-900 p-4 rounded-xl border border-gray-800">
        {/* 왼쪽: 제목 */}
        <div>
          <h3 className="text-xl font-bold text-white mb-1">
            🐋 고래 지갑 & 코인 가격 트렌드
          </h3>
          <p className="text-gray-400 text-sm">
            실시간 상관관계 분석
          </p>
        </div>

        {/* 오른쪽: 컨트롤들 */}
        <div className="flex flex-wrap gap-3 items-center">
          {/* 코인 */}
          <div className="flex gap-2 bg-gray-800 p-1 rounded-lg">
            {([
              { value: 'btc', label: 'BTC', color: 'orange' },
              { value: 'eth', label: 'ETH', color: 'blue' },
              { value: 'both', label: 'Both', color: 'purple' }
            ] as const).map((coin) => (
              <button
                key={coin.value}
                onClick={() => setSelectedCoin(coin.value)}
                className={`px-3 py-1.5 rounded-md font-medium text-sm transition-all ${
                  selectedCoin === coin.value
                    ? `bg-${coin.color}-600 text-white shadow-lg`
                    : 'text-gray-400 hover:text-white'
                }`}
                style={
                  selectedCoin === coin.value
                    ? {
                        backgroundColor:
                          coin.color === 'orange'
                            ? '#f97316'
                            : coin.color === 'blue'
                            ? '#3b82f6'
                            : '#a855f7'
                      }
                    : undefined
                }
              >
                {coin.label}
              </button>
            ))}
          </div>

          {/* 차트 타입 */}
          <div className="flex gap-2 bg-gray-800 p-1 rounded-lg">
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1.5 rounded-md font-medium text-sm transition-all ${
                chartType === 'line'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              선형
            </button>
            <button
              onClick={() => setChartType('area')}
              className={`px-3 py-1.5 rounded-md font-medium text-sm transition-all ${
                chartType === 'area'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              영역
            </button>
            <button
              onClick={() => setChartType('composed')}
              className={`px-3 py-1.5 rounded-md font-medium text-sm transition-all ${
                chartType === 'composed'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              복합
            </button>
          </div>

          {/* 날짜 선택 캘린더 */}
          <div className="flex items-center gap-2 bg-gray-800 px-3 py-1.5 rounded-lg">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <input
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              className="bg-transparent text-gray-300 text-sm border-none outline-none cursor-pointer"
              style={{ colorScheme: 'dark' }}
            />
          </div>
        </div>
      </div>

      {/* 차트 영역 */}
      <div 
        className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 border border-gray-700 shadow-2xl"
        onMouseDown={handleChartMouseDown}
        onMouseMove={handleChartMouseMove}
        onMouseUp={handleChartMouseUp}
        onMouseLeave={handleChartMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        {isDragging && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20 rounded-2xl z-10 pointer-events-none">
            <div className="text-white text-sm font-medium">드래그 중...</div>
          </div>
        )}
        <ResponsiveContainer width="100%" height={550}>
          {chartType === 'composed' ? (
            <ComposedChart data={dataWithSpikes} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <defs>
                <linearGradient id="whaleGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
              <XAxis
                dataKey="date"
                stroke="#9ca3af"
                style={{ fontSize: '11px' }}
                tick={{ fill: '#9ca3af' }}
              />
              
              <YAxis
                yAxisId="left"
                stroke="#a855f7"
                style={{ fontSize: '11px' }}
                tick={{ fill: '#a855f7' }}
                domain={['auto', 'auto']}
                allowDataOverflow={false}
                label={{
                  value: '고래 거래 (건)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#a855f7',
                  style: { fontSize: '12px' }
                }}
              />
              
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#60a5fa"
                style={{ fontSize: '11px' }}
                tick={{ fill: '#60a5fa' }}
                domain={['auto', 'auto']}
                allowDataOverflow={false}
                label={{
                  value: '가격 ($)',
                  angle: 90,
                  position: 'insideRight',
                  fill: '#60a5fa',
                  style: { fontSize: '12px' }
                }}
              />
              
              <Tooltip content={<CustomTooltip spikePoints={spikePoints} />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              
              {/* Spike 마커들 */}
              {spikePoints.map((spike, idx) => {
                const dataPoint = filteredData.find(
                  (d) => new Date(d.timestamp).getTime() === new Date(spike.timestamp).getTime()
                );
                if (!dataPoint) return null;
                
                return (
                  <ReferenceLine
                    key={idx}
                    x={dataPoint.date}
                    stroke="#ffd700"
                    strokeWidth={2}
                    strokeDasharray="0"
                    label={{
                      value: '⭐ SPIKE!',
                      position: 'top',
                      fill: '#ffd700',
                      fontSize: 12,
                      fontWeight: 'bold',
                      offset: 10,
                    }}
                  />
                );
              })}

              {/* 고래 거래 (영역 + 바) */}
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="whale_tx_count"
                fill="url(#whaleGradient)"
                stroke="#a855f7"
                strokeWidth={0}
                name="고래 거래"
              />
              <Bar
                yAxisId="left"
                dataKey="whale_tx_count"
                fill="#a855f7"
                opacity={0.6}
                radius={[4, 4, 0, 0]}
                name="고래 거래"
              />

              {/* BTC */}
              {selectedCoin !== 'eth' && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="btc_close"
                  stroke="#f97316"
                  strokeWidth={3}
                  dot={false}
                  name="BTC 가격"
                  activeDot={{ r: 6, fill: '#f97316' }}
                />
              )}

              {/* ETH */}
              {selectedCoin !== 'btc' && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="eth_close"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={false}
                  name="ETH 가격"
                  activeDot={{ r: 6, fill: '#3b82f6' }}
                />
              )}
            </ComposedChart>
          ) : chartType === 'area' ? (
            <AreaChart data={dataWithSpikes} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <defs>
                <linearGradient id="colorWhale" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorBTC" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorETH" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
              <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="left" stroke="#a855f7" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="right" orientation="right" stroke="#60a5fa" style={{ fontSize: '11px' }} />
              <Tooltip content={<CustomTooltip spikePoints={spikePoints} />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              
              {/* Spike 마커들 */}
              {spikePoints.map((spike, idx) => {
                const dataPoint = filteredData.find(
                  (d) => new Date(d.timestamp).getTime() === new Date(spike.timestamp).getTime()
                );
                if (!dataPoint) return null;
                
                return (
                  <ReferenceLine
                    key={idx}
                    x={dataPoint.date}
                    stroke="#ffd700"
                    strokeWidth={2}
                    strokeDasharray="0"
                    label={{
                      value: '⭐ SPIKE!',
                      position: 'top',
                      fill: '#ffd700',
                      fontSize: 12,
                      fontWeight: 'bold',
                      offset: 10,
                    }}
                  />
                );
              })}

              <Area
                yAxisId="left"
                type="monotone"
                dataKey="whale_tx_count"
                stroke="#a855f7"
                fillOpacity={1}
                fill="url(#colorWhale)"
                strokeWidth={2}
                name="고래 거래"
              />
              
              {selectedCoin !== 'eth' && (
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="btc_close"
                  stroke="#f97316"
                  fillOpacity={1}
                  fill="url(#colorBTC)"
                  strokeWidth={2}
                  name="BTC 가격"
                />
              )}
              
              {selectedCoin !== 'btc' && (
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="eth_close"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorETH)"
                  strokeWidth={2}
                  name="ETH 가격"
                />
              )}
            </AreaChart>
          ) : (
            <LineChart data={dataWithSpikes} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
              <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="left" stroke="#a855f7" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="right" orientation="right" stroke="#60a5fa" style={{ fontSize: '11px' }} />
              <Tooltip content={<CustomTooltip spikePoints={spikePoints} />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              
              {/* Spike 마커들 */}
              {spikePoints.map((spike, idx) => {
                const dataPoint = filteredData.find(
                  (d) => new Date(d.timestamp).getTime() === new Date(spike.timestamp).getTime()
                );
                if (!dataPoint) return null;
                
                return (
                  <ReferenceLine
                    key={idx}
                    x={dataPoint.date}
                    stroke="#ffd700"
                    strokeWidth={2}
                    strokeDasharray="0"
                    label={{
                      value: '⭐ SPIKE!',
                      position: 'top',
                      fill: '#ffd700',
                      fontSize: 12,
                      fontWeight: 'bold',
                      offset: 10,
                    }}
                  />
                );
              })}

              <Line
                yAxisId="left"
                type="monotone"
                dataKey="whale_tx_count"
                stroke="#a855f7"
                strokeWidth={3}
                dot={false}
                name="고래 거래"
              />
              
              {selectedCoin !== 'eth' && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="btc_close"
                  stroke="#f97316"
                  strokeWidth={3}
                  dot={false}
                  name="BTC 가격"
                />
              )}
              
              {selectedCoin !== 'btc' && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="eth_close"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={false}
                  name="ETH 가격"
                />
              )}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* 고래 거래 플로우 상세보기 버튼 */}
      <div className="w-full">
        <a
          href="https://graph-visualization2.vercel.app"
          target="_blank"
          rel="noopener noreferrer"
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
        >
          <span>고래 거래 플로우 상세보기</span>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>

      {/* 통계 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/20 border border-purple-600/50 rounded-xl p-4 hover:shadow-lg hover:shadow-purple-500/20 transition-all">
          <div className="text-purple-300 text-xs font-medium mb-2">평균 고래 거래</div>
          <div className="text-white text-3xl font-bold">
            {(data.reduce((sum, d) => sum + d.whale_tx_count, 0) / data.length).toFixed(0)}
            <span className="text-purple-400 text-lg ml-1">건</span>
          </div>
        </div>

        {selectedCoin !== 'eth' && (
          <>
            <div className="bg-gradient-to-br from-orange-900/40 to-orange-800/20 border border-orange-600/50 rounded-xl p-4 hover:shadow-lg hover:shadow-orange-500/20 transition-all">
              <div className="text-orange-300 text-xs font-medium mb-2">BTC 평균 가격</div>
              <div className="text-white text-3xl font-bold">
                ${(data.reduce((sum, d) => sum + d.btc_close, 0) / data.length / 1000).toFixed(1)}
                <span className="text-orange-400 text-lg ml-1">K</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-900/40 to-orange-800/20 border border-orange-600/50 rounded-xl p-4 hover:shadow-lg hover:shadow-orange-500/20 transition-all">
              <div className="text-orange-300 text-xs font-medium mb-2">BTC 평균 변화</div>
              <div className={`text-3xl font-bold ${
                (data.reduce((sum, d) => sum + d.btc_change, 0) / data.length) > 0
                  ? 'text-green-400'
                  : 'text-red-400'
              }`}>
                {(data.reduce((sum, d) => sum + d.btc_change, 0) / data.length) > 0 ? '+' : ''}
                {(data.reduce((sum, d) => sum + d.btc_change, 0) / data.length).toFixed(2)}
                <span className="text-lg ml-1">%</span>
              </div>
            </div>
          </>
        )}

        {selectedCoin !== 'btc' && (
          <>
            <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-blue-600/50 rounded-xl p-4 hover:shadow-lg hover:shadow-blue-500/20 transition-all">
              <div className="text-blue-300 text-xs font-medium mb-2">ETH 평균 가격</div>
              <div className="text-white text-3xl font-bold">
                ${(data.reduce((sum, d) => sum + d.eth_close, 0) / data.length).toFixed(0)}
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-blue-600/50 rounded-xl p-4 hover:shadow-lg hover:shadow-blue-500/20 transition-all">
              <div className="text-blue-300 text-xs font-medium mb-2">ETH 평균 변화</div>
              <div className={`text-3xl font-bold ${
                (data.reduce((sum, d) => sum + d.eth_change, 0) / data.length) > 0
                  ? 'text-green-400'
                  : 'text-red-400'
              }`}>
                {(data.reduce((sum, d) => sum + d.eth_change, 0) / data.length) > 0 ? '+' : ''}
                {(data.reduce((sum, d) => sum + d.eth_change, 0) / data.length).toFixed(2)}
                <span className="text-lg ml-1">%</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RealTimeChart;

