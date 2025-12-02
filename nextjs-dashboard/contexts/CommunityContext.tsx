'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface CommunityContextType {
  // 스파이크에서 선택한 날짜
  selectedSpikeDate: Date | null;
  setSelectedSpikeDate: (date: Date | null) => void;

  // 워드클라우드에서 선택한 키워드
  selectedKeyword: string;
  setSelectedKeyword: (keyword: string) => void;
}

const CommunityContext = createContext<CommunityContextType | undefined>(
  undefined
);

export function CommunityProvider({ children }: { children: ReactNode }) {
  const [selectedSpikeDate, setSelectedSpikeDate] = useState<Date | null>(null);
  const [selectedKeyword, setSelectedKeyword] = useState<string>('');

  return (
    <CommunityContext.Provider
      value={{
        selectedSpikeDate,
        setSelectedSpikeDate,
        selectedKeyword,
        setSelectedKeyword,
      }}
    >
      {children}
    </CommunityContext.Provider>
  );
}

export function useCommunity() {
  const context = useContext(CommunityContext);
  if (context === undefined) {
    throw new Error('useCommunity must be used within a CommunityProvider');
  }
  return context;
}
