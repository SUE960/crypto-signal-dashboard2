// 분석한 상관관계 데이터
export interface CorrelationItem {
  label: string;
  correlation: number;
  pValue?: number;
  significance: 'high' | 'medium' | 'low';
  description?: string;
  detailedAnalysis?: string; // 상세 분석 (툴팁용)
}

export const priceCorrelations: CorrelationItem[] = [
  {
    label: '고래 거래 빈도 (ETH)',
    correlation: 0.133,
    pValue: 0.000000,
    significance: 'high',
    description: '고래 거래가 많을수록 ETH 가격 상승',
    detailedAnalysis: `📊 가장 강력한 상관관계 (r=0.133, p<0.001)
    
• 고래 거래 빈도가 1 표준편차 증가 시 ETH 가격 평균 13.3% 상승
• 7,992개 데이터 포인트 분석 결과
• 통계적으로 매우 유의미 (p-value < 0.000001)
• ETH가 BTC보다 고래 거래에 더 민감하게 반응

💡 활용: 고래 거래 급증 관찰 시 ETH 매수 타이밍으로 활용 가능`
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
    description: '텔레그램 활동 11시간 후 고래 거래 증가',
    detailedAnalysis: `⏰ 시차 상관관계 분석 결과 (r=0.107, p<0.001)

• 텔레그램 메시지 급증 → 약 11시간 후 고래 거래 증가
• 24시간 시차 분석 중 11시간에서 최대 상관관계 확인
• 커뮤니티 논의가 대형 투자자 행동에 선행 지표로 작용
• 평균 11시간의 의사결정 시간 소요

💡 활용: 텔레그램 활동 급증 감지 시 11시간 후 시장 변동 대비`
  },
  {
    label: '트위터 → 고래 (5시간 시차)',
    correlation: 0.061,
    pValue: 0.000000,
    significance: 'high',
    description: '트위터 활동 5시간 후 고래 거래 반응',
    detailedAnalysis: `⚡ 빠른 반응 시차 (r=0.061, p<0.001)

• 트위터 인플루언서 활동 증가 → 약 5시간 후 고래 거래 반응
• 텔레그램(11시간)보다 2배 이상 빠른 반응 속도
• SNS 확산력이 빠른 의사결정에 영향
• 주로 단기 트레이더들의 빠른 진입/청산과 연관

💡 활용: 트위터 버즈 발생 시 5시간 내 시장 움직임 예상`
  },
  {
    label: '강세 뉴스 비율 (가격 상승)',
    correlation: 0.58,
    pValue: 0.000000,
    significance: 'high',
    description: '강세 뉴스 70% 이상 시 가격 상승 경향',
    detailedAnalysis: `📰 뉴스 감정 분석 (r=0.58, p<0.001)

• 강세 뉴스가 전체의 70% 이상을 차지할 때:
  - BTC 평균 변화율: +0.25%
  - ETH 평균 변화율: +0.51% (BTC의 2배)
  
• 20,000개 뉴스 기사 감정 분석 결과
• 강세 뉴스: 2,490건 (12.5%)
• 약세 뉴스: 1,878건 (9.4%)

💡 활용: 시간당 강세 뉴스 비중 70% 초과 시 매수 신호`
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
    description: '뉴스 급증 시 시장 활동 폭발 (12.7배)',
    detailedAnalysis: `🚨 극강 상관관계 (r=0.72, p<0.001)

• BTC 가격 급변(±2%) 시 평균 활동 수준:
  - 텔레그램: 2.80 msgs (평소 0.22의 12.7배 ⬆️)
  - 고래 거래: 13.22 txs (평소 2.66의 5.0배 ⬆️)
  - 트위터: 4,165 (평소 194의 21.5배 ⬆️)

• 181회의 BTC 급변 이벤트 분석
• 뉴스 급증은 가격 변동의 강력한 동시 지표

💡 활용: 시간당 10건 이상 뉴스 발생 시 변동성 확대 대비 필수`
  },
  {
    label: '강세 뉴스 비율 (가격 상승)',
    correlation: 0.58,
    pValue: 0.000000,
    significance: 'high',
    description: '강세 뉴스 70% 이상 시 가격 상승 경향',
    detailedAnalysis: `📰 뉴스 감정 분석 (r=0.58, p<0.001)

• 강세 뉴스가 전체의 70% 이상을 차지할 때:
  - BTC 평균 변화율: +0.25%
  - ETH 평균 변화율: +0.51% (BTC의 2배)
  
• 20,000개 뉴스 기사 감정 분석 결과
• 강세 뉴스: 2,490건 (12.5%)
• 약세 뉴스: 1,878건 (9.4%)

💡 활용: 시간당 강세 뉴스 비중 70% 초과 시 매수 신호`
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

