## Relevant Files

_Preliminary list. The folder currently holds the scaffolding and the PRD. Everything marked "to be created" does not exist yet. The list will be finalized with the sub-tasks._

- `tasks/0002-prd-billboard-audio-analysis.md` - The PRD this task list implements.
- `src/00_download.py` - Downloads the dataset into `data/raw/` (exists).
- `src/01_inspect.py` - Prints the structure of each raw CSV (exists).
- `src/02_check_coverage.py` - Answers the open data questions: audio-feature coverage by decade, duplicate IDs, latest `last_week` values, peak-position distribution (exists).
- `sql/schema.sql` - Table definitions with primary and foreign keys (to be created).
- `src/03_load_db.py` - Cleans the raw CSV and loads it idempotently into `data/billboard.db` (to be created).
- `sql/analysis/*.sql` - At least 8 documented queries. Written by the author (to be created).
- `src/04_export_results.py` - Runs the queries and writes CSVs to `data/exports/` for Tableau (to be created).
- `src/05_model.py` - Prediction model: target, time-based split, baseline comparison, feature importance (to be created).
- `tests/test_load_db.py` - Tests for the loader: row counts, keys, idempotent re-load (to be created).
- `tests/test_queries.py` - Tests for each query against a small hand-built fixture (to be created).
- `tests/test_model.py` - Tests for the target definition, the time split and the excluded-column rule (to be created).
- `tests/fixtures/` - Small hand-built CSV with known correct answers (to be created).
- `README.md` - Question, method, results, limitations, setup (exists as a skeleton).
- `requirements.txt` - Dependencies, to be pinned once the code works (exists, unpinned).
- `.gitignore` - Keeps `data/` out of git (exists).

### Notes

- Unit tests live in `tests/`, one test file per module. Run them with `pytest` from the repository root.
- The PRD does not call for Docker, so tests run directly rather than in Docker. Add a Docker task if you want that.
- SQL queries in `sql/analysis/`, and the choice of questions, thresholds and model, are written by the author. Scaffolding may be generated.
- Priorities from the PRD: tasks 1.0-4.0, 7.0 and 8.0 are Must; 5.0 (Tableau) is Should; 6.0 (model) is Could and is cut first if time runs short.
- Raw data stays in `data/` and is never committed.

## Tasks

- [ ] 1.0 Set up the git repository, worktree and branch (`billboard-audio-analysis-wt`, `feature/billboard-audio-analysis`)
- [ ] 2.0 Close the open data questions before designing the schema: license and provenance (Kaggle page, author task), audio-feature coverage by decade, duplicate `song_id` rows, the `still_charting` rule, and the peak-position threshold (PRD Section 10, items 1, 5, 6)
- [ ] 3.0 Design the schema and build the SQLite loader with tests: split the flat table, parse genres, handle duplicates and missing data, idempotent re-load (PRD requirements 5-8c, 15-16)
- [ ] 4.0 Write the SQL analysis queries (author-written) and export results to CSV: longevity, concentration, audio features over time, features vs. chart peak; at least 8 documented queries (PRD requirements 9-14, 17)
- [ ] 5.0 Build the Tableau Public dashboard, 1-3 views, from the exported CSVs (PRD requirements 18-19)
- [ ] 6.0 Build and evaluate the prediction model: target from `peak_position`, audio features only, time-based split, majority-class baseline, feature importance (PRD requirements 20-25)
- [ ] 7.0 Write the README and prepare the public release: findings, limitations, pinned requirements, license check (PRD requirements 26-28)
- [ ] 8.0 Final integration and end-to-end testing: rebuild from scratch, full `pytest` run, check every README number against the database, confirm raw data is excluded from the repository
