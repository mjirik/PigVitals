# views_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import add_user, get_user_by_username

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('login_bp.login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user_by_username(username):
            flash('User already exists.')
        else:
            add_user(username, password)
            flash('User added successfully.')
            return redirect(url_for('admin_bp.admin'))
    return render_template('admin.html')
