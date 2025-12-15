"""
감성 분석 유틸리티

VADER를 사용한 텍스트 감성 분석
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd


class SentimentAnalyzer:
    """감성 분석 클래스"""
    
    def __init__(self):
        """VADER 감성 분석기 초기화"""
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text):
        """
        단일 텍스트 감성 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            dict: {'compound', 'pos', 'neu', 'neg', 'label'}
        """
        if not text or pd.isna(text):
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neu': 1.0,
                'neg': 0.0,
                'label': 'neutral'
            }
        
        scores = self.analyzer.polarity_scores(str(text))
        
        # 라벨 결정
        if scores['compound'] >= 0.05:
            label = 'positive'
        elif scores['compound'] <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        scores['label'] = label
        return scores
    
    def analyze_dataframe(self, df, text_column='text'):
        """
        데이터프레임의 텍스트 컬럼 전체 분석
        
        Args:
            df: 데이터프레임
            text_column: 분석할 텍스트 컬럼명
            
        Returns:
            DataFrame: 감성 점수가 추가된 데이터프레임
        """
        if df.empty or text_column not in df.columns:
            return df
        
        results = df[text_column].apply(self.analyze_text)
        
        df['sentiment_compound'] = results.apply(lambda x: x['compound'])
        df['sentiment_pos'] = results.apply(lambda x: x['pos'])
        df['sentiment_neu'] = results.apply(lambda x: x['neu'])
        df['sentiment_neg'] = results.apply(lambda x: x['neg'])
        df['sentiment_label'] = results.apply(lambda x: x['label'])
        
        return df
    
    def get_aggregated_sentiment(self, df, by_column='timestamp'):
        """
        시간/그룹별 감성 집계
        
        Args:
            df: 감성 분석이 완료된 데이터프레임
            by_column: 그룹화할 컬럼 (기본: timestamp)
            
        Returns:
            DataFrame: 집계된 감성 데이터
        """
        if df.empty or 'sentiment_compound' not in df.columns:
            return pd.DataFrame()
        
        agg_df = df.groupby(by_column).agg({
            'sentiment_compound': 'mean',
            'sentiment_pos': 'mean',
            'sentiment_neu': 'mean',
            'sentiment_neg': 'mean'
        }).reset_index()
        
        agg_df = agg_df.rename(columns={
            'sentiment_compound': 'avg_sentiment',
            'sentiment_pos': 'avg_positive',
            'sentiment_neu': 'avg_neutral',
            'sentiment_neg': 'avg_negative'
        })
        
        return agg_df


if __name__ == '__main__':
    # 테스트
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "Bitcoin is going to the moon! Amazing gains!",
        "This is a terrible investment, I'm losing money",
        "The price is stable today",
        "Crypto market looks promising for 2025"
    ]
    
    print("=== 감성 분석 테스트 ===\n")
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"Text: {text}")
        print(f"  Compound: {result['compound']:.3f}")
        print(f"  Label: {result['label']}")
        print()








