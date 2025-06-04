# artproject/app/features/home/routes.py
from flask import render_template
from . import home_bp
from app.models.merchandise import Merchandise
from app.models.account import Account

@home_bp.route('/')
def index():
    sample_merch = [] # Default to empty
    raw_merch_list = None # To store the direct output of get_all()
    try:
        raw_merch_list = Merchandise.get_all()
        if isinstance(raw_merch_list, list):
            sample_merch = raw_merch_list[:3]
        else:
            print(f"ERROR home.index: Merchandise.get_all() did not return a list. sample_merch remains empty.")
        sample_accounts = Account.get_all()[:2] 

    except Exception as e:
        # sample_merch will remain [] due to initialization above
        sample_accounts = []

    return render_template('home.html',
                           sample_merch=sample_merch,
                           sample_accounts=sample_accounts,
                           title="Welcome to ART System")