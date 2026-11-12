"""Shared test setup.

tests/fixtures/mini_billboard.csv has 14 hand-built rows whose correct answers
are known in advance:

  - 10 real songs: Alpha, Beta, Gamma (1960s); Delta, Epsilon, Zeta (1970s);
    Kappa (1980s); Eta (2010s); Theta, Iota (2020s, both on the final chart
    of 2021-05-29, so still charting)
  - Alpha appears twice, identical in every column (one copy is dropped)
  - Kappa appears twice: the first copy has no audio features, the second does
    (the second is kept)
  - 1 corrupted row with no chart data ("37623" by "4")
  - 1 unreliable row dated after 2021-05-29 ("Lambda (Version 5)")
  - Gamma and Zeta have no audio features
  - Primary artists: Ann Lee (Alpha, Beta, Zeta), Cat Band, Dee & Dum,
    Eve (Eta, Theta), Gus, Hal -> 6 artists
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

FIXTURE_CSV = ROOT / "tests" / "fixtures" / "mini_billboard.csv"


@pytest.fixture(scope="session")
def fixture_db(tmp_path_factory):
    """Path to a database built from the fixture CSV."""
    from db import build_database

    db_path = tmp_path_factory.mktemp("db") / "mini.db"
    report = build_database(FIXTURE_CSV, db_path)
    return {"path": db_path, "report": report}
