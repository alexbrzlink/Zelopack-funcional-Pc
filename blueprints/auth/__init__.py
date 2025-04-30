"""
Blueprint de autenticação.
Gerencia autenticação, autorização e recursos avançados de segurança.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from . import routes