from flask import Blueprint, render_template

bp = Blueprint('games', __name__, url_prefix='/games')

@bp.route('/')
def games_page():
    return render_template('games.html')
