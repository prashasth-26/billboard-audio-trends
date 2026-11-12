import sqlite3

from conftest import FIXTURE_CSV
from db import build_database


def count(db_path, sql):
    con = sqlite3.connect(db_path)
    try:
        return con.execute(sql).fetchone()[0]
    finally:
        con.close()


def test_row_counts(fixture_db):
    db = fixture_db["path"]
    assert count(db, "SELECT COUNT(*) FROM songs") == 10
    assert count(db, "SELECT COUNT(*) FROM artists") == 6
    assert count(db, "SELECT COUNT(*) FROM audio_features") == 8
    assert count(db, "SELECT COUNT(*) FROM song_genres") == 11


def test_report(fixture_db):
    r = fixture_db["report"]
    assert r["raw rows"] == 14
    assert r["dropped: corrupted (no chart data)"] == 1
    assert r["dropped: unreliable (after 2021-05-29)"] == 1
    assert r["dropped: duplicate song_id"] == 2
    assert r["songs with no audio features"] == 2
    assert r["songs still charting on 2021-05-29"] == 2


def test_bad_rows_are_gone(fixture_db):
    db = fixture_db["path"]
    assert count(db, "SELECT COUNT(*) FROM songs WHERE title = '37623'") == 0
    assert count(db, "SELECT COUNT(*) FROM songs WHERE last_week > '2021-05-29'") == 0


def test_duplicate_kept_the_row_with_audio(fixture_db):
    db = fixture_db["path"]
    assert count(db, """SELECT a.danceability FROM songs s
                        JOIN audio_features a USING (song_key)
                        WHERE s.title = 'Kappa'""") == 0.9


def test_no_duplicate_keys(fixture_db):
    db = fixture_db["path"]
    assert count(db, "SELECT COUNT(*) - COUNT(DISTINCT song_key) FROM songs") == 0
    assert count(db, "SELECT COUNT(*) - COUNT(DISTINCT song_id) FROM songs") == 0


def test_no_orphaned_foreign_keys(fixture_db):
    con = sqlite3.connect(fixture_db["path"])
    try:
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        con.close()


def test_primary_artist_assigned(fixture_db):
    db = fixture_db["path"]
    sql = """SELECT ar.name FROM songs s JOIN artists ar USING (artist_key)
             WHERE s.title = '{}'"""
    con = sqlite3.connect(db)
    try:
        assert con.execute(sql.format("Beta")).fetchone()[0] == "Ann Lee"
        assert con.execute(sql.format("Theta")).fetchone()[0] == "Eve"
        assert con.execute(sql.format("Epsilon")).fetchone()[0] == "Dee & Dum"
    finally:
        con.close()


def test_reload_is_idempotent(tmp_path):
    db = tmp_path / "twice.db"
    first = build_database(FIXTURE_CSV, db)
    second = build_database(FIXTURE_CSV, db)
    assert first == second
    assert count(db, "SELECT COUNT(*) FROM songs") == 10
    assert count(db, "SELECT COUNT(*) FROM song_genres") == 11
