"""Pieces of the prediction model, kept separate from the script so they can be tested.

Question: using only how a song sounds (Spotify audio features), can we tell
which charting songs reached the top 5?
"""
import pandas as pd

TOP_N = 5                # "high chart position" = peaked at #1-#5 (author's choice)
SPLIT_YEAR = 2010        # train on songs that first charted before this year, test on the rest

FEATURES = [
    "danceability", "energy", "musical_key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "time_signature", "duration_ms", "explicit",
]

# Never used as inputs: they are chart results, derived from chart results, or
# generated labels (PRD requirement 21). Most are not even loaded into the
# database; the list is kept so the test can check the rule.
EXCLUDED = [
    "peak_position", "weeks_on_chart", "still_charting", "spotify_track_popularity",
    "chart_success_tier", "hit_longevity_profile", "acoustic_mood_cluster",
    "musical_era", "evidence_span", "cot_rationale", "confidence_score",
]

MODEL_QUERY = f"""
SELECT s.song_key, s.first_year, s.peak_position, s.still_charting,
       {', '.join('a.' + f for f in FEATURES)}
FROM songs AS s
JOIN audio_features AS a ON a.song_key = s.song_key
"""


def add_target(df: pd.DataFrame, top_n: int = TOP_N) -> pd.DataFrame:
    """Add `top_n_hit`: 1 if the song peaked at #top_n or better, else 0."""
    return df.assign(top_n_hit=(df["peak_position"] <= top_n).astype(int))


def time_split(df: pd.DataFrame, split_year: int = SPLIT_YEAR):
    """Older songs train, newer songs test.

    Songs still on the chart when the data ends are dropped from the test set,
    because their peak could still rise. Returns (train, test, n_dropped).
    """
    train = df[df["first_year"] < split_year]
    test = df[df["first_year"] >= split_year]
    n_dropped = int(test["still_charting"].sum())
    test = test[test["still_charting"] == 0]
    return train, test, n_dropped
