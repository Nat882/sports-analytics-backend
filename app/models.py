from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    User account model integrating Flask-Login's UserMixin for session management.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    # Relationships for storing favorites
    favorites_players = db.relationship(
        'FavoritePlayer', backref='user', lazy=True
    )
    favorites_teams = db.relationship(
        'FavoriteTeam', backref='user', lazy=True
    )

class FavoritePlayer(db.Model):
    """
    Stores a user's favorite NBA players.
    """
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )

class FavoriteTeam(db.Model):
    """
    Stores a user's favorite NBA teams.
    """
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
