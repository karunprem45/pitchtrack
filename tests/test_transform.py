import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from transform import clean  # noqa: E402


def make(rows):
    base = {"game_pk": 1, "at_bat_number": 1, "pitch_number": 1, "pitcher": 100,
            "batter": 200, "player_name": "Doe, John", "pitch_type": "FF",
            "pitch_name": "4-Seam Fastball", "inning": 1, "balls": 0, "strikes": 0,
            "release_speed": 95.0, "release_spin_rate": 2300.0, "pfx_x": -0.5,
            "pfx_z": 1.3, "plate_x": 0.1, "plate_z": 2.5, "description": "ball",
            "events": None, "game_date": "2026-04-01", "home_team": "BOS", "away_team": "NYY"}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_duplicate_pitch_removed():
    tables, counts = clean(make([{}, {}]))
    assert counts["dropped_duplicates"] == 1
    assert len(tables["pitches"]) == 1


def test_missing_key_dropped():
    tables, counts = clean(make([{}, {"pitch_number": None}]))
    assert counts["dropped_missing_keys"] == 1


def test_bad_speed_set_null_not_dropped():
    tables, counts = clean(make([{"release_speed": 250.0}]))
    assert counts["speeds_set_null"] == 1
    assert len(tables["pitches"]) == 1
    assert pd.isna(tables["pitches"]["release_speed"].iloc[0])


def test_pitchers_and_games_stored_once():
    tables, _ = clean(make([{"pitch_number": 1}, {"pitch_number": 2}, {"pitch_number": 3}]))
    assert len(tables["pitchers"]) == 1
    assert len(tables["games"]) == 1
    assert len(tables["pitches"]) == 3


def test_different_pitches_kept():
    _, counts = clean(make([{"pitch_number": 1}, {"pitch_number": 2}]))
    assert counts["dropped_duplicates"] == 0
    assert counts["pitches_out"] == 2
