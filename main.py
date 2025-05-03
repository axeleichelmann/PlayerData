import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import filterSpeed, removeStationary, removeOffPitch,\
rank_distance_covered, rank_top_speed, rank_z5_distance_covered, playerHeatmap, playerZoneDistribution, getPossesion


# Import, Clean & Preprocess Data
df = pd.read_csv('match_data.csv')
df.columns = ['player_id', 'time_s', 'x', 'y', 'speed_mps']

df_players = df[df.player_id != 'ball']
df_players = filterSpeed(window_size=0.3, df=df_players)  # Apply window MA filter to speed data
df_players = removeStationary(min_speed=0.03, df=df_players)   # Remove data points where speed is < 0.03m/s
df_players = removeOffPitch(x_max=52.5, x_min=-52.5, y_max=34, y_min=-34, df=df_players)    # Remove out of pitch data points


df_ball = df[df.player_id == 'ball']
df_ball = filterSpeed(window_size=0.3, df=df_ball)  # Apply window MA filter to speed data
df_ball = removeStationary(min_speed=0.03, df=df_ball)   # Remove data points where speed is < 0.03m/s
df_ball = removeOffPitch(x_max=52.5, x_min=-52.5, y_max=34, y_min=-34, df=df_ball)    # Remove out of pitch data points

#### ----- Streamlit Page Code ----- #####
st.set_page_config(page_title="Sports Analytics Dashboard", page_icon=":soccer_ball:")

st.title("Sports Data Analytics Dashboard")
st.markdown(
    """ 
    Welcome to the dashboard for player & team performance analytics based on data collected with the PlayerData Tracker.
    """
)

### Display Key Metric Leaderboards
with st.container():
    st.write("---")
    st.header("Performance Leaderboard")

    top_k = st.selectbox("Show top ", np.arange(1,17), index=9)
    metric = st.selectbox("Select Leaderboard Metric:", ['Total Distance Covered', 'Speed Zone 5 Distance Covered', 'Top Speed'])

    # Create athlete ranking leaderboard
    rank_dist = rank_distance_covered(df_players, top_k)
    rank_distZ5 = rank_z5_distance_covered(df_players, top_k)
    rank_speed = rank_top_speed(df_players, top_k)

    if metric == 'Total Distance Covered':
        leaderboard = rank_dist.set_index(np.arange(1,top_k+1))
    elif metric == 'Speed Zone 5 Distance Covered':
        leaderboard = rank_distZ5.set_index(np.arange(1,top_k+1))
    else:
        leaderboard = rank_speed.set_index(np.arange(1,top_k+1))

    st.table(leaderboard)


### Display Player Heatmaps & Location Data
with st.container():
    st.write("---")
    st.header("Player Location Data")
    playerID = st.selectbox("Select Player", df_players.player_id.unique().tolist())
    fig, ax = playerHeatmap(playerID=playerID, df=df_players)
    zone_dist = playerZoneDistribution(playerID=playerID, df=df_players)

    st.pyplot(fig)

    st.write(f"Percentage of time spent by player {playerID} in:")
    st.write(f"Left Third = {zone_dist[0]}, Middle Third = {zone_dist[1]}, Right Third = {zone_dist[2]}")

### Display Ball Heatmap & Location Data
with st.container():
    st.write("---")
    st.header("Ball Location Data")
    fig, ax = playerHeatmap(playerID='ball', df=df_ball)

    st.pyplot(fig)

    st.subheader("Ball Possession Leaderboard")
    df_possesion = getPossesion(df_ball, df_players)
    possesion_leaderboard = df_possesion.possesor.value_counts(normalize=True).sort_values(ascending=False)\
                                                .reset_index(drop=False)\
                                                .set_index(np.arange(1,df_possesion.possesor.nunique()+1))
                            
    possesion_leaderboard['proportion'] = possesion_leaderboard['proportion'].apply(lambda x : f"{x*100:.2f}%")
    
    st.table(possesion_leaderboard.rename(columns={'possesor':'Player ID', 'proportion' : 'Possession'}))