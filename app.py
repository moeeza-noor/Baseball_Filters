import pandas as pd
import re
import streamlit as st
from datetime import datetime, timedelta

# Function to clean the date column
def clean_date(date_str):
    date_str = re.sub(r"\s*\(.*\)", "", date_str)
    try:
        return pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
    except ValueError:
        return pd.to_datetime(date_str, format='%m/%d/%Y', errors='coerce')

# Load the dataset
file_path = 'merged_dataset.csv'
df = pd.read_csv(file_path)

# Clean the Date column
df['Date'] = df['Date'].apply(clean_date)
df = df.dropna(subset=['Date'])

# Create a Game Type column based on some logic
def determine_game_type(row):
    if 'All-Star' in row['Result']:
        return 'All-Star Game'
    elif row['RS'] > 0 and row['RA'] > 0:  # Adjust conditions as needed
        return 'Regular Season'
    else:
        return 'Postseason'

# Apply the function to create a new Game Type column
df['Game Type'] = df.apply(determine_game_type, axis=1)

# Sidebar Filters
st.sidebar.header("Timeframe Filters")

# Game Type Filter
game_type_options = ['Regular Season', 'All-Star Game', 'Postseason']
selected_game_type = st.sidebar.selectbox("Choose Game Type", game_type_options)

# Season Filter
season_options = ['Any', '2024', '2023', '2022', 'Wild-Card Era', 'Divisional Era', 'Expansion Era', 'Integration Era', 'Live-Ball Era']
selected_season = st.sidebar.selectbox("Choose Season", season_options)

# Last n Days Filter
last_n_days = st.sidebar.number_input("Last N Days", min_value=1, max_value=365, value=30)

# Custom Timeframe Filter
start_date = st.sidebar.date_input("Start Date", df['Date'].min().date())
end_date = st.sidebar.date_input("End Date", df['Date'].max().date())

# Span of Plate Appearances Filter
min_pa = st.sidebar.number_input("Minimum Plate Appearances (PA)", min_value=1, max_value=165, value=1)
max_pa = st.sidebar.number_input("Maximum Plate Appearances (PA)", min_value=1, max_value=165, value=165)

# Team Filters
st.sidebar.header("Team Filters")

# Team Filter
team_options = df['Team'].unique().tolist()
selected_team = st.sidebar.selectbox("Choose Team", team_options)

# Opponent Filter
opponent_options = df['Opp'].unique().tolist()
selected_opponent = st.sidebar.selectbox("Choose Opponent", opponent_options)

# Team Success Filter
team_success_options = [
    "All Teams",
    "Won World Series",
    "Lost World Series",
    "League Champion",
    "Made Playoffs",
    "Missed Playoffs",
    "By Division Finish",
    "By Team Wins",
    "By Winning Percentage"
]
selected_team_success = st.sidebar.selectbox("Choose Team Success", team_success_options)

# League Filter
league_options = [
    "American League (1901-present)",
    "National League (1876-present)",
    "Federal League (1914-1915)",
    "All/Any",
    "Active",
    "Inactive",
    "Non-Clear"
]
selected_league = st.sidebar.selectbox("Choose League", league_options)

# Inning/Score/Margin Filters
st.sidebar.header("Inning/Score/Margin Filters")

# Home Team Filters
st.sidebar.subheader("Home Team")
home_inning_range = st.sidebar.slider("Home Team Inning Range", min_value=1, max_value=26, value=(1, 9))
home_runs_scored = st.sidebar.number_input("Home Runs Scored >=", min_value=0)
home_runs_allowed = st.sidebar.number_input("Home Runs Allowed >=", min_value=0)
home_margin = st.sidebar.number_input("Home Margin >=", min_value=0)

# Away Team Filters
st.sidebar.subheader("Away Team")
away_inning_range = st.sidebar.slider("Away Team Inning Range", min_value=1, max_value=26, value=(1, 9))
away_runs_scored = st.sidebar.number_input("Away Runs Scored >=", min_value=0)
away_runs_allowed = st.sidebar.number_input("Away Runs Allowed >=", min_value=0)
away_margin = st.sidebar.number_input("Away Margin >=", min_value=0)

# Button to apply filters
apply_filters = st.sidebar.button("Apply Filters")

# Display DataFrame based on whether filters are applied
if apply_filters:
    # Create a copy of the DataFrame to apply filters
    filtered_df = df.copy()

    # Apply Game Type Filter
    filtered_df = filtered_df[filtered_df['Game Type'] == selected_game_type]

    # Apply Season Filter
    if selected_season != 'Any':
        if selected_season.isnumeric():
            filtered_df = filtered_df[filtered_df['Date'].dt.year == int(selected_season)]

    # Apply Last N Days Filter
    if last_n_days:
        filtered_df = filtered_df[filtered_df['Date'] >= (pd.Timestamp.today() - pd.Timedelta(days=last_n_days))]

    # Apply Custom Timeframe Filter
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Date'] >= pd.to_datetime(start_date)) & (filtered_df['Date'] <= pd.to_datetime(end_date))]

    # Apply Plate Appearances Filter
    if 'PA' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['PA'] >= min_pa) & (filtered_df['PA'] <= max_pa)]

    # Apply Team Filter
    if selected_team:
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]

    # Apply Opponent Filter
    if selected_opponent:
        filtered_df = filtered_df[filtered_df['Opp'] == selected_opponent]

    # Apply Home Runs Scored Filter
    if home_runs_scored > 0:
        filtered_df = filtered_df[filtered_df['RS'] >= home_runs_scored]

    # Apply Home Runs Allowed Filter
    if home_runs_allowed > 0:
        filtered_df = filtered_df[filtered_df['RA'] >= home_runs_allowed]

    # Apply Home Margin Filter
    if home_margin > 0:
        filtered_df = filtered_df[filtered_df['RS'] - filtered_df['RA'] >= home_margin]

    # Apply Away Runs Scored Filter
    if away_runs_scored > 0:
        filtered_df = filtered_df[filtered_df['Opp'] == selected_opponent]
        filtered_df = filtered_df[filtered_df['RA'] >= away_runs_scored]

    # Apply Away Runs Allowed Filter
    if away_runs_allowed > 0:
        filtered_df = filtered_df[filtered_df['Opp'] == selected_opponent]
        filtered_df = filtered_df[filtered_df['RS'] >= away_runs_allowed]

    # Display the filtered results
    st.header("Filtered Games")
    st.write(f"Showing {len(filtered_df)} games")
    st.dataframe(filtered_df)

else:
    # Show all data when filters are not applied
    st.header("All Games")
    st.write(f"Showing {len(df)} games")
    st.dataframe(df)
