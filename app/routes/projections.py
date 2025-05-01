from flask import Blueprint, render_template, flash, jsonify, request 
from requests.exceptions import ReadTimeout  
from nba_api.stats.endpoints import leaguedashplayerstats 
from nba_api.stats.endpoints.playergamelog import PlayerGameLog  

from ..services.nba_client import get_current_season, teams as nba_teams_client  
import app.services.ml_models as ml_models  

# Blueprint for all projection-related routes under /projections
bp = Blueprint('projections', __name__, url_prefix='/projections')


@bp.route('/', methods=['GET'])
def projections_page():
    # Determine season (query param or default)
    season = request.args.get('season') or get_current_season()
    # Optional team filter and display mode 'heuristic', 'ml', or 'both'
    team_id = request.args.get('team', type=int)
    mode    = request.args.get('mode', 'both')

    # Fetch per-game player stats for the season
    try:
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]  
        players = df.to_dict(orient='records')  
    except ReadTimeout:
        flash('Could not load player projections.')
        players = []

    # If a team is selected, filter players by TEAM_ID
    if team_id:
        players = [p for p in players if p.get('TEAM_ID') == team_id]

    # Compute simple heuristic projections over an 82-game season
    for p in players:
        avg_pts = p.get('PTS', 0)
        avg_reb = p.get('REB', 0)
        avg_ast = p.get('AST', 0)
        p['PROJECTED_PTS'] = round(avg_pts * 82, 1)
        p['PROJECTED_REB'] = round(avg_reb * 82, 1)
        p['PROJECTED_AST'] = round(avg_ast * 82, 1)

    # Load all NBA teams for the season selector
    try:
        all_teams = nba_teams_client.get_teams()
    except Exception:
        all_teams = []

    # Render the projections page with data and UI controls
    return render_template(
        'projections.html',
        players=players,
        season=season,
        all_teams=all_teams,
        selected_team=team_id,
        mode=mode
    )


@bp.route('/trend/<int:player_id>/<stat>')
def stat_trend(player_id, stat):
    """
    Display a player's cumulative stat trend vs. projected total.
    """
    season = get_current_season()

    # Fetch the player's game log for the season
    try:
        logs = PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star='Regular Season',
            timeout=15
        )
        df = logs.get_data_frames()[0]  
    except ReadTimeout:
        flash('Could not load game log for this player.')
        return render_template(
            'projections_trend.html',
            dates=[], values=[], projected=0,
            stat=stat, player_id=player_id, season=season
        )

    # Build cumulative series of the chosen stat
    dates = df['GAME_DATE'].tolist()
    cum   = df[stat].cumsum().tolist()

    # Compute heuristic projection: mean per game * 82
    avg = df[stat].mean() if not df.empty else 0
    projected = round(avg * 82, 1)

    # Render the trend chart template
    return render_template(
        'projections_trend.html',
        dates=dates,
        values=cum,
        projected=projected,
        stat=stat,
        player_id=player_id,
        season=season
    )


@bp.route('/api/player_projections_ml/<int:player_id>')
def ml_proj(player_id):
    """
    API endpoint returning ML-based season projection for a player.
    """
    season = get_current_season()
    try:
        # Use ML model to predict total points for the season
        proj_total = ml_models.predict_season_total(player_id, season)
        return jsonify({
            'PLAYER_ID':        player_id,
            'SEASON':           season,
            'PROJECTED_PTS_ML': round(proj_total, 1),
            'PROJECTED_PPG_ML': round(proj_total / 82, 2),
        })
    except FileNotFoundError:
        return jsonify({'error': 'Model not found. Please train first.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
