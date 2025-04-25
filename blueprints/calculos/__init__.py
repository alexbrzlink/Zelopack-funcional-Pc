from flask import Blueprint

calculos_bp = Blueprint('calculos', __name__, url_prefix='/calculos', template_folder='templates')

from . import routes