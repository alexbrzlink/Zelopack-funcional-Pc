import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

from . import routes