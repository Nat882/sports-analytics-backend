from flask import Blueprint, jsonify, request
import datetime
from requests.exceptions import ReadTimeout

from ..services.nba_client import get_current_season, get_all_teams
from nba_api.stats.endpoints import (
    ScoreboardV2,
    LeagueDashPlayerStats,
    LeagueDashTeamStats
)

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/games')
def get_games():
    """Return today’s NBA games with basic scores and team names."""
    game_date = datetime.datetime.now().strftime('%m/%d/%Y')
    try:
        sb = ScoreboardV2(game_date=game_date, timeout=15)
        header_df = sb.game_header.get_data_frame()
        line_df = sb.line_score.get_data_frame()
    except ReadTimeout:
        return jsonify(games=[]), 504

    team_dict = get_all_teams()
    games = header_df.to_dict(orient='records')
    for game in games:
        gid = game['GAME_ID']
        game['AWAY_TEAM_NAME'] = team_dict.get(game['VISITOR_TEAM_ID'], 'Unknown')
        game['HOME_TEAM_NAME'] = team_dict.get(game['HOME_TEAM_ID'], 'Unknown')
        game['AWAY_TEAM_SCORE'] = None
        game['HOME_TEAM_SCORE'] = None
        # fill in final scores
        for _, row in line_df[line_df['GAME_ID'] == gid].iterrows():
            if row['TEAM_ID'] == game['HOME_TEAM_ID']:
                game['HOME_TEAM_SCORE'] = row['PTS']
            elif row['TEAM_ID'] == game['VISITOR_TEAM_ID']:
                game['AWAY_TEAM_SCORE'] = row['PTS']
    return jsonify(games=games)

@bp.route('/player_stats/<int:player_id>')
def player_stats_api(player_id):
    """Return per-game stats for a specific player."""
    season = get_current_season()
    try:
        stats = LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        player_df = df[df['PLAYER_ID'] == player_id]
        if player_df.empty:
            return jsonify({"error": "No data found for this player"}), 404
        return jsonify(player_df.iloc[0].to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/team_stats/<int:team_id>')
def team_stats_api(team_id):
    """Return per-game stats for a specific team. Optionally filter by query param `season`."""
    season = request.args.get('season', get_current_season())
    try:
        stats = LeagueDashTeamStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        team_df = df[df['TEAM_ID'] == team_id]
        if team_df.empty:
            return jsonify({"error": "No data found for this team"}), 404
        return jsonify(team_df.iloc[0].to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
