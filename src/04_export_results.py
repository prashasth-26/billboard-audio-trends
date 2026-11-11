"""Run every query in sql/analysis/ and save each result as a CSV in data/exports/.

Tableau Public reads files, not databases, so these CSVs feed the dashboard.

Run from the project root (after src/03_load_db.py):  python3 src/04_export_results.py
"""
from db import DB_PATH, ROOT, query_files, run_query

EXPORT_DIR = ROOT / "data" / "exports"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("data/billboard.db not found. Run python3 src/03_load_db.py first.")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for sql_file in query_files():
        result = run_query(sql_file)
        out = EXPORT_DIR / f"{sql_file.stem}.csv"
        result.to_csv(out, index=False)
        print(f"{sql_file.name:40s} {len(result):>4} rows -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
