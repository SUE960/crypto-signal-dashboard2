'use client';

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

export default function SentimentTrend({
  timeWindow = '1h',
  coin = 'BTC',
}: {
  timeWindow?: string;
  coin?: string;
}) {
  const [data, setData] = useState<any[]>([]);
  const [priceData, setPriceData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);

        const res = await fetch(
          `/api/community/timeseries?freq=${timeWindow}&coin=${coin}`
        );

        const json = await res.json();

        // 1) 감성 데이터
        const sentiment = json.sentiment.map((row: any) => ({
          time: row.post_date,
          avg_sentiment: Number(row.avg_sentiment),
          variance: Number(row.variance),
          pos: Number(row.pos),
          neg: Number(row.neg),
          neu: Number(row.neu),
        }));

        // 2) 가격 데이터
        const price = json.price.map((p: any) => ({
          time: p.timestamp,
          price: Number(p.close),
        }));

        setData(sentiment);
        setPriceData(price);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [timeWindow, coin]);

  if (loading) {
    return (
      <div className="h-64 border rounded-lg flex items-center justify-center text-gray-400 bg-gray-50">
        Loading sentiment trend...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      {/* 감성 평균 + 가격 라인 차트 */}
      <div className="h-80 w-full border rounded-lg bg-white p-4">
        <h3 className="text-lg font-semibold mb-4">Sentiment & Price Trend</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="time" tick={false} />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />

            <Tooltip />
            <Legend />

            {/* 감성 평균 */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="avg_sentiment"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
            />

            {/* 가격 */}
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="price"
              data={priceData}
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* pos / neg / neu 스택 바차트 */}
      <div className="h-80 w-full border rounded-lg bg-white p-4">
        <h3 className="text-lg font-semibold mb-4">Sentiment Composition</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="time" tick={false} />
            <YAxis />
            <Tooltip />
            <Legend />

            <Bar dataKey="pos" stackId="s" fill="#22c55e" />
            <Bar dataKey="neg" stackId="s" fill="#ef4444" />
            <Bar dataKey="neu" stackId="s" fill="#9ca3af" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
