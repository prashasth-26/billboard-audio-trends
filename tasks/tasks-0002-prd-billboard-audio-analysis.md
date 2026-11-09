## Relevant Files

- `tasks/0002-prd-billboard-audio-analysis.md` - The PRD this task list implements.
- `src/00_download.py` - Downloads the dataset into `data/raw/` (exists).
- `src/01_inspect.py` - Prints the structure of each raw CSV (exists).
- `src/02_check_coverage.py` - Audio-feature coverage by decade, duplicate IDs, latest `last_week` values, peak-position distribution (exists).
- `sql/schema.sql` - Table definitions with primary and foreign keys (to be created).
- `src/03_load_db.py` - Cleans the raw CSV and loads it idempotently into `data/billboard.db` (to be created).
- `src/cleaning.py` - Helper functions used by the loader: genre parsing, duplicate grouping, `still_charting` rule, primary-artist parsing (to be created).
- `sql/analysis/01_longevity_by_decade.sql` through `sql/analysis/08_*.sql` - At least 8 documented queries, written by the author (to be created).
- `src/04_export_results.py` - Runs the queries and writes CSVs to `data/exports/` for Tableau (to be created).
- `src/05_model.py` - Prediction model: target, time-based split, baseline comparison, feature importance (to be created).
- `tests/conftest.py` - Shared fixtures: builds a throwaway database from the fixture CSV (to be created).
- `tests/test_cleaning.py` - Unit tests for the helper functions in `src/cleaning.py` (to be created).
- `tests/test_load_db.py` - Tests for the loader: row counts, keys, idempotent re-load (to be created).
- `tests/test_queries.py` - Tests for each query against the fixture (to be created).
- `tests/test_model.py` - Tests for the target definition, the time split and the excluded-column rule (to be created).
- `tests/fixtures/mini_billboard.csv` - Small hand-built CSV with known correct answers (to be created).
- `README.md` - Question, method, results, limitations, setup (exists as a skeleton; commands need `python3`).
- `requirements.txt` - Dependencies, to be pinned once the code works (exists, unpinned; update to pandas, scikit-learn, pytest, kagglehub).
- `.gitignore` - Keeps `data/` out of git (exists).

### Notes

- Run every Python command with `python3`, not `python`.
- Tests live in `tests/`, one file per module. Run them with `pytest` from the repository root. The PRD does not call for Docker, so tests run directly.
- You write the SQL queries (4.0) and choose the questions, thresholds and model settings. Scaffolding (schema, loader, tests, README skeleton) may be generated. You must be able to explain every query in an interview.
- Priorities from the PRD: 1.0-4.0, 7.0 and 8.0 are Must; 5.0 (Tableau) is Should; 6.0 (model) is Could and is cut first if time runs short.
- Decisions already made: SQLite; schema split into `songs`, `audio_features`, `song_genres` (artists table optional); model target is peak position top 5 (11.9%); `still_charting` = `last_week` within 28 days of the latest `last_week`; the 3 corrupted rows are dropped.
- Raw data stays in `data/` and is never committed.
- Commit after each parent task, on the feature branch.

## Tasks

- [ ] 1.0 Set up the git repository, worktree and branch (`billboard-audio-analysis-wt`, `feature/billboard-audio-analysis`)
  - [ ] 1.1 In `/Users/prashastht/Desktop/Career/PersonalProject`, run `git init`, confirm `.gitignore` contains `data/`, and make a first commit on `main` with the existing scripts, README skeleton, `requirements.txt` and `tasks/`.
  - [ ] 1.2 Create the worktree and branch: `git worktree add ../billboard-audio-analysis-wt -b feature/billboard-audio-analysis`. Do all later work in the worktree folder.
  - [ ] 1.3 In the worktree, create a virtual environment (`python3 -m venv .venv`), activate it, and install `pandas`, `scikit-learn`, `pytest` and `kagglehub`. Update `requirements.txt` to list them.
  - [ ] 1.4 Create the empty folders `sql/analysis/`, `tests/fixtures/`, `src/`, and re-run `python3 src/00_download.py` in the worktree so `data/raw/` exists there (it is git-ignored, so it does not carry over).
  - [ ] 1.5 Verify: `git status` is clean on the feature branch, `git worktree list` shows both folders, `data/` does not appear in `git status`, and `python3 src/01_inspect.py` runs.

