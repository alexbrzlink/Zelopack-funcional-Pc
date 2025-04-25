import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

calculos_bp = Blueprint('calculos', __name__, template_folder='templates', url_prefix='/calculos')

from . import routes