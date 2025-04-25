"""
Script para atualizar o esquema do banco de dados para a tabela Supplier.
Este script adiciona os novos campos ao modelo Supplier.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL de conexão com o banco de dados
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    logger.error("Variável de ambiente DATABASE_URL não configurada.")
    sys.exit(1)

def update_supplier_schema():
    """Atualiza o esquema da tabela supplier com novos campos."""
    try:
        # Criar engine para conectar ao banco de dados
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        
        # Iniciar transação
        trans = conn.begin()
        
        try:
            # Verificar colunas existentes
            columns = []
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'supplier'"))
            for row in result:
                columns.append(row[0])
            
            logger.info(f"Colunas existentes na tabela 'supplier': {columns}")
            
            # Adicionar coluna contact_name se não existir e transformar dados da coluna contact
            if 'contact' in columns and 'contact_name' not in columns:
                logger.info("Adicionando coluna contact_name e migrando dados da coluna contact...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN contact_name VARCHAR(150)"))
                conn.execute(text("UPDATE supplier SET contact_name = contact"))
            elif 'contact_name' not in columns:
                logger.info("Adicionando coluna contact_name...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN contact_name VARCHAR(150)"))
            
            # Adicionar endereço se não existir
            if 'address' not in columns:
                logger.info("Adicionando coluna address...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN address TEXT"))
            
            # Adicionar observações se não existir
            if 'notes' not in columns:
                logger.info("Adicionando coluna notes...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN notes TEXT"))
            
            # Adicionar tipo se não existir
            if 'type' not in columns:
                logger.info("Adicionando coluna type...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN type VARCHAR(50)"))
            
            # Adicionar timestamps se não existirem
            if 'created_at' not in columns:
                logger.info("Adicionando coluna created_at...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            
            if 'updated_at' not in columns:
                logger.info("Adicionando coluna updated_at...")
                conn.execute(text("ALTER TABLE supplier ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            
            # Remover coluna contact se contact_name existe
            if 'contact' in columns and 'contact_name' in columns:
                logger.info("Removendo coluna contact (antiga)...")
                conn.execute(text("ALTER TABLE supplier DROP COLUMN contact"))
            
            # Commit das alterações
            trans.commit()
            logger.info("Migração concluída com sucesso!")
            
        except Exception as e:
            # Rollback em caso de erro
            trans.rollback()
            logger.error(f"Erro durante a atualização do esquema: {str(e)}")
            raise
        finally:
            # Fechar conexão
            conn.close()
            
    except SQLAlchemyError as e:
        logger.error(f"Erro de conexão com o banco de dados: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Iniciando atualização do esquema da tabela supplier...")
    update_supplier_schema()
    logger.info("Atualização concluída.")