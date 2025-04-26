import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Importação das rotas após a definição do blueprint para evitar importações circulares
from . import routes