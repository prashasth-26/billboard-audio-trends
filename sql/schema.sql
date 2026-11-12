-- Schema for the Billboard Hot 100 + Spotify audio features database (SQLite).
--
-- The Kaggle file is one wide table. It is split into four tables so that each
-- fact is stored once and the tables are linked by keys:
--
--   artists ──< songs ──< song_genres
--                 │
--                 └──── audio_features   (0 or 1 row per song)
--
-- Re-running this file drops and recreates every table, which is what makes
-- the loader safe to run twice.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS song_genres;
DROP TABLE IF EXISTS audio_features;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS artists;

-- One row per primary artist: the first name in the performer credit, before
-- "Featuring" or "With" (see src/cleaning.py, primary_artist).
CREATE TABLE artists (
    artist_key  INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL UNIQUE
);

-- One row per song that charted on the Hot 100 between 1958-08-02 and
-- 2021-05-29. song_key is our own integer key; song_id is Kaggle's text ID
-- (title and performer joined with no separator), kept for traceability.
CREATE TABLE songs (
    song_key        INTEGER PRIMARY KEY,
    song_id         TEXT    NOT NULL UNIQUE,
    title           TEXT    NOT NULL,
    performer       TEXT    NOT NULL,          -- full credit, e.g. "X Featuring Y"
    artist_key      INTEGER NOT NULL REFERENCES artists (artist_key),
    peak_position   INTEGER NOT NULL CHECK (peak_position BETWEEN 1 AND 100),
    weeks_on_chart  INTEGER NOT NULL CHECK (weeks_on_chart >= 1),
    first_week      TEXT    NOT NULL,          -- ISO date, YYYY-MM-DD
    last_week       TEXT    NOT NULL,          -- ISO date, YYYY-MM-DD
    first_year      INTEGER NOT NULL,          -- year of first_week
    decade          INTEGER NOT NULL,          -- e.g. 1980 for 1980-1989
    still_charting  INTEGER NOT NULL CHECK (still_charting IN (0, 1))
                    -- 1 if on the final chart (2021-05-29): weeks_on_chart is incomplete
);

-- One row per song that has Spotify audio features (about 82% of songs).
-- Songs without features simply have no row here, so use a LEFT JOIN from
-- songs when you need to count the missing ones.
CREATE TABLE audio_features (
    song_key          INTEGER PRIMARY KEY REFERENCES songs (song_key),
    spotify_track_id  TEXT,
    duration_ms       INTEGER,
    explicit          INTEGER CHECK (explicit IN (0, 1)),
    danceability      REAL,   -- 0-1
    energy            REAL,   -- 0-1
    musical_key       INTEGER, -- 0 = C, 1 = C#/Db, ... 11 = B
    loudness          REAL,   -- decibels, usually -60 to 0
    mode              INTEGER, -- 1 = major, 0 = minor
    speechiness       REAL,   -- 0-1
    acousticness      REAL,   -- 0-1
    instrumentalness  REAL,   -- 0-1
    liveness          REAL,   -- 0-1
    valence           REAL,   -- 0-1, musical "positiveness"
    tempo             REAL,   -- beats per minute
    time_signature    INTEGER
);

-- One row per song-genre pair. Spotify assigns genres to artists, not songs,
-- so these are the genres of the song's artist. A song can have many genres.
CREATE TABLE song_genres (
    song_key  INTEGER NOT NULL REFERENCES songs (song_key),
    genre     TEXT    NOT NULL,
    PRIMARY KEY (song_key, genre)
);

CREATE INDEX idx_songs_decade      ON songs (decade);
CREATE INDEX idx_songs_first_year  ON songs (first_year);
CREATE INDEX idx_song_genres_genre ON song_genres (genre);
