from flask import Blueprint, render_template, request, redirect, url_for, flash
from requests.exceptions import ReadTimeout
from nba_api.stats.endpoints import LeagueDashPlayerStats, CommonPlayerInfo
from flask_login import current_user, login_required

from ..services.nba_client import get_current_season, teams as all_teams
from ..models import FavoritePlayer
from ..extensions import db
from ..team_logos import team_logos

bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('/')
def list_players():
    query = request.args.get('q', '').strip()
    season = get_current_season()
    try:
        stats = LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        players = df.to_dict(orient='records')
    except ReadTimeout:
        return render_template(
            'players.html',
            players=[],
            query=query,
            season=season,
            error="Could not load player stats."
        )

    # fetch positions
    positions = {}
    for p in players:
        pid = p['PLAYER_ID']
        try:
            info = CommonPlayerInfo(player_id=pid).get_data_frames()[0]
            positions[pid] = info.at[0, 'POSITION'] if not info.empty else 'N/A'
        except:
            positions[pid] = 'N/A'

    team_dict = {t['id']: t['full_name'] for t in all_teams.get_teams()}
    for p in players:
        p['TEAM_NAME'] = team_dict.get(p['TEAM_ID'], 'Unknown')
        p['POSITION']  = positions.get(p['PLAYER_ID'], 'N/A')
        p['LOGO']      = team_logos.get(p['TEAM_ID'])

    if query:
        players = [
            p for p in players
            if query.lower() in p['PLAYER_NAME'].lower()
        ]

    return render_template(
        'players.html',
        players=players,
        query=query,
        season=season
    )

@bp.route('/compare')
def compare_players():
    ids = request.args.getlist('player_ids')
    if len(ids) != 2:
        return "Select exactly two players.", 400

    season = get_current_season()
    try:
        stats = LeagueDashPlayerStats(
            season=season,
            per_mode_detailed='PerGame',
            timeout=15
        )
        df = stats.get_data_frames()[0]
        all_players = df.to_dict(orient='records')
    except ReadTimeout:
        return "Could not fetch stats.", 504

    team_dict = {t['id']: t['full_name'] for t in all_teams.get_teams()}
    selected = [p for p in all_players if str(p['PLAYER_ID']) in ids]
    for p in selected:
        p['TEAM_NAME'] = team_dict.get(p['TEAM_ID'], 'Unknown')

    if len(selected) != 2:
        return "Players not found.", 404

    return render_template(
        'compare.html',
        players=selected,
        season=season
    )

@bp.route('/save', methods=['POST'])
@login_required
def save_player():
    pid  = request.form['player_id']
    name = request.form['player_name']

    fav = FavoritePlayer.query.filter_by(
        player_id=pid,
        user_id=current_user.id
    ).first()

    if not fav:
        db.session.add(FavoritePlayer(
            player_id=pid,
            player_name=name,
            user_id=current_user.id
        ))
        db.session.commit()
        flash(f"{name} added to favorites!")

    return redirect(url_for('players.list_players'))
