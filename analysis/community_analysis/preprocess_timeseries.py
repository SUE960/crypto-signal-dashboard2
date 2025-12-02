import pandas as pd
import numpy as np

INPUT_PATH = "data/twitter_influencer_labeled_rows.csv"

OUTPUT_4H = "../../data/community_ts_4h.csv"
OUTPUT_1H = "../../data/community_ts_1h.csv"
OUTPUT_1D = "../../data/community_ts_1d.csv"


def preprocess_timeseries():
    df = pd.read_csv(INPUT_PATH)

    # 🔹 post_date를 datetime(UTC)으로 변환
    df["post_date"] = pd.to_datetime(df["post_date"], utc=True)
    df = df.set_index("post_date")

    def make_ts(freq: str, out_path: str):
        grouped = df.resample(freq).agg({
            "sentiment_score": ["mean", "var"],
            "sentiment": lambda x: x.value_counts().to_dict(),
            "post_content": "count"
        })

        grouped.columns = ["avg_sentiment", "variance", "sentiment_dict", "total_posts"]
        grouped = grouped.fillna(0)

        grouped["pos"] = grouped["sentiment_dict"].apply(lambda x: x.get("positive", 0))
        grouped["neg"] = grouped["sentiment_dict"].apply(lambda x: x.get("negative", 0))
        grouped["neu"] = grouped["sentiment_dict"].apply(lambda x: x.get("neutral", 0))

        grouped = grouped.drop(columns=["sentiment_dict"])

        # 🔹 index(post_date)를 컬럼으로 복원
        grouped.reset_index(inplace=True)  # -> 'post_date' 컬럼 생성

        # 혹시라도 이름이 이상하게 되면 강제로 맞춰줌
        if "post_date" not in grouped.columns:
            first_col = grouped.columns[0]
            grouped.rename(columns={first_col: "post_date"}, inplace=True)

        grouped.to_csv(out_path, index=False)
        print(f"Saved → {out_path}")

    make_ts("1H", OUTPUT_1H)
    make_ts("4H", OUTPUT_4H)
    make_ts("1D", OUTPUT_1D)


if __name__ == "__main__":
    preprocess_timeseries()
