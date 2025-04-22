from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from requests.exceptions import ReadTimeout
from nba_api.stats.endpoints import LeagueDashTeamStats
from ..services.nba_client import get_current_season
from ..team_logos import team_logos
from ..models import FavoriteTeam
from ..extensions import db

bp = Blueprint('teams', __name__, url_prefix='/teams')

@bp.route('/')
def list_teams():
    season = request.args.get('season', get_current_season())
    try:
        stats = LeagueDashTeamStats(season=season, per_mode_detailed='PerGame', timeout=15)
        df = stats.get_data_frames()[0]
        teams = df.to_dict(orient='records')
    except (ReadTimeout, ValueError):
        flash("Could not load team stats.")
        teams = []

    for t in teams:
        t['LOGO'] = team_logos.get(t['TEAM_ID'], '')
    all_seasons = [f"{y}-{str(y+1)[-2:]}" for y in range(2015, __import__('datetime').datetime.now().year+1)]
    return render_template('teams.html', teams=teams, season=season, all_seasons=all_seasons)

@bp.route('/compare')
def compare_teams():
    ids = request.args.getlist('team_ids')
    if len(ids) != 2:
        return "Select exactly two teams.", 400
    season = get_current_season()
    try:
        stats = LeagueDashTeamStats(season=season, per_mode_detailed='PerGame', timeout=15)
        df = stats.get_data_frames()[0]
        all_teams = df.to_dict(orient='records')
    except ReadTimeout:
        return "Could not fetch team stats.", 504

    selected = [t for t in all_teams if str(t['TEAM_ID']) in ids]
    for t in selected:
        t['LOGO'] = team_logos.get(t['TEAM_ID'], '')
    if len(selected) != 2:
        return "Teams not found.", 404
    return render_template('compare_teams.html', teams=selected, season=season)

@bp.route('/save', methods=['POST'])
def save_team():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    tid = request.form['team_id']
    name = request.form['team_name']
    fav = FavoriteTeam.query.filter_by(team_id=tid, user_id=session['user_id']).first()
    if not fav:
        db.session.add(FavoriteTeam(team_id=tid, team_name=name, user_id=session['user_id']))
        db.session.commit()
        flash(f"{name} added to favorites!")
    return redirect(url_for('teams.list_teams'))
