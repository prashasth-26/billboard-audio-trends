"""Each query in sql/analysis/ is run against the fixture database, and the
results are compared with answers worked out by hand (see tests/conftest.py
for what the fixture contains)."""
import math

import pytest

from db import ANALYSIS_DIR, query_files, run_query


def q(fixture_db, name):
    return run_query(ANALYSIS_DIR / name, fixture_db["path"])


def row(df, **match):
    sel = df
    for col, val in match.items():
        sel = sel[sel[col] == val]
    assert len(sel) == 1, f"expected one row for {match}, got {len(sel)}"
    return sel.iloc[0]


def test_there_are_at_least_8_queries():
    assert len(query_files()) >= 8


@pytest.mark.parametrize("path", query_files(), ids=lambda p: p.name)
def test_every_query_runs_and_returns_rows(fixture_db, path):
    assert len(run_query(path, fixture_db["path"])) > 0


def test_q1_longevity(fixture_db):
    df = q(fixture_db, "01_longevity_by_decade.sql")
    r = row(df, decade=1960)
    assert (r.songs, r.max_weeks_on_chart) == (3, 9)
    assert r.avg_weeks_on_chart == pytest.approx(5.7)      # (9 + 5 + 3) / 3
    assert r.pct_20_plus_weeks == 0
    r = row(df, decade=1970)
    assert r.avg_weeks_on_chart == pytest.approx(10.3)     # (20 + 10 + 1) / 3
    assert r.pct_20_plus_weeks == pytest.approx(33.3)
    r = row(df, decade=2020)                               # both still charting
    assert r.songs_still_charting == 2
    assert r.avg_weeks_on_chart is None or math.isnan(r.avg_weeks_on_chart)


def test_q2_audio_by_decade(fixture_db):
    df = q(fixture_db, "02_audio_features_by_decade.sql")
    r = row(df, decade=1960)
    assert (r.songs, r.songs_with_audio) == (3, 2)
    assert r.pct_missing_audio == pytest.approx(33.3)
    assert r.avg_danceability == pytest.approx(0.4)        # (0.5 + 0.3) / 2
    assert r.avg_valence == pytest.approx(0.7)
    r = row(df, decade=1980)
    assert r.pct_missing_audio == 0


def test_q3_peak_groups(fixture_db):
    df = q(fixture_db, "03_features_by_peak_group.sql")
    assert row(df, peak_group="1: #1").songs == 1
    r = row(df, peak_group="2: #2-5")
    assert r.songs == 2 and r.avg_danceability == pytest.approx(0.7)
    r = row(df, peak_group="3: #6-100")
    assert r.songs == 5 and r.avg_danceability == pytest.approx(0.56)


def test_q4_lag_by_year(fixture_db):
    df = q(fixture_db, "04_yearly_danceability_change.sql")
    assert len(df) == 8
    assert math.isnan(row(df, year=1965).change_from_prev_year)
    assert row(df, year=1968).change_from_prev_year == pytest.approx(-0.2)
    assert row(df, year=1975).change_from_prev_year == pytest.approx(0.3)


def test_q5_rank_decades(fixture_db):
    df = q(fixture_db, "05_rank_decades_by_feature.sql")
    ranks = dict(zip(df.decade, df.danceability_rank))
    assert ranks == {1980: 1, 2010: 2, 2020: 3, 1970: 4, 1960: 5}


def test_q6_top_genres(fixture_db):
    df = q(fixture_db, "06_top_genres_by_decade.sql")
    assert row(df, decade=1960, genre="pop").genre_rank == 1
    assert row(df, decade=1960, genre="soul").genre_rank == 2
    assert row(df, decade=1970, genre="rock").songs == 2
    # a tie: both 2010s genres share rank 1
    assert set(df[df.decade == 2010].genre_rank) == {1}


def test_q7_artist_concentration(fixture_db):
    df = q(fixture_db, "07_artist_concentration.sql")
    r = row(df, decade=1960)
    assert (r.songs, r.songs_by_top_10, r.busiest_artist) == (3, 3, "Ann Lee")
    assert r.pct_songs_by_top_10 == 100
    assert row(df, decade=2020).busiest_artist == "Eve"     # tie broken alphabetically


def test_q8_explicit_share(fixture_db):
    df = q(fixture_db, "08_explicit_share_by_decade.sql")
    assert row(df, decade=1960).pct_explicit == 0
    assert row(df, decade=2010).pct_explicit == 100
    r = row(df, decade=2020)
    assert r.pct_explicit == 50 and r.change_from_prev_decade == -50
