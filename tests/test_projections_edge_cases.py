# tests/test_projections_edge_cases.py

import pytest
import pandas as pd
from requests.exceptions import ReadTimeout
from flask import url_for

from app.services.ml_models import predict_season_total
from nba_api.stats.endpoints import LeagueDashPlayerStats
from app.routes.projections import bp as projections_bp


def test_ml_api_invalid_player(monkeypatch, client):
    """If the pickle file is missing, we should get a 404 + error message."""
    monkeypatch.setattr(
        'app.services.ml_models.predict_season_total',
        lambda pid, season: (_ for _ in ()).throw(FileNotFoundError)
    )

    res = client.get(url_for('projections.ml_proj', player_id=99999))
    assert res.status_code == 404
    assert res.get_json() == {'error': 'Model not found. Please train first.'}


def test_stat_trend_zero_games(monkeypatch, client):
    """If a player has no games, trend should render with empty series and project=0."""
    # fake an empty log
    class FakeEmptyLog:
        def __init__(*a, **k): pass
        def get_data_frames(self):
            return [pd.DataFrame(columns=['GAME_DATE','PTS','REB','AST'])]

    monkeypatch.setattr(
        'app.routes.projections.PlayerGameLog',
        FakeEmptyLog
    )

    res = client.get(url_for('projections.stat_trend', player_id=1234, stat='PTS'))
    html = res.get_data(as_text=True)
    # Expect the template to at least contain our <canvas> or a specific placeholder
    assert '<canvas' in html or 'No data' in html  


def test_projections_page_renders_controls(client):
    """A very light integration test: /projections/ must include our selectors and canvas."""
    res = client.get(url_for('projections.projections_page'))
    html = res.get_data(as_text=True)

    # the two <select> controls
    assert 'id="projTypeSelector"' in html
    assert 'id="teamSelector"' in html

    # the chart container
    assert '<canvas id="mlProjChart"' in html
