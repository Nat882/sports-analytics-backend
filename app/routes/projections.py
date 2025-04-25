# app/routes/projections.py

from flask import Blueprint, render_template, flash, jsonify, request
from requests.exceptions import ReadTimeout
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints.playergamelog import PlayerGameLog

from ..services.nba_client import get_current_season, teams as nba_teams_client
import app.services.ml_models as ml_models  # note the module import

bp = Blueprint('projections', __name__, url_prefix='/projections')

@bp.route('/', methods=['GET'])
def projections_page():
    season = get_current_season()
    team_id = request.args.get('team', type=int)
    mode    = request.args.get('mode', 'heuristic')  # 'heuristic' or 'ml'

    # 1) Fetch per-game stats
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

    # 2) Optional team filter
    if team_id:
        players = [p for p in players if p.get('TEAM_ID') == team_id]

    # 3) Compute heuristic projections
    for p in players:
        gp = p.get('GP') or 0
        rem = max(0, 82 - gp)
        p['PROJECTED_PTS'] = round(p.get('PTS', 0) * rem, 1)
        p['PROJECTED_REB'] = round(p.get('REB', 0) * rem, 1)
        p['PROJECTED_AST'] = round(p.get('AST', 0) * rem, 1)

    # 4) Load list of all teams for your dropdown
    try:
        all_teams = nba_teams_client.get_teams()
    except Exception:
        all_teams = []

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
    Display a player's cumulative stat trend vs projection.
    """
    season = get_current_season()

    # 1) Fetch per-game logs
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

    # 2) Build cumulative series
    dates = df['GAME_DATE'].tolist()
    vals  = df[stat].tolist()
    cum   = []
    total = 0
    for v in vals:
        total += v
        cum.append(total)

    # 3) Heuristic projection
    gp = len(vals)
    avg = df[stat].mean() if gp else 0
    projected = round(avg * (gp + max(0, 82 - gp)), 1)

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
    Returns ML‐based season projection for a given player.
    """
    season = get_current_season()
    try:
        # call through the ml_models module:
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
