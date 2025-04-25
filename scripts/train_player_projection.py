# scripts/train_player_projection.py

import os
import pickle
import pandas as pd


from nba_api.stats.endpoints.playergamelog import PlayerGameLog

from sklearn.linear_model import LinearRegression

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_save(player_id, season):
    # 1. Fetch game logs
    gl = PlayerGameLog(player_id=player_id, season=season, season_type_all_star='Regular Season')
    df = gl.get_data_frames()[0].sort_values('GAME_DATE')
    df['GAME_NUM'] = range(1, len(df) + 1)
    df['CUM_POINTS'] = df['PTS'].cumsum()

    # 2. Fit linear regression
    X = df[['GAME_NUM']].values
    y = df['CUM_POINTS'].values
    model = LinearRegression().fit(X, y)

    # 3. Persist with pickle
    path = os.path.join(MODEL_DIR, f'proj_model_{player_id}_{season}.pkl')
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Saved model to {path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python train_player_projection.py <PLAYER_ID> <SEASON>")
        sys.exit(1)
    pid, season = int(sys.argv[1]), sys.argv[2]
    train_and_save(pid, season)
