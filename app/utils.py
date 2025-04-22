import requests
from flask import current_app


def fetch_standings_data():
    """
    Fetch the current NBA standings from NBA's public data endpoint and return
    a list of simplified team standings.

    Returns:
        List[dict]: Each dictionary contains:
            - teamId (str)
            - win (str)
            - loss (str)
            - winPct (str)
            - conference (str)
            - division (str)
            - rankConference (str)
            - rankDivision (str)
    """
    url = 'https://data.nba.net/prod/v1/current/standings_all.json'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        teams = data.get('league', {}).get('standard', {}).get('teams', [])

        standings = []
        for team in teams:
            standings.append({
                'teamId': team.get('teamId'),
                'win': team.get('win'),
                'loss': team.get('loss'),
                'winPct': team.get('winPct'),
                'conference': team.get('confName'),
                'division': team.get('divName'),
                'rankConference': team.get('confRank'),
                'rankDivision': team.get('divRank'),
            })
        return standings

    except Exception as e:
        current_app.logger.error(f"Error fetching standings data: {e}")
        return []
