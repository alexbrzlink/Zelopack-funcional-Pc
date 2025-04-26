import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

reports_bp = Blueprint('reports', __name__, url_prefix='/reports', 
                       template_folder='../../templates/reports')

# Importação das rotas após a definição do blueprint para evitar importações circulares
from . import routes
