import pandas as pd
import re

INPUT_PATH = "data/twitter_influencer_labeled_rows.csv"
OUTPUT_PATH = "../../data/community_keywords_freq.csv"

TEXT_COL = "post_content"
SENTIMENT_COL = "sentiment"


def clean_text(text: str):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)                 # URL 제거
    text = re.sub(r"[^a-zA-Z0-9가-힣 ]", " ", text)      # 문자/숫자/한글만
    tokens = [t for t in text.split() if len(t) > 1]    # 한 글자짜리 토큰 제거
    return tokens


def preprocess_keywords():
    df = pd.read_csv(INPUT_PATH)

    # 🔒 컬럼 존재 여부 안전 체크
    missing = [c for c in [TEXT_COL, SENTIMENT_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"CSV에 다음 컬럼이 없습니다: {missing}. 실제 컬럼들: {list(df.columns)}")

    records = []

    # 🔁 각 row마다 단어 + sentiment 수집
    for _, row in df.iterrows():
        tokens = clean_text(row[TEXT_COL])
        sentiment = row[SENTIMENT_COL]

        for w in tokens:
            records.append((w, sentiment))

    if not records:
        print("토큰화 결과가 비어 있습니다. 데이터나 전처리 로직을 확인하세요.")
        return

    words_df = pd.DataFrame(records, columns=["word", "sentiment"])

    # 🔢 단어별/감성별 집계
    summary = words_df.groupby(["word", "sentiment"]).size().unstack().fillna(0)

    # sentiment 컬럼명 정리 (없는 감정은 0으로 채움)
    for col in ["positive", "negative", "neutral"]:
        if col not in summary.columns:
            summary[col] = 0

    summary = summary[["positive", "negative", "neutral"]]
    summary["total_count"] = summary.sum(axis=1)

    # 많이 등장한 단어 순으로 정렬
    summary = summary.sort_values("total_count", ascending=False)

    summary.to_csv(OUTPUT_PATH)
    print(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    preprocess_keywords()
