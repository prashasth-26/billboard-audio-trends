import numpy as np
import pandas as pd

from cleaning import (
    decade_of, dedupe_songs, drop_bad_rows, flag_still_charting, parse_genres,
    primary_artist,
)


def test_parse_genres_normal_list():
    assert parse_genres("['pop', 'dance pop']") == ["pop", "dance pop"]


def test_parse_genres_missing_and_empty():
    assert parse_genres(np.nan) == []
    assert parse_genres(None) == []
    assert parse_genres("[]") == []


def test_parse_genres_bad_text_and_duplicates():
    assert parse_genres("not a list") == []
    assert parse_genres("['Pop', 'pop ', 'rock']") == ["pop", "rock"]


def test_primary_artist_splits_guests():
    assert primary_artist("Drake Featuring Rihanna") == "Drake"
    assert primary_artist("Elton John With Kiki Dee") == "Elton John"


def test_primary_artist_keeps_group_names():
    assert primary_artist("Simon & Garfunkel") == "Simon & Garfunkel"
    assert primary_artist("Earth, Wind & Fire") == "Earth, Wind & Fire"
    assert primary_artist("Lil Nas X Featuring Billy Ray Cyrus") == "Lil Nas X"


def test_decade_of():
    assert decade_of("1987-05-02") == 1980
    assert decade_of("1990-01-01") == 1990
    assert decade_of("2021-05-29") == 2020


def test_flag_still_charting():
    assert flag_still_charting("2021-05-29") == 1
    assert flag_still_charting("2021-05-22") == 0


def test_drop_bad_rows():
    df = pd.DataFrame({
        "peak_position": [1, np.nan, 5],
        "weeks_on_chart": [3, np.nan, 2],
        "first_week": ["2000-01-01", np.nan, "2023-01-01"],
        "last_week": ["2000-02-01", np.nan, "2023-02-01"],
    })
    kept, counts = drop_bad_rows(df)
    assert len(kept) == 1
    assert counts == {"corrupted (no chart data)": 1, "unreliable (after 2021-05-29)": 1}


def test_dedupe_prefers_row_with_audio():
    df = pd.DataFrame({
        "song_id": ["a", "a", "b"],
        "danceability": [np.nan, 0.7, 0.1],
        "marker": ["first", "second", "b"],
    })
    kept, removed = dedupe_songs(df)
    assert removed == 1
    assert kept["marker"].tolist() == ["second", "b"]


def test_dedupe_ties_keep_first():
    df = pd.DataFrame({"song_id": ["a", "a"], "danceability": [0.2, 0.2],
                       "marker": ["first", "second"]})
    kept, _ = dedupe_songs(df)
    assert kept["marker"].tolist() == ["first"]
