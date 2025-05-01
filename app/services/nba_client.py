# app/services/nba_client.py

import datetime
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueDashTeamStats
from requests.exceptions import ReadTimeout

def nba_api_setup():
    NBAStatsHTTP.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Referer': 'https://www.nba.com/',
        'Accept-Language': 'en-US,en;q=0.9'
    })

def get_current_season():
    now = datetime.datetime.now()
    if now.month >= 10:
        start = now.year
        end = str(now.year + 1)[-2:]
    else:
        start = now.year - 1
        end = str(now.year)[-2:]
    return f"{start}-{end}"

def get_all_teams(season=None):
    try:
        stats = LeagueDashTeamStats(
            season=season,
            timeout=15
        )
        df = stats.get_data_frames()[0]
        return {row['TEAM_ID']: row['TEAM_NAME'] for _, row in df.iterrows()}
    except ReadTimeout:
        return {}