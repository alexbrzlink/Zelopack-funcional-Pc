from flask import Blueprint

documents_bp = Blueprint('documents', __name__)

from blueprints.documents import routes