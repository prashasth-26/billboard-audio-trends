# What Hits Sound Like: 63 Years of the Billboard Hot 100 in SQL

A SQLite database and SQL analysis of 29,383 songs that charted on the Billboard
Hot 100 between August 1958 and May 2021, joined with Spotify audio features
(danceability, energy, valence and so on). Results feed a Tableau Public
dashboard and a simple model of which audio features go with reaching the top 5.

**Skills:** SQL (SQLite: joins, CTEs, window functions `LAG`, `RANK`, `ROW_NUMBER`),
relational schema design, Python (pandas), pytest, scikit-learn, Tableau Public.

**Dashboard:** _link to be added after publishing (see `docs/tableau.md`)_

## Questions

1. How long do songs stay on the chart, and has that changed by decade?
2. How has the sound of charting songs changed (danceability, energy, valence, loudness, tempo, length)?
3. Do songs that reached the top 5 sound different from songs that peaked lower?
4. How concentrated is the chart in a few artists, and how has that changed?
5. Which genres dominated each decade, and how common are explicit lyrics?

## Findings

Every figure below states how many songs it rests on. Full results are in
`data/exports/` after running the pipeline.

- **Songs stayed on the chart longer through the 2000s, then less.** Average weeks on
  chart rose from 7.6 for songs debuting in the 1960s (6,850 songs) to 15.4 in the 2000s
  (3,418), then fell to 11.7 in the 2010s (4,442). Only 0.8% of 1960s songs lasted 20+
  weeks, against 42.6% in the 2000s. The longest run is "Radioactive" (87 weeks).
- **Hits got more danceable and much less acoustic, and less happy.** Among songs with
  audio features, average danceability rose from 0.53 (1960s, 5,222 songs) to 0.64
  (2010s, 4,175); acousticness fell from 0.53 to 0.18; valence (musical positiveness)
  fell from 0.66 to 0.48. Songs got louder (-10.4 dB to -6.0 dB) and, after peaking at
  4.4 minutes in the 1990s, shorter again (3.7 minutes in the 2010s).
- **Explicit songs went from almost none to the majority.** 0.3% of 1980s songs with a
  Spotify flag are explicit, 10.8% in the 1990s, 38.3% in the 2010s and 56.2% in
  2020-21 (580 songs).
- **The chart became more concentrated recently.** The 10 busiest artists of each decade
  account for 4.6-7.0% of songs from the 1970s to the 2000s, but 15.2% in the 2010s
  and 25.7% in 2020-21 (913 songs; Taylor Swift alone has 40).
- **Top-5 songs differ only slightly in sound.** Songs that reached #1-#5 (2,703 with
  features) are a little more danceable (0.62 vs 0.60) and positive (0.63 vs 0.60) than
  songs that peaked #6-#100 (21,521).
- **Sound alone is a weak predictor of a top-5 peak.** Trained on 1958-2009 songs and tested
  on 2010-2021 songs, logistic regression reaches ROC AUC 0.63 and a random forest about 0.6,
  against 0.50 for guessing (the random forest's exact score varies a little between
  scikit-learn versions). Danceability is the strongest association. See
  `docs/model_results.txt`.

## Data

