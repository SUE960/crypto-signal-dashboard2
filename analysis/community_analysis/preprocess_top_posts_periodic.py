import pandas as pd

INPUT_PATH = "data/twitter_influencer_labeled_rows.csv"

OUT_DAILY = "../../data/community_top_posts_daily.csv"
OUT_WEEKLY = "../../data/community_top_posts_weekly.csv"
OUT_MONTHLY = "../../data/community_top_posts_monthly.csv"

TOP_N = 10


def preprocess_top_posts_periodic():
    df = pd.read_csv(INPUT_PATH)

    # 날짜 파싱
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce", utc=True)

    # post_date NaT 제거 (이게 없으면 groupby에서 100% crash)
    df = df.dropna(subset=["post_date"]).copy()

    # Engagement 계산
    df["engagement_score"] = (
        df["comments"] * 3 +
        df["shares"] * 2 +
        df["likes"] * 1
    )

    # --- 기간 계산 (안전한 방식) ---

    # 1) 일간: 가장 안전한 방식
    df["day"] = df["post_date"].dt.floor("D").dt.strftime("%Y-%m-%d")

    # 2) 주간: Pandas Period 대신, 직접 Monday 기준으로 계산 (NaT 문제 0%)
    df["week"] = (df["post_date"] - pd.to_timedelta(df["post_date"].dt.weekday, unit="D"))
    df["week"] = df["week"].dt.strftime("%Y-%m-%d")  # 주 시작일(월요일 날짜)

    # 3) 월간
    df["month"] = df["post_date"].dt.strftime("%Y-%m")

    sentiments = ["positive", "negative", "neutral", "all"]

    def make_periodic(df, key, out_path):
        rows = []

        for period_value, group in df.groupby(key):
            for senti in sentiments:

                if senti == "all":
                    sub = group
                else:
                    sub = group[group["sentiment"] == senti]

                if len(sub) == 0:
                    continue

                top = sub.sort_values("engagement_score", ascending=False).head(TOP_N)

                for _, row in top.iterrows():
                    rows.append({
                        "period": period_value,
                        "sentiment": senti,
                        "post_content": row["post_content"],
                        "post_date": row["post_date"],
                        "comments": row["comments"],
                        "shares": row["shares"],
                        "likes": row["likes"],
                        "engagement_score": row["engagement_score"]
                    })

        out_df = pd.DataFrame(rows)
        out_df.to_csv(out_path, index=False)
        print(f"Saved → {out_path}")

    make_periodic(df, "day", OUT_DAILY)
    make_periodic(df, "week", OUT_WEEKLY)
    make_periodic(df, "month", OUT_MONTHLY)


if __name__ == "__main__":
    preprocess_top_posts_periodic()
