# artproject/app/__init__.py
from flask import Flask


def create_app():
    print("DEBUG: >>> INSIDE create_app() IN app/__init__.py <<<", flush=True)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_for_production_env' 

  

    # Register blueprints
    from .features.home import home_bp
    from .features.account import account_bp     # For create_account, view account
    from .features.order import order_bp       # For buy_ticket, buy_merchandise, view orders
    from .features.merchandise import merchandise_bp # For listing merchandise
    from .features.login import login_bp         # For login functionality

    app.register_blueprint(home_bp)
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(merchandise_bp, url_prefix='/merchandise')
    app.register_blueprint(login_bp, url_prefix='/auth') # For /auth/login, /auth/logout etc.

    return app