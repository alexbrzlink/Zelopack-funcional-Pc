from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Importando as rotas depois de definir o blueprint
from blueprints.dashboard.routes import *