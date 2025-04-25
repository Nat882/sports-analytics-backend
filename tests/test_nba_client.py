# tests/test_nba_client.py
import pytest
import pandas as pd
from requests.exceptions import ReadTimeout
from app.services.nba_client import get_all_teams
from nba_api.stats.endpoints import LeagueDashTeamStats

class DummyDF(pd.DataFrame): pass

def test_get_all_teams_returns_dict(monkeypatch):
    # stub NBA API call to return a df with TEAM_ID & TEAM_NAME columns
    class FakeStats:
        def get_data_frames(self):
            return [pd.DataFrame([{"TEAM_ID":1,"TEAM_NAME":"Foo"}])]
    monkeypatch.setattr(LeagueDashTeamStats, '__init__', lambda *a,**k: None)
    monkeypatch.setattr(LeagueDashTeamStats, 'get_data_frames', FakeStats().get_data_frames)

    teams = get_all_teams(season="2024-25")
    assert isinstance(teams, dict)
    assert teams[1] == "Foo"

def test_get_all_teams_handles_timeout(monkeypatch):
    monkeypatch.setattr(LeagueDashTeamStats, '__init__', lambda *a,**k: (_ for _ in ()).throw(ReadTimeout()))
    teams = get_all_teams(season="2024-25")
    assert teams == {}  # your client should return empty dict on timeout
