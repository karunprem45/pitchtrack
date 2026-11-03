"""Clean raw Statcast pitches and split them into the four schema tables.

Rules:
  - keep only the columns the schema uses
  - drop rows missing a key column (game_pk, at_bat_number, pitch_number, pitcher)
  - drop duplicate pitches (same game, at-bat and pitch number)
  - pitch speed outside 40-110 mph is treated as a bad reading and set to null
"""
import glob
import json
from pathlib import Path

import pandas as pd

KEY = ["game_pk", "at_bat_number", "pitch_number"]
PITCH_COLS = KEY + ["pitcher", "batter", "pitch_type", "inning", "balls", "strikes",
                    "release_speed", "release_spin_rate", "pfx_x", "pfx_z",
                    "plate_x", "plate_z", "description", "events"]


def clean(raw: pd.DataFrame):
    """Return (tables, counts). tables maps table name to a DataFrame."""
    counts = {"rows_in": len(raw)}
    df = raw.dropna(subset=KEY + ["pitcher"]).copy()
    counts["dropped_missing_keys"] = counts["rows_in"] - len(df)

    before = len(df)
    df = df.drop_duplicates(subset=KEY, keep="last")
    counts["dropped_duplicates"] = before - len(df)

    bad_speed = ~df["release_speed"].between(40, 110) & df["release_speed"].notna()
    counts["speeds_set_null"] = int(bad_speed.sum())
    df.loc[bad_speed, "release_speed"] = pd.NA

    df["game_date"] = pd.to_datetime(df["game_date"]).dt.date
    for c in KEY + ["pitcher", "batter"]:
        df[c] = df[c].astype("int64")

    pitchers = (df[["pitcher", "player_name"]].dropna()
                .drop_duplicates("pitcher", keep="last")
                .rename(columns={"pitcher": "pitcher_id", "player_name": "pitcher_name"}))
    games = df[["game_pk", "game_date", "home_team", "away_team"]].drop_duplicates("game_pk")
    pitch_types = (df[["pitch_type", "pitch_name"]].dropna(subset=["pitch_type"])
                   .drop_duplicates("pitch_type")
                   .rename(columns={"pitch_name": "description"}))
    pitches = df[PITCH_COLS].rename(columns={"pitcher": "pitcher_id", "batter": "batter_id"})

    counts.update({"pitches_out": len(pitches), "pitchers": len(pitchers),
                   "games": len(games), "pitch_types": len(pitch_types)})
    return {"pitchers": pitchers, "games": games,
            "pitch_types": pitch_types, "pitches": pitches}, counts


def main(raw_dir="data/raw", out_dir="data/clean"):
    files = sorted(glob.glob(f"{raw_dir}/*.parquet"))
    if not files:
        raise SystemExit(f"no raw files in {raw_dir}; run etl/extract.py first")
    raw = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    tables, counts = clean(raw)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for name, t in tables.items():
        t.to_parquet(f"{out_dir}/{name}.parquet", index=False)
    Path("output").mkdir(exist_ok=True)
    Path("output/transform_report.json").write_text(json.dumps(counts, indent=2))
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
