import logging
logger = logging.getLogger(__name__)

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def run_migration():
    """
    Executa a migração do banco de dados para adicionar novas colunas.
    """
    with app.app_context():
        try:
            # Verificar se as colunas já existem antes de tentar adicioná-las
            logger.debug("Verificando esquema atual do banco de dados...")
            columns = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'reports'"))
            existing_columns = [row[0] for row in columns]
            
            # Adicionando novas colunas para análises físico-químicas se não existirem
            new_columns = [
                ('brix', 'FLOAT'),
                ('ph', 'FLOAT'),
                ('acidity', 'FLOAT'),
                ('manufacturing_date', 'DATE'),
                ('expiration_date', 'DATE'),
                ('report_time', 'TIME')
            ]
            
            for column, dtype in new_columns:
                if column not in existing_columns:
                    logger.debug(f"Adicionando coluna {column} ({dtype})...")
                    db.session.execute(text(f"ALTER TABLE reports ADD COLUMN {column} {dtype}"))
            
            # Commit das alterações
            db.session.commit()
            logger.debug("Migração concluída com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            logger.debug(f"Erro durante a migração: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    # Executar a migração
    success = run_migration()
    
    # Sair com código de status apropriado
    sys.exit(0 if success else 1)