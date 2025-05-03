##### ------ Functions for data preprocessing, data plotting, metric calculation, etc. --------- ######
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch

from typing import Tuple


######## ---------   Data Processing Functions  -----------  #########

# Define window moving average speed filter
def filterSpeed(window_size : float, df : pd.DataFrame) -> pd.DataFrame:
    """Apply a window moving average filter to the speed data"""

    df_new = pd.DataFrame(columns=['player_id', 'time_s', 'x', 'y', 'speed_mps', 'adjusted_speed'])

    for id in df.player_id.unique():
        df_player = df[df.player_id == id]

        times = df_player['time_s'].values
        speeds = df_player['speed_mps'].values
        adjusted_speed = np.zeros(len(speeds))

        for i, time in enumerate(times):
            left_idx = np.searchsorted(times, time - (window_size/2 + 0.05), side='left')
            right_idx = np.searchsorted(times, time + (window_size/2 + 0.05), side='right')
            adjusted_speed[i] = speeds[left_idx:right_idx].mean()

        df_player['adjusted_speed'] = adjusted_speed
        df_new = pd.concat([df_new,df_player], axis=0, ignore_index=True)

    return df_new

# Define filter to remove low speed data
def removeStationary(min_speed : float, df : pd.DataFrame) -> pd.DataFrame:
    """Remove data points where speed < min_speed"""
    return df[df.adjusted_speed >= min_speed]

# Define filter to remove out-of-pitch data
def removeOffPitch(x_max : float, x_min : float, y_max : float, y_min : float,
                        df : pd.DataFrame) -> pd.DataFrame:
    """Remove data points that occur outside of the pitch"""
    return df[(df.x > x_min) & (df.x < x_max) & (df.y > y_min) & (df.y < y_max)]



#########  -----------    Leaderboard Metric Calculation Functions   -----------  #########

# Define function to create total distance covered rankings
def rank_distance_covered(df : pd.DataFrame, top_k : int=10) -> pd.Series:
    """Calculate the player rankings based on total distance covered"""

    df['dist'] = df['adjusted_speed'] * 0.1
    df_agg = df.groupby('player_id').aggregate({'dist':'sum'}).sort_values(by='dist',ascending=False)
    
    df_rank = pd.Series(data=[f"{player_id}\nDist={df_agg.loc[player_id].dist:.2f} m" for player_id in df_agg.index.tolist()])

    return df_rank.loc[:top_k-1]

# Define function to create zone 5 distance covered rankings
def rank_z5_distance_covered(df : pd.DataFrame, top_k : int=10) -> pd.Series:
    """Calculate the player rankings based on distance covered in Zone 5 speed"""
    df_z5 = df[(df.adjusted_speed > 5.5) & (df.adjusted_speed < 6.972)]

    df_z5['dist'] = df_z5['adjusted_speed'] * 0.1
    df_agg = df_z5.groupby('player_id').aggregate({'dist':'sum'}).sort_values(by='dist',ascending=False)
    
    df_rank = pd.Series(data=[f"{player_id}\nDist={df_agg.loc[player_id].dist:.2f} m" for player_id in df_agg.index.tolist()])

    return df_rank.loc[:top_k-1]

# Define function to create top speed rankings
def rank_top_speed(df : pd.DataFrame, top_k : int=10) -> pd.Series:
    """Calculate the player rankings based on top speed"""

    df_agg = df.groupby('player_id').aggregate({'adjusted_speed':'max'}).sort_values(by='adjusted_speed',ascending=False)
    
    df_rank = pd.Series(data=[f"{player_id}\nSpeed={df_agg.loc[player_id].adjusted_speed:.2f} m/s" for player_id in df_agg.index.tolist()])

    return df_rank.loc[:top_k-1]


