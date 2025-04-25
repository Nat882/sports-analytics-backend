# app/services/ml_models.py

import os
import pickle
import numpy as np

# must match the directory your train script writes into
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def predict_season_total(player_id: int, season: str) -> float:
    """
    Load the per-player linear regression model and predict cumulative points at game 82.
    """
    model_path = os.path.join(MODEL_DIR, f'proj_model_{player_id}_{season}.pkl')
    if not os.path.exists(model_path):
        # let your blueprint catch this and return 404
        raise FileNotFoundError(f"No model for {player_id} / {season}")

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # we trained on X = [[1], [2], [3], ...] representing game number
    # to project end-of-season total, ask for game number = 82
    X_full = np.array([[82]])
    total = model.predict(X_full)[0]
    return float(total)
