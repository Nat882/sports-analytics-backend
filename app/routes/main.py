from flask import Blueprint, render_template, flash 
from requests.exceptions import ReadTimeout        
from nba_api.stats.endpoints import ScoreboardV2, LeagueDashTeamStats, LeagueDashPlayerStats  
from ..services.nba_client import get_current_season  
from ..team_logos import team_logos                  
from ..utils import fetch_standings_data             

# Blueprint for top-level pages 
bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    # Determine today's date for the scoreboard API
    game_date = __import__('datetime').datetime.now().strftime('%m/%d/%Y')
    try:
        # Fetch today's games from the NBA API
        data = ScoreboardV2(game_date=game_date, timeout=15)
        df = data.get_data_frames()[0]
        games = df.to_dict(orient='records')

        # Enrich each game with team names and logos
        from ..services.nba_client import teams as all_teams
        team_dict = {t['id']: t['full_name'] for t in all_teams.get_teams()}
        for g in games:
            vid, hid = g['VISITOR_TEAM_ID'], g['HOME_TEAM_ID']
            g['AWAY_TEAM_NAME'] = team_dict.get(vid, 'Unknown')
            g['HOME_TEAM_NAME'] = team_dict.get(hid, 'Unknown')
            g['AWAY_TEAM_LOGO'] = team_logos.get(vid)
            g['HOME_TEAM_LOGO'] = team_logos.get(hid)

    except ReadTimeout:
        # On timeout, show empty list and flash an error
        games = []
        flash("Couldn't load today's scoreboard.")

    # Render the homepage with the games list
    return render_template('index.html', games=games)


@bp.route('/games')
def games_page():
    # Static page for upcoming or past games
    return render_template('games.html')


@bp.route('/projections')
def projections_page():
    # Get the current season for projections
    season = get_current_season()
    try:
        # Fetch per-game player stats for heuristic projections
        stats = LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        players = df.to_dict(orient='records')
    except ReadTimeout:
        # On timeout, flash error and fall back to empty list
        players = []
        flash("Couldn't load projections.")

    # Compute remaining games and simple projections
    for p in players:
        played = p.get('GP', 0)
        rem = max(0, 82 - played)
        p['PROJECTED_PTS'] = round(p['PTS'] * rem, 1)
        p['PROJECTED_REB'] = round(p['REB'] * rem, 1)
        p['PROJECTED_AST'] = round(p['AST'] * rem, 1)

    # Render the projections page
    return render_template('projections.html', players=players, season=season)


@bp.route('/stats')
def stats_page():
    # Static page for advanced stats or other visualizations
    return render_template('stats.html')


@bp.route('/standings')
def standings_page():
    # Fetch standings data (e.g., via web scrape or external API)
    standings = fetch_standings_data()
    # Render the standings table
    return render_template('standings.html', standings=standings)
