import pandas as pd

INPUT_PATH = "data/twitter_influencer_labeled_rows.csv"
OUTPUT_PATH = "../../data/community_top_posts.csv"

TOP_N = 10  # 상위 10개 우선 표시 (추가 로딩은 Next.js 쪽에서 처리)


def preprocess_top_posts():
    df = pd.read_csv(INPUT_PATH)

    # 🔍 컬럼 체크 (오타 방지)
    required_cols = ["comments", "shares", "likes", "post_content", "post_date", "sentiment"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(f"다음 컬럼이 CSV에서 누락됨: {missing}\n"
                         f"현재 존재하는 컬럼: {list(df.columns)}")

    # 날짜 파싱
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)
    df = df.dropna(subset=["post_date"]).copy()

    # Engagement score 계산 (replies 없음 → comments 사용)
    df["engagement_score"] = (
        df["comments"] * 3 +
        df["shares"] * 2 +
        df["likes"] * 1
    )

    # 전체 sentiment 리스트 (all 포함)
    sentiments = ["positive", "negative", "neutral", "all"]

    result_rows = []

    # sentiment별 top 10
    for senti in sentiments:
        if senti == "all":
            sub = df
        else:
            sub = df[df["sentiment"] == senti]

        if len(sub) == 0:
            continue

        top = sub.sort_values("engagement_score", ascending=False).head(TOP_N)

        for _, row in top.iterrows():
            result_rows.append({
                "sentiment": senti,
                "post_content": row["post_content"],
                "post_date": row["post_date"],
                "comments": row["comments"],
                "shares": row["shares"],
                "likes": row["likes"],
                "engagement_score": row["engagement_score"]
            })

    out = pd.DataFrame(result_rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    preprocess_top_posts()
