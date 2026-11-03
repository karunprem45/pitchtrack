# Results log (fill in from real runs only)

| What | Value | Where it comes from |
|---|---|---|
| Date range pulled | 2026-04-01 to 2026-04-30 | your `--start` / `--end` |
| Raw pitches | 117,333 | `output/extract_report.json` -> raw_rows |
| Duplicates removed | 0 | `output/transform_report.json` -> dropped_duplicates |
| Bad speed readings set to null | 53 | `transform_report.json` -> speeds_set_null |
| Pitches loaded | 117,333 | `output/load_report.json` -> pitches.rows_in_table |
| Pitchers / games | 533 / 392 | `load_report.json` |
| Load time (seconds) | 11.6 (89,831 new rows on top of a first week already loaded) | `load_report.json` -> seconds |
| Unit tests | 5 passed | `pytest -q` output |
| One real finding from the dashboard | Freddy Peralta's four-seam held its speed deep into starts: 93.5 mph in the 1st inning, 94.5 mph in the 6th | `sql/queries.sql` query 2, pitcher_id 642547 |
