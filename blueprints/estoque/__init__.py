from flask import Blueprint

estoque_bp = Blueprint('estoque', __name__, url_prefix='/estoque', template_folder='templates')

from . import routes