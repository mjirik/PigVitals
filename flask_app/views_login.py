# views_login.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import get_user_by_username
import logging

logger = logging.getLogger(__name__)

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login_bp.login'))

# @login_bp.route('/')
@login_bp.route('/home')
@login_required
def home():
    logger.debug("Home page accessed")

    return render_template('home.html', username=current_user.username)