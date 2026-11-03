# Results log (fill in from real runs only)

| What | Value | Where it comes from |
|---|---|---|
| Date range pulled | | your `--start` / `--end` |
| Raw pitches | | `output/extract_report.json` -> raw_rows |
| Duplicates removed | | `output/transform_report.json` -> dropped_duplicates |
| Bad speed readings set to null | | `transform_report.json` -> speeds_set_null |
| Pitches loaded | | `output/load_report.json` -> pitches.rows_in_table |
| Pitchers / games | | `load_report.json` |
| Load time (seconds) | | `load_report.json` -> seconds |
| Unit tests | | `pytest -q` output |
| One real finding from the dashboard | | e.g. how one pitcher's velocity changed by inning |
