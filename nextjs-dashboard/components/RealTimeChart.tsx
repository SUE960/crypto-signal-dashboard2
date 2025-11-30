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
  Bar
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

const RealTimeChart: React.FC<RealTimeChartProps> = ({ dataPath }) => {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [chartType, setChartType] = useState<'line' | 'area' | 'composed'>('composed');
  const [selectedCoin, setSelectedCoin] = useState<'btc' | 'eth' | 'both'>('both');

  useEffect(() => {
    loadRealData();
  }, [timeRange]);

  const loadRealData = async () => {
    setLoading(true);
    try {
      // API에서 실제 데이터 로드
      const response = await fetch(`/api/timeseries?range=${timeRange}`);
      
      if (!response.ok) {
        throw new Error('데이터 로딩 실패');
      }
      
      const jsonData = await response.json();
      setData(jsonData);
    } catch (error) {
      console.error('데이터 로딩 중 오류:', error);
      // 에러 시 더미 데이터 사용
      setData(generateDummyData(timeRange));
    } finally {
      setLoading(false);
    }
  };

  const generateDummyData = (range: string): ChartDataPoint[] => {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const dataPoints: ChartDataPoint[] = [];
    const now = new Date();

    for (let i = days * 24; i >= 0; i -= 24) { // 일별 데이터
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
          ...(range === '90d' ? {} : { hour: '2-digit' })
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

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-gray-950 border-2 border-gray-700 rounded-xl p-4 shadow-2xl backdrop-blur-sm">
        <p className="text-gray-300 font-semibold mb-3 text-sm border-b border-gray-700 pb-2">
          📅 {label}
        </p>
        
        <div className="space-y-2">
          {payload.map((entry: any, index: number) => (
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
        <div className="flex flex-wrap gap-3">
          {/* 기간 */}
          <div className="flex gap-2 bg-gray-800 p-1 rounded-lg">
            {(['7d', '30d', '90d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1.5 rounded-md font-medium text-sm transition-all ${
                  timeRange === range
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {range === '7d' ? '7일' : range === '30d' ? '30일' : '90일'}
              </button>
            ))}
          </div>

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
        </div>
      </div>

      {/* 차트 영역 */}
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 border border-gray-700 shadow-2xl">
        <ResponsiveContainer width="100%" height={550}>
          {chartType === 'composed' ? (
            <ComposedChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
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
                label={{
                  value: '가격 ($)',
                  angle: 90,
                  position: 'insideRight',
                  fill: '#60a5fa',
                  style: { fontSize: '12px' }
                }}
              />
              
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />

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
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
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
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />

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
            <LineChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
              <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="left" stroke="#a855f7" style={{ fontSize: '11px' }} />
              <YAxis yAxisId="right" orientation="right" stroke="#60a5fa" style={{ fontSize: '11px' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />

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

