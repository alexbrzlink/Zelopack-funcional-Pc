import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

# Importação das rotas após a definição do blueprint para evitar importações circulares
from . import routes