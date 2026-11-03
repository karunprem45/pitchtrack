"""Pull pitch-level Statcast data with pybaseball, one week at a time.

Baseball Savant limits how many rows one request returns, so short date
chunks are safer than one big pull. Raw data is saved as Parquet so later
steps can rerun without downloading again.
"""
import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from pybaseball import cache, statcast


def week_chunks(start: date, end: date):
    cur = start
    while cur <= end:
        stop = min(cur + timedelta(days=6), end)
        yield cur, stop
        cur = stop + timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", default="data/raw")
    args = ap.parse_args()

    cache.enable()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0, total, files = time.time(), 0, 0

    for a, b in week_chunks(date.fromisoformat(args.start), date.fromisoformat(args.end)):
        df = statcast(start_dt=a.isoformat(), end_dt=b.isoformat())
        if df is None or df.empty:
            print(f"{a} to {b}: no games")
            continue
        df.to_parquet(out / f"statcast_{a}_{b}.parquet", index=False)
        total += len(df)
        files += 1
        print(f"{a} to {b}: {len(df)} pitches")

    report = {"raw_rows": total, "files": files, "seconds": round(time.time() - t0, 1)}
    Path("output").mkdir(exist_ok=True)
    Path("output/extract_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
