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
} from 'recharts';

interface ChartDataPoint {
  timestamp: string;
  date: string;
  whale_tx_count: number;
  whale_volume_sum: number;
  btc_close: number;
  eth_close: number;
  btc_change: number;
  eth_change: number;
}

const TimeSeriesChart: React.FC = () => {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');
  const [displayMode, setDisplayMode] = useState<'price' | 'change'>('price');
  const [selectedCoin, setSelectedCoin] = useState<'btc' | 'eth' | 'both'>('both');

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      // 실제 환경에서는 API 엔드포인트에서 데이터를 가져옵니다
      // 여기서는 시뮬레이션 데이터를 사용합니다
      const mockData = generateMockData(timeRange);
      setData(mockData);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = (range: string): ChartDataPoint[] => {
    const days = range === '7d' ? 7 : range === '30d' ? 30 : 90;
    const dataPoints: ChartDataPoint[] = [];
    const now = new Date();

    for (let i = days; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);

      // 시뮬레이션 데이터 생성
      const baseWhale = 50 + Math.random() * 100;
      const baseBtc = 100000 + Math.random() * 20000;
      const baseEth = 3500 + Math.random() * 1000;

      dataPoints.push({
        timestamp: date.toISOString(),
        date: date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
        whale_tx_count: Math.round(baseWhale + Math.sin(i / 2) * 30),
        whale_volume_sum: Math.round(baseWhale * 100 + Math.random() * 5000),
        btc_close: Math.round(baseBtc + Math.sin(i / 3) * 5000),
        eth_close: Math.round(baseEth + Math.sin(i / 3) * 300),
        btc_change: (Math.random() - 0.5) * 4,
        eth_change: (Math.random() - 0.5) * 6,
      });
    }

    return dataPoints;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-xl">
        <p className="text-gray-300 text-sm mb-2">{payload[0].payload.date}</p>
        
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span className="text-purple-400 text-sm">고래 거래:</span>
            <span className="text-white font-bold">{payload[0].value.toFixed(0)}건</span>
          </div>
          
          {selectedCoin !== 'eth' && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-orange-400 text-sm">BTC:</span>
              <span className="text-white font-bold">
                ${payload.find((p: any) => p.dataKey.includes('btc'))?.value.toLocaleString()}
              </span>
            </div>
          )}
          
          {selectedCoin !== 'btc' && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-blue-400 text-sm">ETH:</span>
              <span className="text-white font-bold">
                ${payload.find((p: any) => p.dataKey.includes('eth'))?.value.toLocaleString()}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">데이터 시각화 준비 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 컨트롤 패널 */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        {/* 기간 선택 */}
        <div className="flex gap-2">
          <button
            onClick={() => setTimeRange('7d')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              timeRange === '7d'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            7일
          </button>
          <button
            onClick={() => setTimeRange('30d')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              timeRange === '30d'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            30일
          </button>
          <button
            onClick={() => setTimeRange('90d')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              timeRange === '90d'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            90일
          </button>
        </div>

        {/* 코인 선택 */}
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedCoin('btc')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedCoin === 'btc'
                ? 'bg-orange-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            BTC
          </button>
          <button
            onClick={() => setSelectedCoin('eth')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedCoin === 'eth'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            ETH
          </button>
          <button
            onClick={() => setSelectedCoin('both')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedCoin === 'both'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Both
          </button>
        </div>

        {/* 표시 모드 */}
        <div className="flex gap-2">
          <button
            onClick={() => setDisplayMode('price')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              displayMode === 'price'
                ? 'bg-green-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            가격
          </button>
          <button
            onClick={() => setDisplayMode('change')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              displayMode === 'change'
                ? 'bg-green-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            변화율
          </button>
        </div>
      </div>

      {/* 차트 */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="date"
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            
            {/* 왼쪽 Y축: 고래 거래 */}
            <YAxis
              yAxisId="left"
              stroke="#a855f7"
              style={{ fontSize: '12px' }}
              label={{ value: '고래 거래 (건)', angle: -90, position: 'insideLeft', fill: '#a855f7' }}
            />
            
            {/* 오른쪽 Y축: 가격 또는 변화율 */}
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#3b82f6"
              style={{ fontSize: '12px' }}
              label={{
                value: displayMode === 'price' ? '가격 ($)' : '변화율 (%)',
                angle: 90,
                position: 'insideRight',
                fill: '#3b82f6'
              }}
            />
            
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />

            {/* 고래 거래 라인 */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="whale_tx_count"
              stroke="#a855f7"
              strokeWidth={3}
              dot={false}
              name="고래 거래"
              activeDot={{ r: 6 }}
            />

            {/* BTC 라인 */}
            {selectedCoin !== 'eth' && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey={displayMode === 'price' ? 'btc_close' : 'btc_change'}
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                name={displayMode === 'price' ? 'BTC 가격' : 'BTC 변화율'}
                activeDot={{ r: 5 }}
              />
            )}

            {/* ETH 라인 */}
            {selectedCoin !== 'btc' && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey={displayMode === 'price' ? 'eth_close' : 'eth_change'}
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name={displayMode === 'price' ? 'ETH 가격' : 'ETH 변화율'}
                activeDot={{ r: 5 }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 인사이트 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
          <div className="text-purple-400 text-sm mb-1">평균 고래 거래</div>
          <div className="text-white text-2xl font-bold">
            {(data.reduce((sum, d) => sum + d.whale_tx_count, 0) / data.length).toFixed(0)}건
          </div>
        </div>

        {selectedCoin !== 'eth' && (
          <div className="bg-orange-900/20 border border-orange-700 rounded-lg p-4">
            <div className="text-orange-400 text-sm mb-1">BTC 평균 가격</div>
            <div className="text-white text-2xl font-bold">
              ${(data.reduce((sum, d) => sum + d.btc_close, 0) / data.length).toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </div>
          </div>
        )}

        {selectedCoin !== 'btc' && (
          <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <div className="text-blue-400 text-sm mb-1">ETH 평균 가격</div>
            <div className="text-white text-2xl font-bold">
              ${(data.reduce((sum, d) => sum + d.eth_close, 0) / data.length).toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeSeriesChart;

