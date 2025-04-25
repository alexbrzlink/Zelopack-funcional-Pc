"""
Script para criação das tabelas do banco de dados.
Execute este script quando precisar criar ou atualizar as tabelas do banco de dados.
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Cria todas as tabelas no banco de dados."""
    from app import app, db
    import models

    with app.app_context():
        try:
            # Criar todas as tabelas definidas nos modelos
            db.create_all()
            logger.info("Todas as tabelas foram criadas com sucesso.")
            
            # Adicionar dados iniciais
            initialize_default_data(db, models)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            return False

def initialize_default_data(db, models):
    """Inicializa o banco de dados com dados padrão."""
    try:
        # Categorias padrão
        if models.Category.query.count() == 0:
            default_categories = [
                models.Category(name="Microbiológico", description="Laudos de análises microbiológicas"),
                models.Category(name="Físico-Químico", description="Laudos de análises físico-químicas"),
                models.Category(name="Sensorial", description="Laudos de análises sensoriais"),
                models.Category(name="Embalagem", description="Laudos de análises de embalagens"),
                models.Category(name="Shelf-life", description="Laudos de testes de vida útil")
            ]
            db.session.add_all(default_categories)
            db.session.commit()
            logger.info("Categorias padrão adicionadas.")
    except Exception as e:
        logger.error(f"Erro ao adicionar categorias: {str(e)}")
        db.session.rollback()

    try:
        # Fornecedores padrão
        if models.Supplier.query.count() == 0:
            default_suppliers = [
                models.Supplier(name="Fornecedor Interno", contact_name="Laboratório Zelopack", email="lab@zelopack.com.br"),
                models.Supplier(name="Laboratório Externo", contact_name="Contato do Laboratório", email="contato@labexterno.com.br"),
                models.Supplier(name="Consultoria ABC", contact_name="Consultor", email="contato@consultoriaabc.com.br")
            ]
            db.session.add_all(default_suppliers)
            db.session.commit()
            logger.info("Fornecedores padrão adicionados.")
    except Exception as e:
        logger.error(f"Erro ao adicionar fornecedores: {str(e)}")
        db.session.rollback()

    try:
        # Usuário admin padrão
        if models.User.query.count() == 0:
            admin_user = models.User(
                username='admin',
                email='admin@zelopack.com.br',
                name='Administrador',
                role='admin',
                is_active=True
            )
            admin_user.set_password('Alex')
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Usuário administrador padrão criado.")
    except Exception as e:
        logger.error(f"Erro ao criar usuário admin: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    print("Iniciando criação das tabelas do banco de dados...")
    success = create_all_tables()
    
    if success:
        print("Processo concluído com sucesso!")
        sys.exit(0)
    else:
        print("Ocorreram erros durante o processo. Verifique os logs.")
        sys.exit(1)