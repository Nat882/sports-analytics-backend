# app/services/nba_client.py

import datetime
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueDashTeamStats
from requests.exceptions import ReadTimeout

def nba_api_setup():
    """
    Apply custom headers so the NBA API doesn’t block our requests.
    Call this once when the app starts.
    """
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
    """
    Return the current NBA season string, e.g. "2024-25".
    If today is October or later, it’s the new season; otherwise it’s last year.
    """
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