"""Answer the open data questions from the PRD. Prints five sections.

  1. Missing audio features / track IDs by decade
  2. Rows that share a song_id
  3. The latest `last_week` values (for the still_charting rule)
  4. Rows with no chart data
  5. How peak_position is distributed (for the "high chart position" threshold)

Run from the project root:  python src/02_check_coverage.py
Paste the full output back into chat.
"""
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CSV = RAW / "billboard_hot_100_spotify_audio_features_enriched.csv"


def header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    df = pd.read_csv(CSV, low_memory=False)
    df["first_week"] = pd.to_datetime(df["first_week"], errors="coerce")
    df["last_week"] = pd.to_datetime(df["last_week"], errors="coerce")
    df["decade"] = (df["first_week"].dt.year // 10 * 10).astype("Int64")

    # 1. Missing audio features by decade
    header("1. Missing audio features and track IDs by decade of first_week")
    by_decade = df.groupby("decade", dropna=False).agg(
        songs=("song_id", "size"),
        missing_audio=("danceability", lambda s: int(s.isna().sum())),
        missing_track_id=("spotify_track_id", lambda s: int(s.isna().sum())),
    )
    by_decade["missing_audio_%"] = (
        by_decade["missing_audio"] / by_decade["songs"] * 100
    ).round(1)
    by_decade["missing_track_id_%"] = (
        by_decade["missing_track_id"] / by_decade["songs"] * 100
    ).round(1)
    print(by_decade.to_string())

    # 2. Duplicate song_id
    header("2. Rows sharing a song_id")
    dup = df[df.duplicated("song_id", keep=False)].sort_values("song_id")
    print(f"rows involved: {len(dup)}   distinct song_ids involved: {dup['song_id'].nunique()}")
    print(f"fully identical rows (all 33 columns): {int(df.duplicated(keep=False).sum())}")
    cols = ["song_id", "performer", "song", "peak_position", "weeks_on_chart", "first_week", "last_week"]
    print("\nFirst 20 duplicate rows:")
    print(dup[cols].head(20).to_string())

    # 3. Latest last_week values
    header("3. Latest last_week values (how many songs end on each date)")
    latest = df["last_week"].value_counts().sort_index(ascending=False).head(12)
    out = latest.rename("songs").to_frame()
    out["weekday"] = out.index.day_name()
    print(out.to_string())

    # 4. Rows with no chart data
    header("4. Rows with no chart data")
    missing = df[df["peak_position"].isna() | df["weeks_on_chart"].isna()]
    print(missing[cols].to_string())

    # 5. Peak position distribution
    header("5. Songs by peak_position")
    p = df["peak_position"].dropna()
    for cutoff in (1, 5, 10, 20, 40):
        n = int((p <= cutoff).sum())
        print(f"peak <= {cutoff:>2}: {n:>6,}  ({n / len(p) * 100:.1f}%)")
    print(f"total with a peak: {len(p):,}")


if __name__ == "__main__":
    main()
