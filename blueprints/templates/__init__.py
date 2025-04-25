import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

from . import routes