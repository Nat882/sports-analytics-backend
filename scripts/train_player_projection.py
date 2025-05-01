import os
import pickle
import pandas as pd
from nba_api.stats.endpoints.playergamelog import PlayerGameLog
from sklearn.linear_model import LinearRegression

# Save models here
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_save(player_id: int, season: str):
    """
    Fetches game‐by‐game logs for player_id in the given season,
    fits a linear regression to cumulative points vs game number,
    and pickles the model.
    """
    # 1. Fetch game logs
    logs = PlayerGameLog(
        player_id=player_id,
        season=season,
        season_type_all_star='Regular Season',
        timeout=15
    )
    df = logs.get_data_frames()[0].sort_values('GAME_DATE')

    # Skip players with fewer than 2 games
    if df.shape[0] < 2:
        print(f"  → Skipping {player_id}: only {df.shape[0]} games")
        return

    df['GAME_NUM']   = range(1, len(df) + 1)
    df['CUM_POINTS'] = df['PTS'].cumsum()

    # 2. Fit linear regression
    X = df[['GAME_NUM']].values
    y = df['CUM_POINTS'].values
    model = LinearRegression().fit(X, y)

    # 3. Persist with pickle
    fname = f"proj_model_{player_id}_{season.replace('-','')}.pkl"
    path  = os.path.join(MODEL_DIR, fname)
    with open(path, 'wb') as f:
        pickle.dump(model, f)

    print(f"  → Saved model for {player_id} to {path}")
