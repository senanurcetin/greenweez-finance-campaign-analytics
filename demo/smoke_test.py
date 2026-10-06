"""Headless smoke test of the Streamlit dashboard (no browser needed).

Usage: python demo/smoke_test.py <duckdb file> <sources|no-sources>

`sources` expects the default source mode (per-source ads sections visible), `no-sources` the
fvt_gsheet mode (those sections hidden and an explanatory note shown). Each mode runs in its own
process because the app reads DEMO_DB once at import time.
"""
import os
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent / "app.py"


def main() -> int:
    db, mode = sys.argv[1], sys.argv[2]
    expect_sources = mode == "sources"
    os.environ["DEMO_DB"] = db
    at = AppTest.from_file(str(APP), default_timeout=120).run()
    problems = []
    if at.exception:
        problems.append(f"app raised: {[e.value for e in at.exception]}")
    if at.error:
        problems.append(f"app showed errors: {[e.value for e in at.error]}")
    subheaders = [s.value for s in at.subheader]
    if ("Ad spend by source" in subheaders) != expect_sources:
        problems.append(f"'Ad spend by source' visibility wrong for mode {mode}: {subheaders}")
    if bool(at.info) == expect_sources:
        problems.append(f"source-mode note visibility wrong for mode {mode}: {[i.value for i in at.info]}")
    for required in ("Monthly margin waterfall", "Marketing efficiency"):
        if required not in subheaders:
            problems.append(f"missing section: {required}")
    if len(at.metric) != 5:
        problems.append(f"expected 5 KPI tiles, found {len(at.metric)}")
    if problems:
        print(f"FAIL ({db}, {mode}):\n  " + "\n  ".join(problems))
        return 1
    print(f"OK ({db}, {mode}): {len(subheaders)} sections, {len(at.metric)} KPI tiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
