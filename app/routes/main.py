from flask import Blueprint, render_template, flash
from requests.exceptions import ReadTimeout
from nba_api.stats.endpoints import ScoreboardV2, LeagueDashTeamStats, LeagueDashPlayerStats
from ..services.nba_client import get_current_season
from ..team_logos import team_logos
from ..utils     import fetch_standings_data



bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    game_date = __import__('datetime').datetime.now().strftime('%m/%d/%Y')
    try:
        data = ScoreboardV2(game_date=game_date, timeout=15)
        df = data.get_data_frames()[0]
        games = df.to_dict(orient='records')
        # enrich with names/logos
        from ..extensions import db  # if you need db here
        from ..services.nba_client import teams as all_teams
        team_dict = {t['id']: t['full_name'] for t in all_teams.get_teams()}
        for g in games:
            vid, hid = g['VISITOR_TEAM_ID'], g['HOME_TEAM_ID']
            g['AWAY_TEAM_NAME'] = team_dict.get(vid, 'Unknown')
            g['HOME_TEAM_NAME'] = team_dict.get(hid, 'Unknown')
            g['AWAY_TEAM_LOGO'] = team_logos.get(vid)
            g['HOME_TEAM_LOGO'] = team_logos.get(hid)
    except ReadTimeout:
        games = []
        flash("Couldn't load today's scoreboard.")
    return render_template('index.html', games=games)

@bp.route('/games')
def games_page():
    return render_template('games.html')

@bp.route('/projections')
def projections_page():
    season = get_current_season()
    try:
        stats = LeagueDashPlayerStats(season=season, per_mode_detailed='PerGame', timeout=15)
        df = stats.get_data_frames()[0]
        players = df.to_dict(orient='records')
    except ReadTimeout:
        players = []
        flash("Couldn't load projections.")
    for p in players:
        rem = max(0, 82 - p.get('GP', 0))
        p['PROJECTED_PTS'] = round(p['PTS'] * rem, 1)
        p['PROJECTED_REB'] = round(p['REB'] * rem, 1)
        p['PROJECTED_AST'] = round(p['AST'] * rem, 1)
    return render_template('projections.html', players=players, season=season)

@bp.route('/stats')
def stats_page():
    return render_template('stats.html')

@bp.route('/standings')
def standings_page():
    # you’ll implement fetch_standings_data somewhere else
    from ..utils import fetch_standings_data
    standings = fetch_standings_data()
    return render_template('standings.html', standings=standings)
