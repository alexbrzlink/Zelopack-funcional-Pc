from flask import Blueprint

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

from . import routes