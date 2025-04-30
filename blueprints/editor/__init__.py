from flask import Blueprint

editor_bp = Blueprint('document_editor', __name__)

from . import routes