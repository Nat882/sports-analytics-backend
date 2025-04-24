from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, FavoritePlayer, FavoriteTeam
from ..extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, go home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        ident = request.form.get('username', '').strip()
        pwd   = request.form.get('password', '')

        if not ident or not pwd:
            flash('Please enter both username/email and password.')
            return render_template('login.html')

        try:
            user = User.query.filter(
                (User.username == ident) | (User.email == ident)
            ).first()
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while accessing user data.')
            return render_template('login.html')

        if user and check_password_hash(user.password, pwd):
            login_user(user)
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials.')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        u   = request.form.get('username', '').strip()
        e   = request.form.get('email', '').strip()
        pwd = request.form.get('password', '')

        if not u or not e or not pwd:
            flash('All fields are required.')
            return render_template('register.html')

        try:
            existing = User.query.filter(
                (User.username == u) | (User.email == e)
            ).first()
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred during registration.')
            return render_template('register.html')

        if existing:
            flash('Username or email already in use.')
            return render_template('register.html')

        hashed = generate_password_hash(pwd, method='pbkdf2:sha256')
        new_user = User(username=u, email=e, password=hashed)
        try:
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash('Could not create account. Try again.')
            return render_template('register.html')

        flash('Account created! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    sel = request.form.get('type', 'player')
    if sel not in ['player', 'team']:
        sel = 'player'

    try:
        fav_players = FavoritePlayer.query.filter_by(user_id=current_user.id).all() if sel=='player' else []
        fav_teams   = FavoriteTeam.query.filter_by(user_id=current_user.id).all()   if sel=='team'   else []
    except SQLAlchemyError:
        flash('Could not load account information.')
        fav_players = []
        fav_teams   = []

    return render_template(
        'account.html',
        selected_type=sel,
        favorite_players=fav_players,
        favorite_teams=fav_teams
    )
