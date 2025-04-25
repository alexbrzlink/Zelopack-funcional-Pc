import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python3
from app import app, db

def fix_database():
    logger.debug("Tentando restaurar a sessão do banco de dados...")
    with app.app_context():
        try:
            db.session.rollback()
            logger.debug("Sessão do banco de dados restaurada com sucesso!")
        except Exception as e:
            logger.debug(f"Erro ao restaurar a sessão: {e}")

if __name__ == "__main__":
    fix_database()