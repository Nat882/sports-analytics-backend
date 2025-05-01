from flask import Blueprint, render_template, request, redirect, url_for, flash  
from requests.exceptions import ReadTimeout  
from nba_api.stats.endpoints import LeagueDashTeamStats  
from flask_login import current_user, login_required  

from ..services.nba_client import get_current_season  
from ..team_logos import team_logos  
from ..models import FavoriteTeam  
from ..extensions import db  

# Blueprint for team-related routes
bp = Blueprint('teams', __name__, url_prefix='/teams')

@bp.route('/')
def list_teams():
    # Get season from query or default to current
    season = request.args.get('season', get_current_season())
    try:
        # Fetch per-game stats for all teams
        stats = LeagueDashTeamStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]  # First DataFrame contains team stats
        teams = df.to_dict(orient='records')  
    except (ReadTimeout, ValueError):
        # Show error message and fallback to empty list
        flash("Could not load team stats.")
        teams = []

    # Attach logo URL to each team record
    for t in teams:
        t['LOGO'] = team_logos.get(t['TEAM_ID'], '')

    # Generate list of seasons
    all_seasons = [
        f"{y}-{str(y+1)[-2:]}"
        for y in range(2015, __import__('datetime').datetime.now().year + 1)
    ]

    # Render the template with teams and season data
    return render_template(
        'teams.html',
        teams=teams,
        season=season,
        all_seasons=all_seasons
    )

@bp.route('/compare')
def compare_teams():
    # Expect exactly two team IDs for comparison
    ids = request.args.getlist('team_ids')
    if len(ids) != 2:
        return "Select exactly two teams.", 400

    season = get_current_season()  
    try:
        stats = LeagueDashTeamStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        all_teams = df.to_dict(orient='records')
    except ReadTimeout:
        return "Could not fetch team stats.", 504

    # Filter stats for the two selected teams
    selected = [t for t in all_teams if str(t['TEAM_ID']) in ids]
    for t in selected:
        t['LOGO'] = team_logos.get(t['TEAM_ID'], '')

    # Return 404 if teams not found
    if len(selected) != 2:
        return "Teams not found.", 404

    # Render comparison template
    return render_template(
        'compare_teams.html',
        teams=selected,
        season=season
    )

@bp.route('/save', methods=['POST'])
@login_required  # Ensure user is logged in to save favorite team
def save_team():
    # Extract team ID and name from form data
    tid  = request.form['team_id']
    name = request.form['team_name']

    # Check if favorite already exists for this user
    fav = FavoriteTeam.query.filter_by(
        team_id=tid,
        user_id=current_user.id
    ).first()

    if not fav:
        # Add new favorite team and commit
        db.session.add(FavoriteTeam(
            team_id=tid,
            team_name=name,
            user_id=current_user.id
        ))
        db.session.commit()
        flash(f"{name} added to favorites!")

    # Redirect back to team list
    return redirect(url_for('teams.list_teams'))
