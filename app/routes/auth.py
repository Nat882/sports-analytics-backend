from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ident = request.form['username']
        pwd = request.form['password']
        user = User.query.filter((User.username==ident)|(User.email==ident)).first()
        if user and check_password_hash(user.password, pwd):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!")
            return redirect(url_for('main.index'))
        flash('Invalid credentials.')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        e = request.form['email']
        p = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        if User.query.filter((User.username==u)|(User.email==e)).first():
            flash('Username or email already in use.')
            return redirect(url_for('auth.register'))
        db.session.add(User(username=u, email=e, password=p))
        db.session.commit()
        flash('Account created! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    from ..models import FavoritePlayer, FavoriteTeam
    sel = request.form.get('type', 'player')
    players = FavoritePlayer.query.filter_by(user_id=session['user_id']).all() if sel=='player' else []
    teams   = FavoriteTeam.query.filter_by(user_id=session['user_id']).all()   if sel=='team'   else []
    return render_template('account.html', selected_type=sel, favorite_players=players, favorite_teams=teams)