- [ ] 2.0 Close the open data questions before designing the schema (PRD Section 10)
  - [x] 2.1 Run the coverage checks (`src/02_check_coverage.py`) and record the results in the PRD. (Done: missing audio by decade, duplicate IDs, last_week spread, peak distribution.)
  - [x] 2.2 Check the dataset license on the Kaggle page. (Done: CC0 Public Domain.)
  - [x] 2.3 Decide the model threshold, database and schema. (Done: top 5, SQLite, three-table split.)
  - [ ] 2.4 Find out which columns differ between the rows that share a `song_id`: write a short script (`src/02b_check_duplicates.py`) that, for each shared ID, lists which of the 33 columns differ, and counts the three groups from PRD requirement 8a.
  - [ ] 2.5 Pick a rule for each duplicate group (keep one when identical; keep one when only Spotify or generated columns differ; treat as separate chart runs when chart fields differ). Write the rules into the PRD as a short table.
  - [ ] 2.6 Check `weeks_on_chart` for 3 well-known songs (for example "Blinding Lights", "All I Want for Christmas Is You", one older song) against Billboard's own site. Record whether the file matches in the PRD.
  - [ ] 2.7 Count how many songs the 28-day `still_charting` rule flags, and how many at 14 and 56 days. Record the three numbers in the PRD.
  - [ ] 2.8 Test: re-run `02_check_coverage.py` and `02b_check_duplicates.py` from a clean shell and confirm the numbers in the PRD match the output.

- [ ] 3.0 Design the schema and build the SQLite loader with tests (PRD requirements 5-8c, 15-16)
  - [ ] 3.1 Write `sql/schema.sql` with `songs`, `audio_features`, `song_genres` (optionally `artists`), using an integer `song_key` primary key and foreign keys back to `songs`. Add a comment above each table saying what one row means.
  - [ ] 3.2 Write `src/cleaning.py` with small functions: `parse_genres(text)` (turns `"['pop', 'dance pop']"` into a list, handles null), `flag_still_charting(last_week, latest, days=28)`, `decade_of(date)`, and `primary_artist(performer)` (documented rule for "Featuring", "&", "With", "x", commas).
  - [ ] 3.3 Write `src/03_load_db.py`: read the raw CSV, drop the 3 corrupted rows, apply the duplicate rules from 2.5, create `song_key`, split into the three tables, and write `data/billboard.db`.
  - [ ] 3.4 Make the load safe to re-run: delete and rebuild the tables (or use `INSERT OR REPLACE`), so running it twice gives the same row counts.
  - [ ] 3.5 Make the loader print a report: rows in the raw file, rows dropped (with reasons), rows per table, songs with no audio features, and missing-audio share by decade.
  - [ ] 3.6 Build `tests/fixtures/mini_billboard.csv` by hand: about 15 rows with known answers, including one identical duplicate, one duplicate with different chart fields, one corrupted row, one song with no audio features, one still-charting song, and songs in at least three decades.
  - [ ] 3.7 Write `tests/conftest.py` (builds a temporary database from the fixture) and `tests/test_cleaning.py` (genre parsing, `still_charting`, decade, primary artist).
  - [ ] 3.8 Write `tests/test_load_db.py`: expected row count per table, no duplicate primary keys, no orphaned foreign keys (`PRAGMA foreign_key_check`), loading twice gives identical counts, corrupted row is absent.
  - [ ] 3.9 Run `pytest` and the loader on the real data; confirm the report matches the numbers in the PRD. Commit.

- [ ] 4.0 Write the SQL analysis queries (author-written) and export results to CSV (PRD requirements 9-14, 17)
  - [ ] 4.1 Write `sql/analysis/01_longevity_by_decade.sql`: songs, average and median-ish weeks on chart by decade of `first_week`, excluding or flagging `still_charting` songs, with the song count per decade.
  - [ ] 4.2 Write `02_audio_features_by_decade.sql`: average of each audio feature by decade for songs with audio features, plus the number of songs used and the missing-audio share.
  - [ ] 4.3 Write `03_features_top5_vs_rest.sql`: join `songs` to `audio_features`; compare average features for peak <= 5 versus the rest, with counts. Add a #1 versus rest version.
  - [ ] 4.4 Write `04_yearly_feature_change.sql`: yearly averages in a CTE, then `LAG` for year-over-year change in danceability (or energy).
  - [ ] 4.5 Write `05_rank_decades_by_feature.sql`: `RANK` the decades by average energy, valence and danceability.
  - [ ] 4.6 Write `06_top_genres_by_decade.sql`: join `song_genres` to `songs`; `RANK` genres within each decade (`PARTITION BY decade`) and keep the top 5.
  - [ ] 4.7 Write `07_artist_concentration.sql` (Should): share of songs held by the top 10 primary artists per decade, using the `artists` table or the parsed primary artist.
  - [ ] 4.8 Write `08_explicit_share_by_decade.sql`: share of explicit songs per decade with a running comparison to the previous decade (`LAG`).
  - [ ] 4.9 At the top of each file, add a comment: the question, which tables it joins, and the caveat (for example missing audio in early decades).
  - [ ] 4.10 Write `src/04_export_results.py`: run each query file against `data/billboard.db` and save a CSV per query in `data/exports/`.
  - [ ] 4.11 Write `tests/test_queries.py`: run every query against the fixture database and assert the exact expected values you worked out by hand in 3.6; also assert each file exists and returns at least one row.
  - [ ] 4.12 Run `pytest` and `python3 src/04_export_results.py`; open two exported CSVs and sanity-check them. Commit.

