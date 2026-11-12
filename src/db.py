"""Build the SQLite database from the raw CSV, and run query files against it.

Used by src/03_load_db.py, src/04_export_results.py, src/05_model.py and the tests.
"""
import sqlite3
from pathlib import Path

import pandas as pd

from cleaning import (
    AUDIO_COLS, decade_of, dedupe_songs, drop_bad_rows, flag_still_charting,
    parse_genres, primary_artist,
)

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data" / "raw" / "billboard_hot_100_spotify_audio_features_enriched.csv"
DB_PATH = ROOT / "data" / "billboard.db"
SCHEMA = ROOT / "sql" / "schema.sql"
ANALYSIS_DIR = ROOT / "sql" / "analysis"


def connect(db_path=DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _to_bool_int(value):
    if pd.isna(value):
        return None
    return int(str(value).strip().lower() in ("true", "1"))


def build_tables(raw: pd.DataFrame) -> tuple[dict, dict]:
    """Split the raw rows into the four tables. Returns (tables, report)."""
    report = {"raw rows": len(raw)}
    df, dropped = drop_bad_rows(raw)
    report.update({f"dropped: {k}": v for k, v in dropped.items()})
    df, n_dupes = dedupe_songs(df)
    report["dropped: duplicate song_id"] = n_dupes
    df = df.reset_index(drop=True)
    df["song_key"] = range(1, len(df) + 1)

    df["primary_artist"] = df["performer"].map(primary_artist)
    artists = (pd.DataFrame({"name": sorted(df["primary_artist"].unique())})
               .assign(artist_key=lambda a: range(1, len(a) + 1)))
    df = df.merge(artists, left_on="primary_artist", right_on="name", how="left")

    first = pd.to_datetime(df["first_week"])
    songs = pd.DataFrame({
        "song_key": df["song_key"],
        "song_id": df["song_id"],
        "title": df["song"].astype(str),
        "performer": df["performer"],
        "artist_key": df["artist_key"],
        "peak_position": df["peak_position"].astype(int),
        "weeks_on_chart": df["weeks_on_chart"].astype(int),
        "first_week": first.dt.strftime("%Y-%m-%d"),
        "last_week": pd.to_datetime(df["last_week"]).dt.strftime("%Y-%m-%d"),
        "first_year": first.dt.year,
        "decade": first.map(decade_of),
        "still_charting": df["last_week"].map(flag_still_charting),
    })

    has_audio = df["danceability"].notna()
    a = df[has_audio]
    audio = pd.DataFrame({
        "song_key": a["song_key"],
        "spotify_track_id": a["spotify_track_id"],
        "duration_ms": a["spotify_track_duration_ms"].round().astype("Int64"),
        "explicit": a["spotify_track_explicit"].map(_to_bool_int).astype("Int64"),
        **{("musical_key" if c == "key" else c): a[c] for c in AUDIO_COLS},
    })
    for c in ("musical_key", "mode", "time_signature"):
        audio[c] = audio[c].round().astype("Int64")

    genres = (df[["song_key", "spotify_genre"]]
              .assign(genre=lambda g: g["spotify_genre"].map(parse_genres))
              .explode("genre").dropna(subset=["genre"])[["song_key", "genre"]])

    tables = {
        "artists": artists[["artist_key", "name"]],
        "songs": songs,
        "audio_features": audio,
        "song_genres": genres,
    }
    report.update({f"rows in {k}": len(v) for k, v in tables.items()})
    report["songs with no audio features"] = int((~has_audio).sum())
    report["songs still charting on 2021-05-29"] = int(songs["still_charting"].sum())
    missing = (~has_audio).groupby(songs["decade"]).mean().mul(100).round(1)
    report["missing audio % by decade"] = missing.to_dict()
    return tables, report


def build_database(csv_path=RAW_CSV, db_path=DB_PATH) -> dict:
    """Create (or rebuild) the database. Safe to run any number of times."""
    raw = pd.read_csv(csv_path, low_memory=False)
    tables, report = build_tables(raw)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = connect(db_path)
    try:
        con.executescript(SCHEMA.read_text())  # drops and recreates every table
        for name in ("artists", "songs", "audio_features", "song_genres"):
            tables[name].to_sql(name, con, if_exists="append", index=False)
        con.commit()
        bad = con.execute("PRAGMA foreign_key_check").fetchall()
        if bad:
            raise RuntimeError(f"Foreign key violations: {bad[:5]}")
    finally:
        con.close()
    return report


def run_query(sql_path, db_path=DB_PATH) -> pd.DataFrame:
    """Run one .sql file and return the result as a DataFrame."""
    con = connect(db_path)
    try:
        return pd.read_sql_query(Path(sql_path).read_text(), con)
    finally:
        con.close()


def query_files() -> list[Path]:
    return sorted(ANALYSIS_DIR.glob("*.sql"))
