import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# NLTK 데이터 다운로드 (최초 1회만 필요)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

import os

# 스크립트 기준 절대 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

INPUT_PATH = os.path.join(DATA_DIR, "twitter_influencer_labeled_rows.csv")
OUT_DAILY = os.path.join(DATA_DIR, "community_keywords_daily.csv")
OUT_WEEKLY = os.path.join(DATA_DIR, "community_keywords_weekly.csv")
OUT_MONTHLY = os.path.join(DATA_DIR, "community_keywords_monthly.csv")
TEXT_COL = "post_content"
SENTIMENT_COL = "sentiment"

# NLTK 표준 불용어 + 추가 불용어
STOPWORDS = set(stopwords.words('english'))
# 추가 불용어 (SNS/암호화폐 관련)
EXTRA_STOPWORDS = {"rt", "im", "dont", "cant", "youre", "thats", "gonna", "wont", "didnt", "doesnt", "ive", "youve", "weve", "theyre", "hes", "shes", "lets", "theres", "whats", "heres", "isnt", "arent", "wasnt", "werent", "hasnt", "havent", "hadnt", "couldnt", "wouldnt", "shouldnt", "mustnt", "neednt"}
STOPWORDS.update(EXTRA_STOPWORDS)

# 의미 있는 품사 태그 (명사, 동사, 형용사, 부사)
# NN: 명사, NNS: 복수명사, NNP: 고유명사, NNPS: 복수 고유명사
# VB: 동사원형, VBD: 과거형, VBG: 현재분사, VBN: 과거분사, VBP: 현재형, VBZ: 3인칭 단수
# JJ: 형용사, JJR: 비교급, JJS: 최상급
# RB: 부사 (선택적)
MEANINGFUL_POS_TAGS = {
    'NN', 'NNS', 'NNP', 'NNPS',  # 명사
    'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # 동사
    'JJ', 'JJR', 'JJS',  # 형용사
}


def clean_text(text):
    """텍스트 전처리: URL 제거, 특수문자 제거, 불용어 제거, 의미 있는 품사만 추출"""
    text = str(text).lower()
    # URL 제거
    text = re.sub(r"http\S+", "", text)
    # 특수문자 제거 (알파벳, 숫자, 한글, 공백만 유지)
    text = re.sub(r"[^a-zA-Z0-9가-힣 ]", " ", text)
    
    # 토큰화
    tokens = word_tokenize(text)
    
    # 품사 태깅
    tagged = pos_tag(tokens)
    
    # 불용어 제거 + 의미 있는 품사만 선택 + 길이 2 이상
    meaningful_words = [
        word for word, tag in tagged
        if len(word) > 1 
        and word not in STOPWORDS 
        and tag in MEANINGFUL_POS_TAGS
    ]
    
    return meaningful_words


def preprocess_keywords_periodic():
    df = pd.read_csv(INPUT_PATH)

    # ⛔ 날짜 파싱 시 NaT 허용하되 이후 dropna로 제거
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)

    # ⛔ 날짜 없는 row는 제거 (이거 안 하면 100% 오류 터진다)
    df = df.dropna(subset=["post_date"]).copy()

    # 일간
    df["day"] = df["post_date"].dt.strftime("%Y-%m-%d")

    # 주간 → 안전한 방식: 월요일 날짜만 뽑기
    df["week"] = df["post_date"].dt.to_period("W-MON").apply(lambda r: r.start_time.strftime("%Y-%m-%d"))

    # 월간
    df["month"] = df["post_date"].dt.strftime("%Y-%m")

    def make_keyword_csv(df, key, out_path):
        rows = []

        for period_value, group in df.groupby(key):
            counter_total = Counter()
            counter_pos = Counter()
            counter_neg = Counter()
            counter_neu = Counter()

            for _, row in group.iterrows():
                words = clean_text(row[TEXT_COL])
                senti = row[SENTIMENT_COL]

                for w in words:
                    counter_total[w] += 1

                    if senti == "positive":
                        counter_pos[w] += 1
                    elif senti == "negative":
                        counter_neg[w] += 1
                    else:
                        counter_neu[w] += 1

            for w, cnt in counter_total.items():
                rows.append({
                    "period": period_value,
                    "word": w,
                    "total_count": cnt,
                    "positive": counter_pos[w],
                    "negative": counter_neg[w],
                    "neutral": counter_neu[w],
                })

        out_df = pd.DataFrame(rows)
        out_df = out_df.sort_values(["period", "total_count"], ascending=[True, False])
        out_df.to_csv(out_path, index=False)
        print(f"Saved → {out_path}")

    # CSV 생성
    make_keyword_csv(df, "day", OUT_DAILY)
    make_keyword_csv(df, "week", OUT_WEEKLY)
    make_keyword_csv(df, "month", OUT_MONTHLY)


if __name__ == "__main__":
    preprocess_keywords_periodic()
