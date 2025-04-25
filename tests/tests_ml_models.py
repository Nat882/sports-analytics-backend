# tests/test_ml_models.py
import os, pickle
import pandas as pd
import numpy as np
import tempfile
from sklearn.linear_model import LinearRegression
from app.services.ml_models import train_and_save, predict_season_total

def make_dummy_log(tmp_path):
    # create a fake model for player_id=999 season="2024-25"
    model = LinearRegression()
    # train on a tiny linear dataset
    X = np.array([[1],[2],[3]])
    y = np.array([2,4,6])
    model.fit(X,y)
    pkl_path = tmp_path / "proj_model_999_2024-25.pkl"
    with open(pkl_path,'wb') as f:
        pickle.dump(model, f)
    return str(pkl_path)

def test_predict_season_total(tmp_path, monkeypatch):
    # point your MODEL_DIR to tmp_path
    monkeypatch.setenv("MODEL_DIR", str(tmp_path))
    # write a dummy model file
    pkl = make_dummy_log(tmp_path)
    # now call predict_season_total
    total = predict_season_total(999, "2024-25")
    # linear cum points: at game N, cum=2N, so final over 82 games = 2*82
    assert abs(total - 164.0) < 1e-6

def test_predict_season_total_missing_model(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        predict_season_total(12345, "2024-25")
