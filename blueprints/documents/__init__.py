import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

documents_bp = Blueprint('documents', __name__)

# Importação das rotas após a definição do blueprint para evitar importações circulares
from blueprints.documents import routes