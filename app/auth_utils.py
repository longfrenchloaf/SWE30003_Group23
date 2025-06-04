# artproject/app/auth_utils.py
from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'warning')
            # Store the intended destination to redirect after login
            return redirect(url_for('login.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    return session.get('user_id')

def get_current_user():
    from app.models.account import Account # Import here to avoid circular dependencies at module load
    user_id = get_current_user_id()
    if user_id:
        return Account.get_by_id(user_id)
    return None