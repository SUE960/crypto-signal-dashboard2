// app/community/page.tsx
'use client';

import { CommunityProvider } from '../../contexts/CommunityContext';
import SentimentTrend from '../../components/community/SentimentTrend';
import SpikeTimeline from '../../components/community/SpikeTimeline';
import TopPosts from '../../components/community/TopPosts';
import KeywordAnalysis from '../../components/community/KeywordAnalysis';

export default function CommunityPage() {
  return (
    <CommunityProvider>
      <div className="p-6 flex flex-col gap-8">
        <h1 className="text-3xl font-bold">Community Dashboard</h1>

        <section>
          <SentimentTrend />
        </section>

        <section>
          <SpikeTimeline />
        </section>

        <section>
          <TopPosts />
        </section>

        {/* 키워드 분석: WordCloud + Sentiment Breakdown 통합 */}
        <section>
          <KeywordAnalysis />
        </section>
      </div>
    </CommunityProvider>
  );
}
