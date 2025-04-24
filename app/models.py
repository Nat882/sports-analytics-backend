# app/models.py

from .extensions import db
from flask_login import UserMixin  # if you integrate Flask-Login

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email    = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    favorites_players = db.relationship('FavoritePlayer', backref='user', lazy=True)
    favorites_teams   = db.relationship('FavoriteTeam',   backref='user', lazy=True)

class FavoritePlayer(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    player_id   = db.Column(db.Integer, nullable=False)
    player_name = db.Column(db.String(100))
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FavoriteTeam(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    team_id   = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(100))
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
