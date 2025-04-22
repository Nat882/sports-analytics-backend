# from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
# from nba_api.stats.endpoints import (
#     scoreboardv2,
#     leaguedashplayerstats,
#     leaguedashteamstats,
#     commonplayerinfo
# )
# from nba_api.stats.static import teams
# from nba_api.stats.library.http import NBAStatsHTTP
# from requests.exceptions import ReadTimeout
# from werkzeug.security import generate_password_hash, check_password_hash
# from models.models import db, User, FavoritePlayer, FavoriteTeam
# from team_logos import team_logos

# import datetime
# import json

# # Update headers to avoid NBA API blocking
# NBAStatsHTTP.headers.update({
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Referer': 'https://www.nba.com/',
#     'Accept-Language': 'en-US,en;q=0.9'
# })

# # Flask setup
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nba_analytics.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# # Team info
# all_teams = teams.get_teams()
# team_dict = {team['id']: team['full_name'] for team in all_teams}

# def get_current_season():
#     now = datetime.datetime.now()
#     return f"{now.year}-{str(now.year + 1)[-2:]}" if now.month >= 10 else f"{now.year - 1}-{str(now.year)[-2:]}"

# # ---------- ROUTES ----------

# @app.route('/')
# def index():
#     game_date = datetime.datetime.now().strftime('%m/%d/%Y')
#     try:
#         scoreboard_data = scoreboardv2.ScoreboardV2(game_date=game_date, timeout=15)
#         games_df = scoreboard_data.get_data_frames()[0]
#         games = games_df.to_dict(orient='records')
#         for game in games:
#             visitor_team_id = game.get('VISITOR_TEAM_ID')
#             home_team_id = game.get('HOME_TEAM_ID')
#             game['AWAY_TEAM_NAME'] = team_dict.get(visitor_team_id, 'Unknown')
#             game['HOME_TEAM_NAME'] = team_dict.get(home_team_id, 'Unknown')
#             game['AWAY_TEAM_LOGO'] = team_logos.get(visitor_team_id)
#             game['HOME_TEAM_LOGO'] = team_logos.get(home_team_id)
#             game.setdefault('AWAY_TEAM_SCORE', 0)
#             game.setdefault('HOME_TEAM_SCORE', 0)
#     except ReadTimeout:
#         games = []
#     return render_template('index.html', games=games)

# @app.route('/games')
# def games_page():
#     return render_template('games.html')

# @app.route('/players')
# def players_page():
#     query = request.args.get('q', '').strip()
#     season = get_current_season()
#     try:
#         stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         player_stats = df.to_dict(orient='records')
#     except ReadTimeout:
#         return render_template('players.html', players=[], query=query, season=season, error="Could not load player stats.")

#     player_positions = {}
#     for player in player_stats:
#         pid = player['PLAYER_ID']
#         try:
#             info = commonplayerinfo.CommonPlayerInfo(player_id=pid)
#             info_df = info.get_data_frames()[0]
#             position = info_df.loc[0, 'POSITION'] if not info_df.empty else 'N/A'
#             player_positions[pid] = position
#         except Exception:
#             player_positions[pid] = 'N/A'

#     for player in player_stats:
#         player['TEAM_NAME'] = team_dict.get(player.get('TEAM_ID'), 'Unknown Team')
#         player['PLAYER_POSITION'] = player_positions.get(player['PLAYER_ID'], 'N/A')

#     if query:
#         player_stats = [p for p in player_stats if query.lower() in p['PLAYER_NAME'].lower()]

#     return render_template('players.html', players=player_stats, query=query, season=season)

# @app.route('/players/compare')
# def compare_players():
#     player_ids = request.args.getlist('player_ids')
#     if len(player_ids) != 2:
#         return "Select exactly two players.", 400

#     season = get_current_season()
#     try:
#         stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         player_stats = df.to_dict(orient='records')
#     except ReadTimeout:
#         return "Could not fetch player stats. Try again.", 504

#     for p in player_stats:
#         p['TEAM_NAME'] = team_dict.get(p.get('TEAM_ID'), 'Unknown')

#     selected = [p for p in player_stats if str(p['PLAYER_ID']) in player_ids]
#     if len(selected) != 2:
#         return "Selected players not found.", 404

#     return render_template('compare.html', players=selected, season=season)

# @app.route('/save_player', methods=['POST'])
# def save_player():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     player_id = request.form.get('player_id')
#     player_name = request.form.get('player_name')

#     favorite = FavoritePlayer.query.filter_by(player_id=player_id, user_id=session['user_id']).first()
#     if not favorite:
#         fav = FavoritePlayer(player_id=player_id, player_name=player_name, user_id=session['user_id'])
#         db.session.add(fav)
#         db.session.commit()
#         flash(f"{player_name} added to favorites!")

#     return redirect(url_for('players_page'))

# @app.route('/save_team', methods=['POST'])
# def save_team():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     team_id = request.form.get('team_id')
#     team_name = request.form.get('team_name')

#     favorite = FavoriteTeam.query.filter_by(team_id=team_id, user_id=session['user_id']).first()
#     if not favorite:
#         fav = FavoriteTeam(team_id=team_id, team_name=team_name, user_id=session['user_id'])
#         db.session.add(fav)
#         db.session.commit()
#         flash(f"{team_name} added to favorites!")

#     return redirect(url_for('teams_page'))

# @app.route('/projections')
# def projections_page():
#     season = get_current_season()
#     try:
#         stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         players = df.to_dict(orient='records')
#     except ReadTimeout:
#         players = []

#     for player in players:
#         games_played = player.get('GP', 0)
#         remaining = max(0, 82 - games_played)
#         player['PROJECTED_PTS'] = round(player['PTS'] * remaining, 1)
#         player['PROJECTED_REB'] = round(player['REB'] * remaining, 1)
#         player['PROJECTED_AST'] = round(player['AST'] * remaining, 1)

