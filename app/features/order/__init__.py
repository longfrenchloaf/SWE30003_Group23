# artproject/app/features/order/__init__.py
from flask import Blueprint

order_bp = Blueprint('order', __name__, template_folder='templates')

from . import routes 