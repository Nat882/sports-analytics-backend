from flask import Blueprint, render_template, flash
from flask import Blueprint, render_template, flash
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints.playergamelog import PlayerGameLog
from requests.exceptions import ReadTimeout
from ..services.nba_client import get_current_season

bp = Blueprint('projections', __name__, url_prefix='/projections')

@bp.route('/', methods=['GET'])
def projections_page():
    # Determine the current season (e.g. '2024-25')
    season = get_current_season()
    try:
        # Fetch per-game player stats for the season
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

    # Compute projections based on games played and per-game averages
    for p in players:
        games_played = p.get('GP', 0) or 0
        remaining = max(0, 82 - games_played)
        p['PROJECTED_PTS'] = round(p.get('PTS', 0) * remaining, 1)
        p['PROJECTED_REB'] = round(p.get('REB', 0) * remaining, 1)
        p['PROJECTED_AST'] = round(p.get('AST', 0) * remaining, 1)

    return render_template('projections.html', players=players, season=season)

@bp.route('/trend/<int:player_id>/<stat>')
def stat_trend(player_id, stat):
    """
    Display player's cumulative stat trend vs projection.
    """
    season = get_current_season()
    try:
        # Fetch game-by-game logs for this player in the regular season
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
            stat=stat, player_id=player_id,
            season=season
        )

    # Prepare date labels and cumulative stat values
    dates = df['GAME_DATE'].tolist()
    vals  = df[stat].tolist()
    cum   = []
    total = 0
    for v in vals:
        total += v
        cum.append(total)

    # Calculate projection same as in projections_page
    gp = df.shape[0]
    remaining = max(0, 82 - gp)
    per_game_avg = df[stat].mean() if gp else 0
    projected = round(per_game_avg * (gp + remaining), 1)

    return render_template(
        'projections_trend.html',
        dates=dates,
        values=cum,
        projected=projected,
        stat=stat,
        player_id=player_id,
        season=season
    )
