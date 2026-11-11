"""Look at the rows that share a song_id and sort them into three groups.

  Group A: every column identical             -> keep one row
  Group B: chart fields identical, other
           columns (Spotify or generated) differ -> keep one row
  Group C: chart fields differ               -> separate chart runs (see PRD 8a)

Also prints which columns differ, and how many songs the still_charting
rule flags at 14, 28 and 56 days.

Run from the project root:  python3 src/02b_check_duplicates.py
"""
from collections import Counter
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CSV = RAW / "billboard_hot_100_spotify_audio_features_enriched.csv"
CHART_COLS = ["peak_position", "weeks_on_chart", "first_week", "last_week"]
# The real Billboard data ends on this chart week. The 3,000 rows after it
# look synthetic (see the PRD, Section 1) and are left out.
REAL_DATA_END = pd.Timestamp("2021-05-29")


def main() -> None:
    df = pd.read_csv(CSV, low_memory=False)
    df = df.dropna(subset=CHART_COLS, how="all")  # the 3 corrupted rows
    df = df[pd.to_datetime(df["last_week"]) <= REAL_DATA_END]  # synthetic rows
    print(f"Rows kept: {len(df)}")

    shared = df[df.duplicated("song_id", keep=False)]
    print(f"Shared song_ids: {shared['song_id'].nunique()}  rows: {len(shared)}")

    groups = Counter()
    diff_cols = Counter()
    examples = {}
    for sid, g in shared.groupby("song_id"):
        cols = [c for c in df.columns if g[c].astype(str).nunique() > 1]
        diff_cols.update(cols)
        if not cols:
            grp = "A"
        elif not set(cols) & set(CHART_COLS):
            grp = "B"
        else:
            grp = "C"
        groups[grp] += 1
        examples.setdefault(grp, (sid, cols))

    print("\nGroups (number of song_ids):")
    for k in "ABC":
        print(f"  {k}: {groups[k]}   example: {examples.get(k)}")
    print("\nHow often each column differs within a shared ID:")
    for col, n in diff_cols.most_common():
        print(f"  {col:28s} {n}")

    print("\nstill_charting flag counts (last_week within N days of the latest):")
    lw = pd.to_datetime(df["last_week"], errors="coerce")
    latest = lw.max()
    print(f"  latest last_week: {latest.date()} ({latest.day_name()})")
    for days in (0, 14, 28, 56):
        print(f"  {days:>2} days: {(lw >= latest - pd.Timedelta(days=days)).sum()}")


if __name__ == "__main__":
    main()
