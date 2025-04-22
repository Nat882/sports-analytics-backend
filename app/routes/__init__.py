from .main       import bp as main_bp
from .auth       import bp as auth_bp
from .games      import bp as games_bp
from .players     import bp as players_bp
from .projections import bp as projections_bp
from .teams      import bp as teams_bp
from .api        import bp as api_bp

def register_blueprints(app):
    for bp in (main_bp, auth_bp, games_bp, players_bp, projections_bp, teams_bp, api_bp):
        app.register_blueprint(bp)
