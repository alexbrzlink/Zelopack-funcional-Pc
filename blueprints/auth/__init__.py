import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import routes