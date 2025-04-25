from flask import Blueprint

templates_bp = Blueprint('templates', __name__)

from blueprints.templates import routes