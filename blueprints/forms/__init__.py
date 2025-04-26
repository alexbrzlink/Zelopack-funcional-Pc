import logging
logger = logging.getLogger(__name__)

from flask import Blueprint

forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

# Importação das rotas após a definição do blueprint para evitar importações circulares
from . import routes
from . import routes_editor
from . import routes_autofill