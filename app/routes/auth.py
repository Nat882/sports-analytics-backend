from flask import Blueprint, render_template, request, redirect, url_for, flash  
from werkzeug.security import generate_password_hash, check_password_hash  
from sqlalchemy.exc import SQLAlchemyError  
from flask_login import login_user, logout_user, login_required, current_user  
from ..models import User, FavoritePlayer, FavoriteTeam  
from ..extensions import db  

# Blueprint for authentication routes under /auth
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect authenticated users to home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Get form data
        ident = request.form.get('username', '').strip()
        pwd   = request.form.get('password', '')

        # Validate presence of credentials
        if not ident or not pwd:
            flash('Please enter both username/email and password.')
            return render_template('login.html')

        # Lookup user by username or email
        try:
            user = User.query.filter(
                (User.username == ident) | (User.email == ident)
            ).first()
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while accessing user data.')
            return render_template('login.html')

        # Verify password and log in
        if user and check_password_hash(user.password, pwd):
            login_user(user)
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials.')

    # Render login form
    return render_template('login.html')


@bp.route('/logout')
@login_required  # Only logged-in users can log out
def logout():
    logout_user()  # Clear session
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect authenticated users to home
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Get registration form data
        u   = request.form.get('username', '').strip()
        e   = request.form.get('email', '').strip()
        pwd = request.form.get('password', '')

        # Ensure all fields are filled
        if not u or not e or not pwd:
            flash('All fields are required.')
            return render_template('register.html')

        # Check for existing username or email
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

        # Hash password and create new user
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

    # Render registration form
    return render_template('register.html')


@bp.route('/account', methods=['GET', 'POST'])
@login_required  # Must be logged in to view account
def account():
    # Determine whether to show players or teams
    sel = request.form.get('type', 'player')
    if sel not in ['player', 'team']:
        sel = 'player'

    # Fetch user's favorites, handling potential DB errors
    try:
        fav_players = FavoritePlayer.query.filter_by(user_id=current_user.id).all() if sel == 'player' else []
        fav_teams   = FavoriteTeam.query.filter_by(user_id=current_user.id).all()   if sel == 'team'   else []
    except SQLAlchemyError:
        flash('Could not load account information.')
        fav_players = []
        fav_teams   = []

    # Render the account page with the selected favorites
    return render_template(
        'account.html',
        selected_type=sel,
        favorite_players=fav_players,
        favorite_teams=fav_teams
    )
