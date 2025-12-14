// components/community/CommunityFilters.tsx

'use client';

import { useState } from 'react';

export default function CommunityFilters() {
  const [timeWindow, setTimeWindow] = useState('1h');
  const [coin, setCoin] = useState('BTC');
  const [threshold, setThreshold] = useState('2.0');
  const [period, setPeriod] = useState('daily');

  return (
    <div className="flex flex-wrap gap-4 p-4 border rounded-lg bg-white shadow-sm">
      {/* 시간 간격 */}
      <div>
        <label className="text-sm font-medium">Time Window</label>
        <select
          className="block border p-2 rounded"
          value={timeWindow}
          onChange={(e) => setTimeWindow(e.target.value)}
        >
          <option value="1h">1h</option>
          <option value="4h">4h</option>
          <option value="1d">1d</option>
        </select>
      </div>

      {/* 코인 */}
      <div>
        <label className="text-sm font-medium">Coin</label>
        <select
          className="block border p-2 rounded"
          value={coin}
          onChange={(e) => setCoin(e.target.value)}
        >
          <option value="BTC">BTC</option>
          <option value="ETH">ETH</option>
        </select>
      </div>

      {/* Spike Threshold */}
      <div>
        <label className="text-sm font-medium">Spike Threshold</label>
        <select
          className="block border p-2 rounded"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        >
          <option value="2.0">2.0</option>
          <option value="2.5">2.5</option>
          <option value="3.0">3.0</option>
        </select>
      </div>

      {/* Period */}
      <div>
        <label className="text-sm font-medium">Period</label>
        <select
          className="block border p-2 rounded"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
    </div>
  );
}