Source: [Billboard Hot 100 + Spotify Audio Features](https://www.kaggle.com/datasets/luthfimuthathohirin/billboard-hot-100-spotify-audio-features)
on Kaggle, licensed CC0 (public domain). One CSV, 32,503 rows x 33 columns, one row per song.
The raw data is not included in this repository; `src/00_download.py` fetches it.

### Cleaning

| Step | Rows | Rule |
|---|---:|---|
| Raw file | 32,503 | |
| Corrupted rows dropped | 3 | No chart data; garbled titles or performers (e.g. title "37623") |
| Unreliable rows dropped | 3,000 | The last 3,000 rows (see below) |
| Duplicate song IDs merged | 117 | 117 IDs appear twice: 24 identical pairs, 93 differing only in Spotify fields. Kept the row with audio features, else the first |
| **Songs loaded** | **29,383** | |

**Why 3,000 rows were dropped.** The dataset's version 3 update (October 2026) added 3,000 songs
described as chart issues from June 2021 to October 2026. Those rows fail checks the other 29,500 pass,
so the analysis stops at the last chart week before them, 2021-05-29:

- Billboard issue dates are Saturdays. All 29,500 original rows start on a Saturday; the added rows
  start on all seven weekdays, about 14% each.
- Many titles carry labels such as "Kill Bill (Version 1057)".
- Some songs appear twice with conflicting peaks and dates (for example "Deja Vu" at #8 in 2021 and
  #1 in 2024), but a song has one peak.
- None of the added rows is missing audio features, against 17.5% of the original rows, and 28% of them
  reach the top 5, against 10%.

I could not tell whether the rows were generated or real data scrambled during assembly; either way
they are not reliable. The analysis covers chart weeks from 1958-08-02 to 2021-05-29.

**Checked against Billboard.** `weeks_on_chart` matches Billboard for "Radioactive" (87) and
for "Blinding Lights" as of 2021-05-29 (76; it reached 88 later in 2021).

**Not used:** seven columns the Kaggle page describes as generated enrichment labels
(`chart_success_tier`, `hit_longevity_profile`, `acoustic_mood_cluster`, `musical_era`,
`evidence_span`, `cot_rationale`, `confidence_score`), and `spotify_track_popularity`, which
reflects today's streaming rather than the song itself.

## Method

### Schema

The flat file is split into four tables (`sql/schema.sql`):

```
artists ──< songs ──< song_genres
              │
              └──── audio_features   (0 or 1 row per song)
```

- `songs` (29,383): title, performer, peak position, weeks on chart, first and last chart
  week, decade, and a `still_charting` flag for the 99 songs on the final chart.
- `audio_features` (24,224): one row per song that has Spotify features.
- `song_genres` (128,671): one row per song-genre pair, parsed from Spotify's genre list.
- `artists` (8,089): the lead act in each credit, before "Featuring" or "With".

Genres are a real one-to-many relationship, which is the main reason to split the table.
Songs without features have no `audio_features` row, so queries use `LEFT JOIN` when
they need to count the missing ones.

### Queries (`sql/analysis/`)

| File | Question | Techniques |
|---|---|---|
| `01_longevity_by_decade.sql` | Weeks on chart by decade | `GROUP BY`, `CASE`, `NULLIF` |
| `02_audio_features_by_decade.sql` | Sound by decade, with missing-data share | `LEFT JOIN`, aggregates |
| `03_features_by_peak_group.sql` | #1 vs #2-5 vs #6-100 | `JOIN`, `CASE` groups |
| `04_yearly_danceability_change.sql` | Year-over-year change | CTE, `LAG` |
| `05_rank_decades_by_feature.sql` | Rank decades by feature | CTE, `RANK` |
| `06_top_genres_by_decade.sql` | Top 5 genres per decade | CTEs, `RANK ... PARTITION BY` |
| `07_artist_concentration.sql` | Share of songs by top 10 artists | CTEs, `ROW_NUMBER`, windowed `SUM` |
| `08_explicit_share_by_decade.sql` | Explicit share and change | CTE, `LAG` |

The SQL avoids SQLite-only features, so it should also run on PostgreSQL.

### Model (`src/05_model.py`)

- Target: peaked at #5 or better (10% of songs).
- Inputs: the 12 Spotify audio features plus duration and the explicit flag. No chart
  results or columns derived from them.
- Split by time: train on 1958-2009 (19,465 songs), test on 2010-2021 (4,694 songs,
  excluding 61 still charting, whose peak could still rise).
- Compared with a baseline that always predicts "not top 5". Because about 94% of test
  songs are not top 5, that baseline already scores 94% accuracy, so ROC AUC is the main metric.
- Feature importance from logistic regression coefficients and permutation importance.

## Limitations

- **Only songs that charted.** The model compares big hits with smaller hits, not hits with
  songs that never charted. It cannot pick hits from all released music.
- **No weekly chart data.** Only peak, total weeks and first and last week are available, so
  there is no week-by-week movement.
- **Missing audio features** for 17.5% of songs, concentrated in the 1950s (35%), 1960s (24%)
  and 2020-21 (36%). Averages for those decades rest on fewer songs.
- **Spotify measures today's version.** Genres are tagged per artist with current labels, and
  the explicit flag reflects the version on Spotify, not necessarily the charting edit.
- **Holiday songs** return each December, so their weeks on chart add up across years.
- **Associations, not causes.** Nothing here shows that a feature makes a song succeed.
- **2020-21 is a partial decade** (913 songs, through May 2021).

## Run it

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/00_download.py         # download the Kaggle CSV into data/raw/
python3 src/03_load_db.py          # build data/billboard.db and print a cleaning report
python3 src/04_export_results.py   # run every query, save CSVs to data/exports/
python3 src/05_model.py            # fit and evaluate the model
pytest                             # 40 tests against a small hand-built fixture
```

Optional checks: `python3 src/01_inspect.py` (column summary), `python3 src/02_check_coverage.py`
and `python3 src/02b_check_duplicates.py` (the data checks behind the cleaning rules).

## Layout

```
src/        scripts (00-05) plus cleaning.py, db.py, model.py
sql/        schema.sql and analysis/ (8 queries)
tests/      pytest tests and fixtures/mini_billboard.csv
docs/       model results and the Tableau guide
tasks/      the PRD and task list for this project
data/       raw data, database and exports (git-ignored)
```
