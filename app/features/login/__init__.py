# artproject/app/features/login/__init__.py
from flask import Blueprint

login_bp = Blueprint(
    'login',  # 1. Blueprint name (used internally by Flask, e.g., for url_for)
    __name__, # 2. Import name (usually __name__)
    template_folder='templates', # 3. Tells Flask where to find templates for this blueprint
)

from . import routes  