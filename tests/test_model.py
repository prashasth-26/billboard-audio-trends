import pandas as pd

from model import EXCLUDED, FEATURES, MODEL_QUERY, add_target, time_split


def test_target_uses_top_5():
    df = pd.DataFrame({"peak_position": [1, 5, 6, 100]})
    assert add_target(df, top_n=5)["top_n_hit"].tolist() == [1, 1, 0, 0]


def test_time_split_has_no_overlap_and_test_is_later():
    df = pd.DataFrame({
        "first_year": [1990, 2005, 2009, 2010, 2015, 2021],
        "still_charting": [0, 0, 0, 0, 0, 1],
    })
    train, test, dropped = time_split(df, split_year=2010)
    assert train["first_year"].max() < test["first_year"].min()
    assert set(train.index).isdisjoint(test.index)
    assert len(train) == 3 and len(test) == 2


def test_time_split_drops_still_charting_from_test():
    df = pd.DataFrame({"first_year": [2015, 2021, 2021], "still_charting": [0, 1, 1]})
    _, test, dropped = time_split(df, split_year=2010)
    assert dropped == 2
    assert test["still_charting"].sum() == 0


def test_no_excluded_column_is_a_feature():
    assert set(FEATURES).isdisjoint(EXCLUDED)


def test_model_query_runs_on_fixture(fixture_db):
    from db import connect

    con = connect(fixture_db["path"])
    df = pd.read_sql_query(MODEL_QUERY, con)
    con.close()
    assert len(df) == 8                       # the 8 fixture songs with audio features
    assert set(FEATURES) <= set(df.columns)
    assert "spotify_track_popularity" not in df.columns
