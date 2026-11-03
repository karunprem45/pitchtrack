-- 1. Average fastball velocity by month for one pitcher
SELECT date_trunc('month', g.game_date) AS month,
       ROUND(AVG(p.release_speed)::numeric, 1) AS avg_velo,
       COUNT(*) AS pitches
FROM pitches p JOIN games g USING (game_pk)
WHERE p.pitcher_id = :pitcher_id AND p.pitch_type = 'FF'
GROUP BY 1 ORDER BY 1;

-- 2. Does velocity drop as the game goes on? Average speed by inning
SELECT p.inning, ROUND(AVG(p.release_speed)::numeric, 1) AS avg_velo, COUNT(*) AS pitches
FROM pitches p
WHERE p.pitcher_id = :pitcher_id AND p.pitch_type = 'FF'
GROUP BY p.inning ORDER BY p.inning;

-- 3. Pitch mix for one pitcher
SELECT p.pitch_type, COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM pitches p
WHERE p.pitcher_id = :pitcher_id
GROUP BY p.pitch_type ORDER BY n DESC;

-- 4. Whiff rate by pitch type (swinging strikes / swings)
SELECT p.pitch_type,
       ROUND(100.0 * SUM(CASE WHEN p.description IN ('swinging_strike','swinging_strike_blocked') THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN p.description IN ('swinging_strike','swinging_strike_blocked',
                   'foul','foul_tip','hit_into_play') THEN 1 ELSE 0 END), 0), 1) AS whiff_pct
FROM pitches p
WHERE p.pitcher_id = :pitcher_id
GROUP BY p.pitch_type ORDER BY whiff_pct DESC NULLS LAST;
