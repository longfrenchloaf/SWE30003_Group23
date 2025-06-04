from flask import Blueprint

home_bp = Blueprint('home', __name__, template_folder='templates')

from . import routes # Import routes after blueprint creation to avoid circular dependency