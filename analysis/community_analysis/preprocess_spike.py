import pandas as pd

INPUT = "../../data/community_ts_1h.csv"
OUTPUT = "../../data/community_spike_events.csv"


def preprocess_spike():
    df = pd.read_csv(INPUT)

    # 🔹 시간 컬럼 찾기: 우선순위 post_date > timestamp > 첫 번째 컬럼
    if "post_date" in df.columns:
        time_col = "post_date"
    elif "timestamp" in df.columns:
        time_col = "timestamp"
    else:
        time_col = df.columns[0]  # 그래도 뭐라도 있긴 하도록

    # 🔹 datetime 변환 (UTC)
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df = df.sort_values(time_col)

    # 🔹 avg_sentiment 숫자 변환 (혹시 문자열로 되어 있으면)
    if "avg_sentiment" not in df.columns:
        raise ValueError("community_ts_1h.csv에 'avg_sentiment' 컬럼이 없습니다. timeseries 전처리부터 확인하세요.")

    df["avg_sentiment"] = pd.to_numeric(df["avg_sentiment"], errors="coerce")

    # 🔹 감성 변화량
    df["diff"] = df["avg_sentiment"].diff()

    # 🔹 rolling 평균/표준편차 (24시간 윈도우, min_periods로 초기구간 NaN 방지)
    df["roll_mean"] = df["diff"].rolling(24, min_periods=5).mean()
    df["roll_std"] = df["diff"].rolling(24, min_periods=5).std()

    # 🔹 z-score
    df["zscore"] = (df["diff"] - df["roll_mean"]) / df["roll_std"]

    # 🔹 스파이크 flag (threshold 3단계)
    df["spike_2_0"] = df["zscore"] >= 2.0
    df["spike_2_5"] = df["zscore"] >= 2.5
    df["spike_3_0"] = df["zscore"] >= 3.0

    # 🔹 결과 저장
    df.to_csv(OUTPUT, index=False)
    print(f"Saved → {OUTPUT}")


if __name__ == "__main__":
    preprocess_spike()
