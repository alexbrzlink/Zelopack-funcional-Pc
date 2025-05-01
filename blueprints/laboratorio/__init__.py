from flask import Blueprint

laboratorio_bp = Blueprint('laboratorio', __name__, url_prefix='/laboratorio')

from . import routes