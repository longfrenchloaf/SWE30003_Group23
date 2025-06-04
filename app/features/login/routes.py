# artproject/app/features/login/routes.py
from flask import render_template, redirect, url_for, flash, request, session # <<< IMPORT session
from . import login_bp
from .forms import LoginForm
from app.models.account import Account
# from app.auth_utils import get_current_user_id # Can use this if you want

@login_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'user_id' in session: # Check if already logged in
        flash('You are already logged in.', 'info')
        return redirect(url_for('home.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        account = Account.get_by_email(email)

        if account and account.check_password(password):
            session['user_id'] = account.accountID # <<< STORE USER ID IN SESSION
            session['user_name'] = account.name   # <<< Optional: store name for display
            flash(f'Welcome back, {account.name}! You have been logged in.', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home.index'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html', title="Login", form=form)

@login_bp.route('/logout')
def logout_page():
    session.pop('user_id', None) # <<< REMOVE USER ID FROM SESSION
    session.pop('user_name', None) # <<< remove name
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('login.login_page'))