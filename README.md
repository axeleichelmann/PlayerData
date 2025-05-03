# PlayerData Technical Task

This repository contains the scripts used to generate meaningful insights from GPS tracking data as part of the PlayerData Graduate Data Scientist Interview Process.

## Overview of Insights Dashboard
For this task I created an interactive data insights dashboard using streamlit which can be viewed [here](https://axeleichelmann-playerdata.streamlit.app):

The dashboard contains the following sections:
1. Performance Leaderboard - This sections displays a leaderboard showing the rankings of players based on three key metrics: 'Total Distance Covered', 'Distance Covered in Speed Zone 5', 'Top Speed'. The leaderboard shows the players ID along with their achieved metric value.

2. Player Location Data - This section displays a heatmap showing the locational distribution of each player. A dropdown menu allows you to select a PlayerID for whom you wish to see a heatmap. There is also a breakdown of the percentage of time spent by the player in each third of the pitch.

3. Ball Location Data - This section displays a heatmap showing the locational distribution of the ball, along with a leaderboard showing the percentage of time spent in possesion of the ball by each player.

## Repository Breakdown
The key files in this repository are as follows:
* `Data Scientist - Technical Task.pdf` - contains the task description
* `match_data.csv` - CSV file containing GPS tracking data
* `EDA.ipynb` - Python notebook containing code and findings of Exploratory Data Analysis phase
* `utils.py` - Python script containing functions used for data procesing, leaderboard generation, and generation of various other elements used in the insights dashboard
* `main.py` - Python script containing code used to generate streamlit dashboard
* `requirements.txt` - File containing required packages & libraries used throughout this task to create and run dashboard locally