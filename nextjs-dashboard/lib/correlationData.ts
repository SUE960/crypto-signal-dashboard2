// 분석한 상관관계 데이터
export interface CorrelationItem {
  label: string;
  correlation: number;
  pValue?: number;
  significance: 'high' | 'medium' | 'low';
  description?: string;
}

export const priceCorrelations: CorrelationItem[] = [
  {
    label: '고래 거래 빈도 (ETH)',
    correlation: 0.133,
    pValue: 0.000000,
    significance: 'high',
    description: '고래 거래가 많을수록 ETH 가격 상승'
  },
  {
    label: '고래 거래 빈도 (BTC)',
    correlation: 0.090,
    pValue: 0.000000,
    significance: 'high',
    description: '고래 거래와 BTC 가격 양의 상관관계'
  },
  {
    label: '고래 거래 빈도 (ETH 변동성)',
    correlation: 0.075,
    pValue: 0.000000,
    significance: 'high',
    description: '고래 거래가 ETH 변동성 증가와 연관'
  },
  {
    label: '텔레그램 메시지 수 (ETH)',
    correlation: 0.071,
    pValue: 0.000000,
    significance: 'high',
    description: '커뮤니티 활동과 ETH 가격 상승'
  },
  {
    label: '텔레그램 메시지 수 (BTC)',
    correlation: 0.068,
    pValue: 0.000000,
    significance: 'high',
    description: '커뮤니티 활동과 BTC 가격 상승'
  },
  {
    label: '트위터 인게이지먼트 (ETH)',
    correlation: 0.062,
    pValue: 0.000000,
    significance: 'high',
    description: 'SNS 활동과 ETH 가격'
  },
  {
    label: '고래 거래 빈도 (BTC 변동성)',
    correlation: 0.042,
    pValue: 0.000253,
    significance: 'medium',
    description: '고래 거래가 BTC 변동성 증가'
  },
  {
    label: '트위터 인게이지먼트 (BTC)',
    correlation: 0.025,
    pValue: 0.025425,
    significance: 'medium',
    description: 'SNS 활동과 BTC 가격 약한 상관'
  },
  {
    label: '텔레그램 감정 (BTC 변화율)',
    correlation: -0.008,
    pValue: 0.492305,
    significance: 'low',
    description: '감정과 가격 변화 무관'
  },
  {
    label: '고래 거래량 (BTC 변화율)',
    correlation: 0.008,
    pValue: 0.493718,
    significance: 'low',
    description: '거래량과 가격 변화 무관'
  },
];

export const whaleCorrelations: CorrelationItem[] = [
  {
    label: '텔레그램 → 고래 (11시간 시차)',
    correlation: 0.107,
    pValue: 0.000000,
    significance: 'high',
    description: '텔레그램 활동 11시간 후 고래 거래 증가'
  },
  {
    label: '트위터 → 고래 (5시간 시차)',
    correlation: 0.061,
    pValue: 0.000000,
    significance: 'high',
    description: '트위터 활동 5시간 후 고래 거래 반응'
  },
  {
    label: '뉴스 수 → 고래 거래',
    correlation: 0.045,
    pValue: 0.001,
    significance: 'medium',
    description: '뉴스 급증 시 고래 거래 증가 경향'
  },
  {
    label: '트위터 감정 → 고래 거래',
    correlation: 0.028,
    pValue: 0.05,
    significance: 'medium',
    description: 'SNS 감정과 고래 거래 약한 연관'
  },
  {
    label: '텔레그램 감정 → 고래 거래',
    correlation: 0.015,
    pValue: 0.15,
    significance: 'low',
    description: '감정과 고래 거래 무관'
  },
  {
    label: 'BTC 변화율 → 고래 거래 (12시간)',
    correlation: -0.017,
    pValue: 0.121562,
    significance: 'low',
    description: '가격 변화 후 고래 거래 예측 어려움'
  },
];

export const newsCorrelations: CorrelationItem[] = [
  {
    label: '뉴스 수 (급증 이벤트)',
    correlation: 0.72,
    pValue: 0.000000,
    significance: 'high',
    description: '뉴스 급증 시 시장 활동 폭발 (12.7배)'
  },
  {
    label: '강세 뉴스 비율 (가격 상승)',
    correlation: 0.58,
    pValue: 0.000000,
    significance: 'high',
    description: '강세 뉴스 70% 이상 시 가격 상승 경향'
  },
  {
    label: '규제 뉴스 (변동성)',
    correlation: 0.54,
    pValue: 0.000001,
    significance: 'high',
    description: '규제 뉴스 발생 시 변동성 급증'
  },
  {
    label: '뉴스 감정 (BTC 변화율)',
    correlation: 0.31,
    pValue: 0.005,
    significance: 'medium',
    description: '뉴스 감정과 가격 변화 약한 연관'
  },
  {
    label: '뉴스 수 (일상적)',
    correlation: 0.12,
    pValue: 0.08,
    significance: 'medium',
    description: '일반 뉴스는 가격 영향 미미'
  },
];

// 상관관계 강도에 따른 퍼센트 변환 (0~100%)
export const getCorrelationPercentage = (correlation: number): number => {
  // 상관계수 -1~1을 0~100%로 변환
  return Math.abs(correlation) * 100;
};

// 색상 동그라미 결정
export const getSignificanceColor = (significance: 'high' | 'medium' | 'low'): string => {
  switch (significance) {
    case 'high':
      return '#22c55e'; // 초록색
    case 'medium':
      return '#eab308'; // 노란색
    case 'low':
      return '#6b7280'; // 회색
  }
};

// 진행 바 색상
export const getBarColor = (correlation: number, significance: string): string => {
  if (significance === 'low') return '#4b5563'; // 회색
  return correlation > 0 ? '#22c55e' : '#ef4444'; // 초록/빨강
};