##### ------------------ Heatmap Creation Functions -------------  #######
def playerHeatmap(playerID : str, df : pd.DataFrame) -> None:
    """Create a heatmap showing the location distribution of a player"""

    loc_data = df[(df.player_id == playerID)][['x','y']].round(1)
    loc_data['x'] = loc_data.x + 52.5
    loc_data['y'] = loc_data.y + 34

    pitch = Pitch('statsbomb', line_color='white', line_zorder=2)
    fig, ax = pitch.draw()

    bin_stats = pitch.bin_statistic(x=loc_data.x, y=loc_data.y, bins=(30,20), statistic='count')
    heatmap = pitch.heatmap(bin_stats, ax=ax, cmap='hot', edgecolors="#22312b")

    #fig.colorbar(heatmap, ax=ax)
    if playerID=='ball':
        title = f'Location Heatmap of Ball'
    else:
        title = f'Location Heatmap of Player {playerID}'
    fig.suptitle(title)
    plt.show()

    return fig, ax

def playerZoneDistribution(playerID : str, df : pd.DataFrame) -> Tuple:
    """Return the percentage of time spent by the player in the left, middle, and right thirds of the field"""

    loc_data = df[(df.player_id == playerID)][['x','y']].round(1)
    loc_data['x'] = loc_data.x + 52.5
    loc_data['y'] = loc_data.y + 34

    pitch = Pitch('statsbomb', line_color='white', line_zorder=2)
    bin_stats = pitch.bin_statistic(x=loc_data.x, y=loc_data.y, statistic='count', bins=(3,1))
    bin_stats['statistic'] = (pd.DataFrame(bin_stats['statistic']/bin_stats['statistic'].sum())).map(lambda x : f"{x:.0%}").values

    return bin_stats['statistic'][0]



######## -------- Ball Possesion ------- #####
def getPossesion(df_ball : pd.DataFrame, df_players : pd.DataFrame) -> pd.DataFrame:
    """Create new column in df_ball dataframe describing what player is in possesion of ball (based on proximity)"""

    possesion = []

    for i, time in enumerate(df_ball.time_s.values):

        ball_x, ball_y = df_ball[df_ball.time_s == time]['x'].values[0], df_ball[df_ball.time_s == time]['y'].values[0]
        players = df_players[df_players.time_s == time]

        possesionID = None
        min_dist = 100

        for playerID in players.player_id.unique():
            player_x, player_y = players[players.player_id == playerID].x.values[0], players[players.player_id == playerID].y.values[0]
            dist_from_ball = ((player_x - ball_x)**2 + (player_y - ball_y)**2)**(1/2)
            if dist_from_ball < min_dist:
                min_dist = dist_from_ball
                possesionID = playerID
        
        possesion.append(possesionID)
    
    df_ball['possesor'] = possesion

    return df_ball







if __name__=='__main__':
    df = pd.read_csv('match_data.csv')
    df.columns = ['player_id', 'time_s', 'x', 'y', 'speed_mps']
    
    df_players = df[df.player_id != 'ball']
    df_players = filterSpeed(window_size=0.3, df=df_players)
    df_players = removeStationary(min_speed=0.03, df=df_players)

    df_ball = df[df.player_id == 'ball']
    df_ball = filterSpeed(window_size=0.3, df=df_ball)  # Apply window MA filter to speed data
    df_ball = removeStationary(min_speed=0.03, df=df_ball)   # Remove data points where speed is < 0.03m/s
    df_ball = removeOffPitch(x_max=52.5, x_min=-52.5, y_max=34, y_min=-34, df=df_ball)    # Remove out of pitch data points

    df_poss = getPossesion(df_ball, df_players)
    print(df_poss.possesor.value_counts(normalize=True))


    # Test speed filtering
    # df_players = df[df.player_id != 'ball']

    # df_players = filter_speed(0.3, df_players)
    # print(df_players)

    # for playerID in df_players.player_id.unique():
    #     fig, ax = plt.subplots(2,1, figsize=(12,8))

    #     ax[0].plot(df_players[df_players.player_id==playerID]['time_s'], df_players[df_players.player_id==playerID]['speed_mps'])
    #     ax[0].set_title(f"Unfiltered Speed of Player {playerID}")

    #     ax[1].plot(df_players[df_players.player_id==playerID]['time_s'], df_players[df_players.player_id==playerID]['adjusted_speed'])
    #     ax[1].set_title(f"Filtered Speed of Player {playerID}")

    # plt.show()