- [ ] 5.0 Build the Tableau Public dashboard, 1-3 views, from the exported CSVs (PRD requirements 18-19)
  - [ ] 5.1 Install Tableau Public (free) and create an account.
  - [ ] 5.2 Connect to the exported CSVs from 4.10 (text/CSV connector).
  - [ ] 5.3 Build view 1: a line chart of audio features by decade (for example danceability, energy, valence), with song count shown in the tooltip.
  - [ ] 5.4 Build view 2 (optional): weeks on chart by decade, or the top genres by decade.
  - [ ] 5.5 Add a text note on the dashboard that audio data is missing for about 35% of 1950s songs and 24% of 1960s songs.
  - [ ] 5.6 Publish to Tableau Public, copy the link, and check it opens while logged out.
  - [ ] 5.7 Test: confirm 2 numbers on the dashboard match the CSV and the database. Save a screenshot to `docs/dashboard.png` for the README.

- [ ] 6.0 Build and evaluate the prediction model (PRD requirements 20-25)
  - [ ] 6.1 In `src/05_model.py`, define constants: `TOP_N = 5`, the list of audio feature columns, and the list of excluded columns from PRD requirement 21.
  - [ ] 6.2 Load rows with audio features from the database, build the target (`peak_position <= TOP_N`), print the class balance and the number of rows excluded for missing audio.
  - [ ] 6.3 Split by time: train on songs with `first_week` before a cutoff year, test on songs after it; exclude `still_charting` songs from the test set and print how many.
  - [ ] 6.4 Fit a majority-class baseline, a logistic regression (scaled features) and a random forest or gradient boosting model.
  - [ ] 6.5 Report accuracy, ROC AUC and the baseline for each model on the test set. If the models do not beat the baseline, print that plainly.
  - [ ] 6.6 Report logistic coefficients and permutation importance on the test set, and write one sentence per result describing it as association.
  - [ ] 6.7 Write `tests/test_model.py`: target is built correctly from known peaks, the time split has no overlap and the test set is later than the train set, and no excluded column appears in the feature list.
  - [ ] 6.8 Run `pytest` and `python3 src/05_model.py`; save the printed results to `docs/model_results.txt`. Commit.

- [ ] 7.0 Write the README and prepare the public release (PRD requirements 26-28)
  - [ ] 7.1 Write the README: the question, dataset (with Kaggle link and CC0 credit), method (schema diagram or table list, cleaning rules), results (each with its song count), dashboard link, model results, and limitations.
  - [ ] 7.2 State the limitations plainly: no weekly data, only charted songs, missing audio in early decades, generated columns excluded, `weeks_on_chart` check result, association not cause.
  - [ ] 7.3 Write setup steps using `python3`: create the venv, install, download, load, query, test, model.
  - [ ] 7.4 Pin the versions in `requirements.txt` (`pip freeze` for the five libraries you use).
  - [ ] 7.5 Confirm `data/` is ignored and no raw or database file is tracked (`git ls-files | grep data`).
  - [ ] 7.6 Create the public GitHub repository, push `main` and the feature branch, and open a pull request to merge the feature branch.
  - [ ] 7.7 Test: clone the public repo into a fresh folder and follow the README exactly; fix any step that fails.

- [ ] 8.0 Final integration and end-to-end testing
  - [ ] 8.1 From a fresh clone and a new virtual environment, run the full chain: `python3 src/00_download.py`, `python3 src/03_load_db.py`, `python3 src/04_export_results.py`, `python3 src/05_model.py`.
  - [ ] 8.2 Run `pytest` and confirm every test passes with one command.
  - [ ] 8.3 Check every number in the README against the database or the exported CSVs.
  - [ ] 8.4 Check that the dashboard link works and the screenshot matches the live version.
  - [ ] 8.5 Confirm the repository is public, the raw data is not in it, and the README mentions CC0 and the Kaggle source.
  - [ ] 8.6 Write the resume bullet from what was actually built (SQL with SQLite, CTEs, window functions, pytest, Tableau, scikit-learn), and add the repo and dashboard links.
