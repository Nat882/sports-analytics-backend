#!/usr/bin/env python3
import os
import sys
from requests.exceptions import ReadTimeout

# ensure project root is on path, so we can import both scripts
ROOT = os.path.abspath(os.path.join(__file__, ".."))
sys.path.insert(0, ROOT)

from nba_api.stats.endpoints import LeagueDashPlayerStats
from train_player_projection import train_and_save

def train_everyone(season="2024-25"):
    print(f"Fetching all player IDs for season {season}…")
    stats = LeagueDashPlayerStats(
        season=season,
        per_mode_detailed="PerGame",
        timeout=30
    )
    df = stats.get_data_frames()[0]
    player_ids = df["PLAYER_ID"].unique()
    print(f"Found {len(player_ids)} unique players")

    for pid in player_ids:
        try:
            print(f"Training player {pid} …")
            train_and_save(pid, season)
        except ReadTimeout:
            print(f"  ! Timeout when fetching logs for {pid}, skipping.")
        except Exception as e:
            print(f"  ! Error training {pid}: {e}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("season", nargs="?", default="2024-25")
    args = p.parse_args()
    train_everyone(args.season)
