-- PitchTrack schema: one row per pitch, with pitchers and games split out
-- so names and game info are stored once instead of on every pitch.

CREATE TABLE IF NOT EXISTS pitchers (
    pitcher_id   INTEGER PRIMARY KEY,          -- MLBAM player ID
    pitcher_name TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS games (
    game_pk   INTEGER PRIMARY KEY,             -- MLBAM game ID
    game_date DATE    NOT NULL,
    home_team TEXT    NOT NULL,
    away_team TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS pitch_types (
    pitch_type  TEXT PRIMARY KEY,              -- e.g. FF, SL, CH
    description TEXT
);

CREATE TABLE IF NOT EXISTS pitches (
    game_pk          INTEGER NOT NULL REFERENCES games(game_pk),
    at_bat_number    INTEGER NOT NULL,
    pitch_number     INTEGER NOT NULL,         -- pitch number within the at-bat
    pitcher_id       INTEGER NOT NULL REFERENCES pitchers(pitcher_id),
    batter_id        INTEGER NOT NULL,
    pitch_type       TEXT    REFERENCES pitch_types(pitch_type),
    inning           SMALLINT,
    balls            SMALLINT,
    strikes          SMALLINT,
    release_speed    REAL,                     -- mph
    release_spin_rate REAL,                    -- rpm
    pfx_x            REAL,                     -- horizontal movement (ft)
    pfx_z            REAL,                     -- vertical movement (ft)
    plate_x          REAL,
    plate_z          REAL,
    description      TEXT,                     -- e.g. called_strike, ball
    events           TEXT,                     -- at-bat result, last pitch only
    PRIMARY KEY (game_pk, at_bat_number, pitch_number)
);

-- Dashboard queries filter by pitcher and by date, so index those paths.
CREATE INDEX IF NOT EXISTS idx_pitches_pitcher ON pitches (pitcher_id);
CREATE INDEX IF NOT EXISTS idx_games_date      ON games (game_date);
