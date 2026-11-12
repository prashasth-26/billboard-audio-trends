"""Print a structural summary of every CSV in data/raw/.

Makes no assumptions about column names. Paste the output back into chat
so the schema can be designed from what is actually in the files.

Run from the project root:  python3 src/01_inspect.py
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def summarize(path: Path) -> None:
    df = pd.read_csv(path, low_memory=False)
    print("=" * 78)
    print(f"{path.relative_to(RAW_DIR)}  ->  {len(df):,} rows x {df.shape[1]} columns")
    print("-" * 78)
    info = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "nulls": df.isna().sum(),
            "null_%": (df.isna().mean() * 100).round(1),
            "distinct": df.nunique(),
        }
    )
    print(info.to_string())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    # Report the range of any column that looks like a date.
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]) and any(
            k in col.lower() for k in ("date", "year", "week")
        ):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().any():
                    print(f"\n{col}: {parsed.min()} -> {parsed.max()}")
            except Exception:
                pass
    print()


def main() -> None:
    files = sorted(RAW_DIR.rglob("*.csv"))
    if not files:
        print(f"No CSV files found in {RAW_DIR}. Run src/00_download.py first.")
        return
    print(f"Found {len(files)} CSV file(s): {[f.name for f in files]}\n")
    for f in files:
        summarize(f)


if __name__ == "__main__":
    main()
