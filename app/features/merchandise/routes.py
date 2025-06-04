from flask import render_template, current_app
from . import merchandise_bp
from app.models.merchandise import Merchandise

@merchandise_bp.route('/')
def list_merchandise():
    all_merchandise = Merchandise.get_all()
    return render_template('merchandise_list.html', merchandise_items=all_merchandise, title="Browse Merchandise")