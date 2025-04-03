from flask import Flask, render_template, request
from nba_api.stats.static import players  # This provides a function to get players

app = Flask(__name__)

@app.route('/players')
def players_page():
    # Get the search query from the URL (if provided)
    query = request.args.get('q', '').strip()
    
    # Retrieve all players from the NBA API
    all_players = players.get_players()
    
    # If a search query is provided, filter the player list by the player's full name
    if query:
        filtered_players = [player for player in all_players
                            if query.lower() in player['full_name'].lower()]
    else:
        filtered_players = all_players

    # Pass the list of players and the query back to the template
    return render_template('players.html', players=filtered_players, query=query)

if __name__ == '__main__':
    app.run(debug=True)
