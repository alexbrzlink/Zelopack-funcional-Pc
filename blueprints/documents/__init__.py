import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

documents_bp = Blueprint('documents', __name__)

from blueprints.documents import routes