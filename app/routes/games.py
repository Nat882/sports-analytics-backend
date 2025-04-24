from flask import Blueprint, render_template, request, flash
from requests.exceptions import ReadTimeout
from datetime import datetime, timedelta
from ..services.nba_client import get_all_teams
from ..team_logos import team_logos
from nba_api.stats.library.http import NBAStatsHTTP
import requests

bp = Blueprint('games', __name__, url_prefix='/games')

@bp.route('/', methods=['GET'])
def games_page():
    # Determine the selected date (ISO) and display date
    date_param = request.args.get('date')
    try:
        if date_param:
            dt = datetime.strptime(date_param, '%Y-%m-%d')
        else:
            dt = datetime.now() - timedelta(days=1)
    except Exception:
        flash("Invalid date, defaulting to yesterday.")
        dt = datetime.now() - timedelta(days=1)

    selected_date = dt.strftime('%Y-%m-%d')  # for the <input>
    display_date  = dt.strftime('%d/%m/%Y')  # for the <h1>
    game_date     = dt.strftime('%m/%d/%Y')  # for the NBA API

    games = []
    teams = get_all_teams()
    headers = NBAStatsHTTP.headers

    try:
        # Manual fetch to avoid WinProbability KeyError
        url = 'https://stats.nba.com/stats/scoreboardv2'
        params = {'GameDate': game_date, 'LeagueID': '00'}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        data = resp.json()

        # Extract GameHeader and LineScore
        rs = data.get('resultSets', [])
        header_set = next((r for r in rs if r.get('name') == 'GameHeader'), None)
        line_set   = next((r for r in rs if r.get('name') == 'LineScore'), None)
        if not header_set or not line_set:
            raise ValueError('Missing GameHeader or LineScore in API response')

        hdr_cols = header_set['headers']
        hdr_rows = header_set['rowSet']
        ln_cols  = line_set['headers']
        ln_rows  = line_set['rowSet']

        # Build score map by GAME_ID and TEAM_ID
        scores = {}
        for lr in ln_rows:
            rec = dict(zip(ln_cols, lr))
            gid, tid = rec['GAME_ID'], rec['TEAM_ID']
            scores.setdefault(gid, {})[tid] = rec.get('PTS', 0)

        # Construct games list
        for hr in hdr_rows:
            rec = dict(zip(hdr_cols, hr))
            gid = rec['GAME_ID']
            vid = rec['VISITOR_TEAM_ID']
            hid = rec['HOME_TEAM_ID']
            games.append({
                'AWAY_TEAM_NAME':  teams.get(vid, 'Unknown'),
                'HOME_TEAM_NAME':  teams.get(hid, 'Unknown'),
                'AWAY_TEAM_LOGO':  team_logos.get(vid, ''),
                'HOME_TEAM_LOGO':  team_logos.get(hid, ''),
                'AWAY_TEAM_SCORE': scores.get(gid, {}).get(vid, 0),
                'HOME_TEAM_SCORE': scores.get(gid, {}).get(hid, 0),
                'GAME_STATUS_TEXT': rec.get('GAME_STATUS_TEXT'),
                'GAME_TIME_EST':    rec.get('GAME_TIME_EST')
            })
    except (ReadTimeout, ValueError, requests.RequestException) as e:
        flash(f"Could not load games for {display_date}: {e}")
        games = []

    return render_template(
        'games.html',
        games=games,
        selected_date=selected_date,
        display_date=display_date
    )
