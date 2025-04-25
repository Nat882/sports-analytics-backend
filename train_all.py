# train_all.py
import pandas as pd
from nba_api.stats.endpoints import LeagueDashPlayerStats
from scripts.train_player_projection import train_and_save

if __name__ == '__main__':
    season = "2024-25"
    # fetch all player IDs
    df = LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame"
    ).get_data_frames()[0]

    for pid in df["PLAYER_ID"].unique():
        train_and_save(pid, season)
