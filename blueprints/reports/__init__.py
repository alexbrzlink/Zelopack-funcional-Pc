from flask import Blueprint

reports_bp = Blueprint('reports', __name__, url_prefix='/reports', 
                       template_folder='../../templates/reports')

# Importando as rotas depois de definir o blueprint
from blueprints.reports.routes import *
