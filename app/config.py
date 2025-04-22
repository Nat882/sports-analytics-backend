import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this!')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///nba_analytics.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
