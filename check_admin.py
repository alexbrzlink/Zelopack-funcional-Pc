import logging
logger = logging.getLogger(__name__)

from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    logger.debug(f'Usuário admin existe: {user is not None}')
    if user:
        logger.debug(f'Senha válida: {user.check_password("Alex")}')
        logger.debug(f'Nome: {user.name}')
        logger.debug(f'Email: {user.email}')
        logger.debug(f'Ativo: {user.is_active}')
