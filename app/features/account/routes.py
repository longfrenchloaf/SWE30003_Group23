# artproject/app/features/account/routes.py
from flask import render_template, redirect, url_for, flash
from . import account_bp
from .forms import RegistrationForm
from app.models.account import Account

@account_bp.route('/register', methods=['GET', 'POST'])
def create_account_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            new_account = Account.create(
                name=form.name.data,
                email=form.email.data,
                phoneNumber=form.phoneNumber.data,
                password=form.password.data
            )
            flash(f'Account created successfully for {new_account.name}! You can now log in.', 'success')
            return redirect(url_for('login.login_page'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred during account creation: {e}', 'danger')
            
    return render_template('create_account.html', form=form, title="Create New Account")