#     return render_template('projections.html', players=players, season=season)

# @app.route('/teams')
# def teams_page():
#     season = request.args.get('season', get_current_season())
#     try:
#         stats = leaguedashteamstats.LeagueDashTeamStats(
#             season=season,
#             per_mode_detailed='PerGame',
#             timeout=15
#         )
#         df = stats.get_data_frames()[0]
#         teams = df.to_dict(orient='records')
#     except (ReadTimeout, json.decoder.JSONDecodeError) as e:
#         print(f"Error fetching team stats: {e}")
#         flash("Could not load team stats. Please try again later.")
#         teams = []

#     for team in teams:
#         team['LOGO'] = team_logos.get(team['TEAM_ID'], '')

#     all_seasons = [f"{y}-{str(y+1)[-2:]}" for y in range(2015, datetime.datetime.now().year + 1)]
#     return render_template('teams.html', teams=teams, season=season, all_seasons=all_seasons)

# @app.route('/teams/compare')
# def compare_teams():
#     team_ids = request.args.getlist('team_ids')
#     if len(team_ids) != 2:
#         return "Select exactly two teams.", 400

#     season = get_current_season()
#     try:
#         stats = leaguedashteamstats.LeagueDashTeamStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         all_teams_data = df.to_dict(orient='records')
#     except ReadTimeout:
#         return "Could not fetch team stats. Try again later.", 504

#     selected = [t for t in all_teams_data if str(t['TEAM_ID']) in team_ids]
#     for team in selected:
#         team['LOGO'] = team_logos.get(team['TEAM_ID'], '')

#     return render_template('compare_teams.html', teams=selected, season=season)

# @app.route('/stats')
# def stats():
#     return render_template('stats.html')

# @app.route('/standings')
# def standings_page():
#     # Fetch standings data from an external API or source
#     standings_data = fetch_standings_data()
#     return render_template('standings.html', standings=standings_data)


# # ---------- AUTH ----------

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         identifier = request.form['username']
#         password = request.form['password']
#         user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
#         if user and check_password_hash(user.password, password):
#             session['user_id'] = user.id
#             session['username'] = user.username
#             flash('Welcome back, ' + user.username)
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid credentials.')
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out.')
#     return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
#         user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
#         if user_exists:
#             flash('Username or email already in use.')
#             return redirect(url_for('register'))
#         new_user = User(username=username, email=email, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Account created! You can now log in.')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/account', methods=['GET', 'POST'])
# def account():
#     if 'user_id' not in session:
#         flash('Please log in to view your account.')
#         return redirect(url_for('login'))

#     selected_type = request.form.get('type', 'player')  # default to players
#     favorite_players = []
#     favorite_teams = []
#     if selected_type == 'player':
#         favorite_players = FavoritePlayer.query.filter_by(user_id=session['user_id']).all()
#     elif selected_type == 'team':
#         favorite_teams = FavoriteTeam.query.filter_by(user_id=session['user_id']).all()

#     return render_template(
#         'account.html',
#         selected_type=selected_type,
#         favorite_players=favorite_players,
#         favorite_teams=favorite_teams
#     )

# # ---------- NEW API ENDPOINTS FOR FAVORITES ----------

# @app.route('/api/player_stats/<int:player_id>')
# def player_stats_api(player_id):
#     season = get_current_season()
#     try:
#         stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         player_data = df[df['PLAYER_ID'] == player_id]
#         if player_data.empty:
#             return jsonify({"error": "No data found for this player"}), 404
#         player_stats = player_data.iloc[0].to_dict()
#         return jsonify(player_stats)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/team_stats/<int:team_id>')
# def team_stats_api(team_id):
#     season = request.args.get('season', get_current_season())
#     try:
#         stats = leaguedashteamstats.LeagueDashTeamStats(season=season, per_mode_detailed='PerGame', timeout=15)
#         df = stats.get_data_frames()[0]
#         team_data = df[df['TEAM_ID'] == team_id]
#         if team_data.empty:
#             return jsonify({"error": "No data found for this team"}), 404
#         team_stats = team_data.iloc[0].to_dict()
#         return jsonify(team_stats)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # ---------- API FOR GAMES ----------

# @app.route('/api/games')
# def get_games():
#     game_date = datetime.datetime.now().strftime('%m/%d/%Y')
#     try:
#         scoreboard_data = scoreboardv2.ScoreboardV2(game_date=game_date, timeout=15)
#         game_header_df = scoreboard_data.game_header.get_data_frame()
#         line_score_df = scoreboard_data.line_score.get_data_frame()
#     except ReadTimeout:
#         return jsonify(games=[]), 504

#     games = game_header_df.to_dict(orient='records')
#     for game in games:
#         game['AWAY_TEAM_NAME'] = team_dict.get(game.get('VISITOR_TEAM_ID'), 'Unknown')
#         game['HOME_TEAM_NAME'] = team_dict.get(game.get('HOME_TEAM_ID'), 'Unknown')
#         game['AWAY_TEAM_SCORE'] = None
#         game['HOME_TEAM_SCORE'] = None

#         line_scores = line_score_df[line_score_df['GAME_ID'] == game['GAME_ID']]
#         for _, score in line_scores.iterrows():
#             if score['TEAM_ID'] == game['HOME_TEAM_ID']:
#                 game['HOME_TEAM_SCORE'] = score['PTS']
#             elif score['TEAM_ID'] == game['VISITOR_TEAM_ID']:
#                 game['AWAY_TEAM_SCORE'] = score['PTS']

#     return jsonify(games=games)

# # ---------- MAIN ----------

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
