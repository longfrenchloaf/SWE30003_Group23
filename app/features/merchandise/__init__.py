from flask import Blueprint

merchandise_bp = Blueprint('merchandise', __name__, template_folder='templates')

from . import routes