# app/__init__.py

import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .services.nba_client import nba_api_setup
from .routes import register_blueprints

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Initialize third‑party extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Configure NBA API headers once
    nba_api_setup()

    # Wire up all your route blueprints
    register_blueprints(app)

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
