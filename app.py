from flask import Flask, render_template, jsonify, request
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2, leaguedashplayerstats
from nba_api.stats.static import teams
import datetime

# Import team logos mapping 
from team_logos import team_logos

app = Flask(__name__)

# Create a dictionary to map team IDs to team names (used on other pages)
all_teams = teams.get_teams()
team_dict = {team['id']: team['full_name'] for team in all_teams}

@app.route('/')
def index():
    # Uses scoreboardv2 to display game information for today's date.
    game_date = datetime.datetime.now().strftime('%m/%d/%Y')
    scoreboard_data = scoreboardv2.ScoreboardV2(game_date=game_date)
    data_frames = scoreboard_data.get_data_frames()
    games = []
    if data_frames:
        games_df = data_frames[0]
        games = games_df.to_dict(orient='records')
        # Map team IDs to team names and add logos
        for game in games:
            visitor_team_id = game.get('VISITOR_TEAM_ID')
            home_team_id = game.get('HOME_TEAM_ID')
            game['AWAY_TEAM_NAME'] = team_dict.get(visitor_team_id, 'Unknown Team')
            game['HOME_TEAM_NAME'] = team_dict.get(home_team_id, 'Unknown Team')
            game['AWAY_TEAM_LOGO'] = team_logos.get(visitor_team_id)
            game['HOME_TEAM_LOGO'] = team_logos.get(home_team_id)
    return render_template('index.html', games=games)

@app.route('/games')
def games():
    return render_template('games.html')

def get_current_season():
    """Compute the current NBA season string in the format 'YYYY-YY'."""
    now = datetime.datetime.now()
    # NBA season typically starts in October.
    if now.month >= 10:
        season_start = now.year
        season_end = str(now.year + 1)[-2:]
    else:
        season_start = now.year - 1
        season_end = str(now.year)[-2:]
    return f"{season_start}-{season_end}"

@app.route('/players')
def players_page():
    # Get the search query from the query parameters.
    query = request.args.get('q', '').strip()
    
    # Compute the current season string 
    season = get_current_season()
    # Fetch league-wide player stats for the current season.
    stats_endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed='PerGame'
    )
    df = stats_endpoint.get_data_frames()[0]
    player_stats = df.to_dict(orient='records')

    # Add the full team name to each player's data using TEAM_ID.
    for player in player_stats:
        team_id = player.get('TEAM_ID')
        player['TEAM_NAME'] = team_dict.get(team_id, "Unknown Team")

    # If a search query is provided, filter the list by the player's full name
    if query:
        filtered_stats = [
            player for player in player_stats
            if query.lower() in player['PLAYER_NAME'].lower()
        ]
    else:
        filtered_stats = player_stats

    return render_template('players.html', players=filtered_stats, query=query, season=season)

@app.route('/players/compare')
def compare_players():
    # Get the list of selected player IDs from the query parameters.
    player_ids = request.args.getlist('player_ids')
    if len(player_ids) != 2:
        return "Please select exactly two players for comparison.", 400

    # Compute the current season string
    season = get_current_season()

    # Fetch league-wide player stats for the current season.
    stats_endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        per_mode_detailed='PerGame'
    )
    df = stats_endpoint.get_data_frames()[0]
    player_stats = df.to_dict(orient='records')

    # Add the full team name to each player's data using TEAM_ID.
    for player in player_stats:
        team_id = player.get('TEAM_ID')
        player['TEAM_NAME'] = team_dict.get(team_id, "Unknown Team")

    # Filter to include only the players with IDs in the submitted list.
    selected_players = [
        player for player in player_stats
        if str(player['PLAYER_ID']) in player_ids
    ]

    if len(selected_players) != 2:
        return "Could not find data for the selected players.", 404

    return render_template('compare.html', players=selected_players, season=season)


@app.route('/teams')
def teams_page():
    return render_template('teams.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/games')
def get_games():
    game_date = datetime.datetime.now().strftime('%m/%d/%Y')
    scoreboard_data = scoreboardv2.ScoreboardV2(game_date=game_date)
    data_frames = scoreboard_data.get_data_frames()
    games = []
    if data_frames:
        games_df = data_frames[0]
        games = games_df.to_dict(orient='records')
        for game in games:
            visitor_team_id = game.get('VISITOR_TEAM_ID')
            home_team_id = game.get('HOME_TEAM_ID')
            game['AWAY_TEAM_NAME'] = team_dict.get(visitor_team_id, 'Unknown Team')
            game['HOME_TEAM_NAME'] = team_dict.get(home_team_id, 'Unknown Team')
    return jsonify(games=games)

if __name__ == '__main__':
    app.run(debug=True)
