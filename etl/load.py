"""Load the clean tables into PostgreSQL. Safe to rerun: rows that already
exist (same primary key) are skipped, not duplicated."""
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.dialects.postgresql import insert

ORDER = ["pitchers", "games", "pitch_types", "pitches"]  # parents before pitches


def main(clean_dir="data/clean"):
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.begin() as conn:
        conn.execute(text(Path("sql/schema.sql").read_text()))

    meta = MetaData()
    t0, report = time.time(), {}
    with engine.begin() as conn:
        for name in ORDER:
            df = pd.read_parquet(f"{clean_dir}/{name}.parquet")
            df = df.astype(object).where(df.notna(), None)
            table = Table(name, meta, autoload_with=conn)
            before = conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
            rows = df.to_dict("records")
            for i in range(0, len(rows), 5000):
                conn.execute(insert(table).values(rows[i:i + 5000]).on_conflict_do_nothing())
            after = conn.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar()
            report[name] = {"rows_in_file": len(df), "new_rows": after - before, "rows_in_table": after}
            print(f"{name}: {after - before} new rows, {after} total")
    report["seconds"] = round(time.time() - t0, 1)
    Path("output").mkdir(exist_ok=True)
    Path("output/load_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
