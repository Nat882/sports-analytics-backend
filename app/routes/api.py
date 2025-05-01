from flask import Blueprint, jsonify, request  
import datetime                              
from requests.exceptions import ReadTimeout   

from ..services.nba_client import get_current_season, get_all_teams  
from nba_api.stats.endpoints import (                              
    ScoreboardV2,
    LeagueDashPlayerStats,
    LeagueDashTeamStats
)

# Blueprint for API routes under /api
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/games')
def get_games():
    """Return today’s NBA games with basic scores and team names."""
    # Format today's date for the NBA stats API (MM/DD/YYYY)
    game_date = datetime.datetime.now().strftime('%m/%d/%Y')
    try:
        # Fetch the scoreboard data
        sb = ScoreboardV2(game_date=game_date, timeout=15)
        # Get header info (game IDs, teams, status)
        header_df = sb.game_header.get_data_frame()
        # Get line score info (points per team)
        line_df = sb.line_score.get_data_frame()
    except ReadTimeout:
        # On timeout, return empty games list with HTTP 504
        return jsonify(games=[]), 504

    # Build a map of team IDs to team names
    team_dict = get_all_teams()
    # Convert header DataFrame to list of dicts
    games = header_df.to_dict(orient='records')

    # Enrich each game dict with team names and scores
    for game in games:
        gid = game['GAME_ID']
        # Lookup team names, defaulting to 'Unknown'
        game['AWAY_TEAM_NAME'] = team_dict.get(game['VISITOR_TEAM_ID'], 'Unknown')
        game['HOME_TEAM_NAME'] = team_dict.get(game['HOME_TEAM_ID'], 'Unknown')
        # Initialize score fields
        game['AWAY_TEAM_SCORE'] = None
        game['HOME_TEAM_SCORE'] = None
        # Fill in actual scores from line_df
        for _, row in line_df[line_df['GAME_ID'] == gid].iterrows():
            if row['TEAM_ID'] == game['HOME_TEAM_ID']:
                game['HOME_TEAM_SCORE'] = row['PTS']
            elif row['TEAM_ID'] == game['VISITOR_TEAM_ID']:
                game['AWAY_TEAM_SCORE'] = row['PTS']

    # Return JSON payload
    return jsonify(games=games)


@bp.route('/player_stats/<int:player_id>')
def player_stats_api(player_id):
    """Return per-game stats for a specific player."""
    # Determine the season to query
    season = get_current_season()
    try:
        # Fetch per-game player stats for the season
        stats = LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        # Filter to the requested player
        player_df = df[df['PLAYER_ID'] == player_id]
        if player_df.empty:
            # No data found for this player
            return jsonify({"error": "No data found for this player"}), 404
        # Return the first (and only) record as JSON
        return jsonify(player_df.iloc[0].to_dict())
    except Exception as e:
        # On any error, return a 500 with the error message
        return jsonify({"error": str(e)}), 500


@bp.route('/team_stats/<int:team_id>')
def team_stats_api(team_id):
    """Return per-game stats for a specific team. Optionally filter by query param `season`."""
    # Allow overriding season via query, default to current
    season = request.args.get('season', get_current_season())
    try:
        # Fetch per-game team stats for that season
        stats = LeagueDashTeamStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        # Filter to the requested team
        team_df = df[df['TEAM_ID'] == team_id]
        if team_df.empty:
            # No data found for this team
            return jsonify({"error": "No data found for this team"}), 404
        # Return the first (and only) record as JSON
        return jsonify(team_df.iloc[0].to_dict())
    except Exception as e:
        # On any error, return a 500 with the error message
        return jsonify({"error": str(e)}), 500
