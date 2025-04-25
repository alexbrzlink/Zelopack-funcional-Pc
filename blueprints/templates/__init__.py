from flask import Blueprint

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

from . import routes