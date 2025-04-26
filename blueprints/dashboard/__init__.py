import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Importação das rotas após a definição do blueprint para evitar importações circulares
from . import routes