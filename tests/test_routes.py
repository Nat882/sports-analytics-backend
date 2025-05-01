# tests/test_routes.py
import json
import pandas as pd
from requests.exceptions import ReadTimeout
import pytest
from nba_api.stats.endpoints import LeagueDashPlayerStats
from nba_api.stats.endpoints.playergamelog import PlayerGameLog

def test_players_list_route(client, monkeypatch):
    # stub LeagueDashPlayerStats to return two fake players
    fake_df = [{"PLAYER_ID":10,"PLAYER_NAME":"Alice","TEAM_ID":1,"PTS":10,"REB":5,"AST":2,"GP":10}]
    class FakeStats:
        def get_data_frames(self):
            import pandas as pd
            return [pd.DataFrame(fake_df)]
    monkeypatch.setattr(LeagueDashPlayerStats, '__init__', lambda *a,**k: None)
    monkeypatch.setattr(LeagueDashPlayerStats, 'get_data_frames', FakeStats().get_data_frames)

    response = client.get('/players/')
    assert response.status_code == 200
    assert b"Alice" in response.data

def test_stat_trend_route(client, monkeypatch):
    # stub PlayerGameLog to return 3 games of PTS
    class FakeLog:
        def get_data_frames(self):
            import pandas as pd
            return [pd.DataFrame([{"GAME_DATE":"2025-01-01","PTS":5},
                                  {"GAME_DATE":"2025-01-02","PTS":7}])]
    monkeypatch.setattr(PlayerGameLog, '__init__', lambda *a,**k: None)
    monkeypatch.setattr(PlayerGameLog, 'get_data_frames', FakeLog().get_data_frames)

    res = client.get('/projections/trend/10/PTS')
    assert res.status_code == 200
    # cumulative 5, then 12
    assert b"12" in res.data

def test_ml_api_route(client, monkeypatch):
    # stub predict_season_total
    from app.services.ml_models import predict_season_total
    monkeypatch.setattr('app.services.ml_models.predict_season_total', lambda pid,season: 123.4)
    res = client.get('/projections/api/player_projections_ml/10')
    data = res.get_json()
    assert data['PROJECTED_PTS_ML'] == 123.4
    assert res.status_code == 200

def test_ml_api_route_model_not_found(client, monkeypatch):
    # Make predict_season_total raise FileNotFoundError
    import app.services.ml_models as ml
    monkeypatch.setattr(ml, 'predict_season_total', lambda pid, season: (_ for _ in ()).throw(FileNotFoundError()))
    
    res = client.get('/projections/api/player_projections_ml/99999')
    assert res.status_code == 404
    data = res.get_json()
    assert 'error' in data
    assert data['error'] == 'Model not found. Please train first.'

def test_stat_trend_handles_no_games(monkeypatch, client):
    from app.routes.projections import PlayerGameLog

    class FakeEmptyLog:
        def __init__(self, *args, **kwargs): pass
        def get_data_frames(self):
            # empty DataFrame with at least the columns used
            return [pd.DataFrame(columns=['GAME_DATE','PTS','REB','AST'])]

    # patch the PlayerGameLog in your projections module
    monkeypatch.setattr('app.routes.projections.PlayerGameLog', FakeEmptyLog)

    # hit the trend endpoint for 'PTS'
    resp = client.get('/projections/trend/999/PTS')
    assert resp.status_code == 200
    # make sure the page still renders and includes a '0' projected value
    body = resp.get_data(as_text=True)
    # template prints projected value; look for "0" near that context
    assert '0' in body

# projections_page: filtering by a team with no players yields an empty table
def test_projections_page_team_filter_no_matches(client):
    # pick a (very unlikely) team id to filter
    resp = client.get('/projections/?team=9999999')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # between the <tbody>…</tbody> there should be no <tr> rows
    tbody = html.split('<tbody>')[1].split('</tbody>')[0]
    assert '<tr>' not in tbody

# projections_page: simulate a timeout when fetching stats => flash + empty players
def test_projections_page_handles_timeout(monkeypatch, client):
    from nba_api.stats.endpoints import leaguedashplayerstats

    # stub the constructor to raise ReadTimeout
    monkeypatch.setattr(leaguedashplayerstats.LeagueDashPlayerStats,
                        '__init__',
                        lambda *args, **kwargs: (_ for _ in ()).throw(ReadTimeout()))
    resp = client.get('/projections/')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # ensure your flash appears about load failure
    assert "Could not load player projections." in html
    # the table should render with no players
    tbody = html.split('<tbody>')[1].split('</tbody>')[0]
    assert '<tr>' not in tbody