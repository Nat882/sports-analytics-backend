# app/services/nba_client.py

import datetime
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.static import teams

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

def get_all_teams():
    """
    Fetch the static list of all NBA teams once and return it as a dict:
      { team_id: full_name, ... }
    """
    all_teams = teams.get_teams()
    return {t['id']: t['full_name'] for t in all_teams}
