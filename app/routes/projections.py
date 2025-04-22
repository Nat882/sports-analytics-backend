from flask import Blueprint, render_template

bp = Blueprint('projections', __name__, url_prefix='/projections')

@bp.route('/')
def projections_page():
    
    return render_template('projections.html')