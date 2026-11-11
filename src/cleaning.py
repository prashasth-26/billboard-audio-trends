"""Small cleaning functions used by the loader (src/03_load_db.py).

Each function does one thing and is tested in tests/test_cleaning.py.
"""
import ast
import re

import pandas as pd

# The final chart week of the real Billboard data. Rows after it are synthetic
# (PRD Section 1) and are dropped; songs on this chart are still charting.
REAL_DATA_END = pd.Timestamp("2021-05-29")

CHART_COLS = ["peak_position", "weeks_on_chart", "first_week", "last_week"]

AUDIO_COLS = [
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "time_signature",
]

# Words that join a lead artist to a guest. "&", "And", "," and "x" are NOT
# used, because they are often part of one act's name ("Earth, Wind & Fire",
# "Simon & Garfunkel", "Sly And The Family Stone", "Lil Nas X").
_GUEST_SPLIT = re.compile(r"\s+(?:Featuring|Feat\.|feat\.|With)\s+")


def parse_genres(text) -> list[str]:
    """Turn "['pop', 'dance pop']" into ['pop', 'dance pop'].

    Returns [] for a missing value, an empty list, or text that is not a list.
    Genres are lower-cased, stripped and de-duplicated, keeping their order.
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return []
    try:
        value = ast.literal_eval(str(text))
    except (ValueError, SyntaxError):
        return []
    if not isinstance(value, (list, tuple)):
        return []
    seen = []
    for g in value:
        g = str(g).strip().lower()
        if g and g not in seen:
            seen.append(g)
    return seen


def primary_artist(performer: str) -> str:
    """The lead act in a performer credit.

    "Drake Featuring Rihanna" -> "Drake"; "Elton John With Kiki Dee" -> "Elton John".
    "Simon & Garfunkel" stays whole. Limitation: true duets credited with "&"
    ("Ashford & Simpson" vs. "Ariana Grande & Justin Bieber") are not split.
    """
    return _GUEST_SPLIT.split(str(performer).strip(), maxsplit=1)[0].strip()


def decade_of(date) -> int:
    """1987-05-02 -> 1980."""
    return int(pd.Timestamp(date).year // 10 * 10)


def flag_still_charting(last_week, final_week=REAL_DATA_END) -> int:
    """1 if the song was on the final chart in the data, else 0."""
    return int(pd.Timestamp(last_week) == pd.Timestamp(final_week))


def drop_bad_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Remove corrupted and synthetic rows. Returns (kept rows, counts dropped)."""
    no_chart = df[CHART_COLS].isna().all(axis=1)
    last = pd.to_datetime(df["last_week"], errors="coerce")
    synthetic = ~no_chart & (last > REAL_DATA_END)
    counts = {
        "corrupted (no chart data)": int(no_chart.sum()),
        "synthetic (after 2021-05-29)": int(synthetic.sum()),
    }
    return df[~no_chart & ~synthetic].copy(), counts


def dedupe_songs(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Keep one row per song_id.

    Among rows sharing an ID, prefer the one with audio features; ties go to
    the first row in file order. Returns (deduplicated rows, rows removed).
    """
    order = df.assign(_has_audio=df["danceability"].notna(), _pos=range(len(df)))
    order = order.sort_values(["song_id", "_has_audio", "_pos"],
                              ascending=[True, False, True], kind="stable")
    kept = order.drop_duplicates("song_id", keep="first")
    kept = kept.sort_values("_pos").drop(columns=["_has_audio", "_pos"])
    return kept, len(df) - len(kept)
