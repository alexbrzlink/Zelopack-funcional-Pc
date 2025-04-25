from flask import Blueprint

reports_bp = Blueprint('reports', __name__, url_prefix='/reports', template_folder='../../templates/reports')

from blueprints.reports.routes import *
