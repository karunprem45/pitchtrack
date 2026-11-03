"""Streamlit + Plotly dashboard on the PitchTrack database.
Run: streamlit run dashboard/app.py"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])
st.set_page_config(page_title="PitchTrack", layout="wide")
st.title("PitchTrack: pitch velocity and movement")


@st.cache_data
def q(sql, **params):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


pitchers = q("""SELECT pt.pitcher_id, pt.pitcher_name, COUNT(*) AS n
                FROM pitchers pt JOIN pitches p USING (pitcher_id)
                GROUP BY 1, 2 HAVING COUNT(*) >= 300 ORDER BY pitcher_name""")
choice = st.selectbox("Pitcher", pitchers["pitcher_name"])
pid = int(pitchers.loc[pitchers["pitcher_name"] == choice, "pitcher_id"].iloc[0])

df = q("""SELECT g.game_date, p.pitch_type, p.release_speed, p.release_spin_rate,
                 p.pfx_x, p.pfx_z, p.inning
          FROM pitches p JOIN games g USING (game_pk)
          WHERE p.pitcher_id = :pid""", pid=pid)

c1, c2, c3 = st.columns(3)
c1.metric("Pitches", f"{len(df):,}")
c2.metric("Games", df["game_date"].nunique())
c3.metric("Pitch types", df["pitch_type"].nunique())

# 1. Time series: average velocity per game, one line per pitch type
by_game = (df.dropna(subset=["release_speed"])
             .groupby(["game_date", "pitch_type"], as_index=False)["release_speed"].mean())
st.plotly_chart(px.line(by_game, x="game_date", y="release_speed", color="pitch_type",
                        markers=True, labels={"release_speed": "Avg speed (mph)", "game_date": "Game"},
                        title="Average velocity by game"), use_container_width=True)

left, right = st.columns(2)
# 2. Movement chart: horizontal vs vertical break, in inches
mv = df.dropna(subset=["pfx_x", "pfx_z"]).assign(h_in=lambda d: d.pfx_x * 12, v_in=lambda d: d.pfx_z * 12)
left.plotly_chart(px.scatter(mv, x="h_in", y="v_in", color="pitch_type", opacity=0.5,
                             labels={"h_in": "Horizontal break (in)", "v_in": "Vertical break (in)"},
                             title="Pitch movement"), use_container_width=True)
# 3. Velocity by inning (fatigue check)
inn = df[df.pitch_type == "FF"].groupby("inning", as_index=False)["release_speed"].mean()
right.plotly_chart(px.bar(inn, x="inning", y="release_speed",
                          labels={"release_speed": "Avg four-seam speed (mph)"},
                          title="Four-seam velocity by inning"), use_container_width=True)
