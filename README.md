# PitchTrack

Pulls public pitch-by-pitch Statcast data with `pybaseball`, cleans it, loads
it into a PostgreSQL schema built around pitchers, games and pitches, and shows
velocity and movement in a Streamlit + Plotly dashboard.

```
pybaseball -> extract.py -> transform.py -> load.py -> PostgreSQL -> dashboard
             (raw parquet)  (clean tables)  (upsert)
```

## 1. Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Install PostgreSQL (on Mac: `brew install postgresql@16 && brew services start postgresql@16`),
then create the database: `createdb pitchtrack`. Edit `DATABASE_URL` in `.env`
if your username or password differ.

## 2. Run the tests

```bash
pytest -q
```

## 3. Pull data

Start small (one week) to check everything works, then pull a full month or season:

```bash
python etl/extract.py --start 2026-04-01 --end 2026-04-07
```

A full season is several hundred thousand pitches and takes a while. Results
are cached, so reruns are fast.

## 4. Clean and load

```bash
python etl/transform.py
python etl/load.py
```

Both steps write a JSON report in `output/`. `load.py` is safe to rerun:
pitches already in the database are skipped.

## 5. Dashboard

```bash
streamlit run dashboard/app.py
```

## 6. Queries

`sql/queries.sql` has four analysis queries (velocity by month, velocity by
inning, pitch mix, whiff rate). Run them in `psql` or any SQL client, replacing
`:pitcher_id` with a real ID from the `pitchers` table.

## 7. Record results

Fill in `RESULTS.md` from the reports and the dashboard. Only real numbers.

## Notes

- Schema and design reasoning: `docs/schema.md`
- Data comes from Baseball Savant via `pybaseball`. Use it for personal and
  educational projects, and credit the source in your README.
