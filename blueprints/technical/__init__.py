from flask import Blueprint

technical_bp = Blueprint('technical', __name__)

from . import routes