"""
Script para sincronizar o esquema do banco de dados.
Este script verifica se há alterações nos modelos do SQLAlchemy e atualiza o banco de dados conforme necessário.
"""
import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def sync_database():
    """Sincroniza o banco de dados com os modelos atuais."""
    from app import app, db
    import models

    with app.app_context():
        try:
            # Verificar conexão com o banco
            try:
                connection = db.engine.connect()
                connection.close()
                logger.info("Conexão com o banco de dados estabelecida com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
                return False

            # Criar uma nova conexão especificamente para operações DDL
            # para evitar problemas com transações abortadas
            from sqlalchemy import create_engine
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            
            # Implementação básica para tabelas que sabemos que existem
            try:
                # Verificar se as colunas necessárias existem em Report
                columns_to_check = [
                    "client_id", "sample_id", "template_id", "version", "parent_id",
                    "has_print_version", "print_version_path", "additional_metrics",
                    "analysis_start_time", "analysis_end_time"
                ]
                
                for column in columns_to_check:
                    # Usar conexão independente para cada operação para evitar problemas de transação
                    with engine.connect() as conn:
                        try:
                            # Verificar se a coluna existe
                            conn.execute(text(f"SELECT {column} FROM report LIMIT 1"))
                            logger.info(f"Coluna {column} já existe na tabela report.")
                        except Exception:
                            # A coluna não existe, adicionar
                            try:
                                data_type = "TEXT"
                                if column in ["version", "client_id", "sample_id", "template_id", "parent_id"]:
                                    data_type = "INTEGER"
                                elif column in ["has_print_version"]:
                                    data_type = "BOOLEAN DEFAULT FALSE"
                                elif column in ["analysis_start_time", "analysis_end_time"]:
                                    data_type = "TIMESTAMP"
                                
                                # Execute o ALTER TABLE em uma transação independente
                                conn.execute(text(f"ALTER TABLE report ADD COLUMN {column} {data_type}"))
                                conn.commit()
                                logger.info(f"Coluna {column} adicionada à tabela report.")
                            except Exception as e:
                                logger.error(f"Erro ao adicionar coluna {column}: {str(e)}")
                                conn.rollback()
            except Exception as e:
                logger.error(f"Erro ao verificar colunas da tabela Report: {str(e)}")
                # Não precisamos de rollback aqui pois cada operação tem sua própria transação

            # Verificar se as tabelas para os novos modelos existem
            tables_to_check = [
                "report_template", "report_attachment", "report_comment", 
                "report_history", "custom_formula", "calculation_result",
                "client", "sample", "notification"
            ]
            
            for table in tables_to_check:
                with engine.connect() as conn:
                    try:
                        # Verificar se a tabela existe
                        conn.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                        logger.info(f"Tabela {table} já existe.")
                    except Exception:
                        logger.info(f"Tabela {table} não existe. Será criada com db.create_all().")
            
            # Criar todas as tabelas que não existem
            db.create_all()
            logger.info("Estrutura do banco de dados atualizada.")
            
            # Adicionar dados iniciais se necessário
            initialize_default_data(db, models)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao sincronizar banco de dados: {str(e)}")
            return False

def initialize_default_data(db, models):
    """Inicializa o banco de dados com dados padrão."""
    try:
        # Usuário admin padrão
        admin_exists = models.User.query.filter_by(username='admin').first()
        if not admin_exists:
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
        # Cliente padrão
        if models.Client.query.count() == 0:
            default_clients = [
                models.Client(
                    name="Zelopack Sucos", 
                    type="cliente",
                    contact_name="João Silva",
                    email="contato@zelopacksucos.com.br",
                    phone="(11) 9999-8888",
                    is_active=True
                ),
                models.Client(
                    name="Fornecedor ABC",
                    type="fornecedor",
                    contact_name="Maria Oliveira",
                    email="maria@fornecedorabc.com.br",
                    phone="(11) 7777-6666",
                    is_active=True
                )
            ]
            db.session.add_all(default_clients)
            db.session.commit()
            logger.info("Clientes padrão adicionados.")
    except Exception as e:
        logger.error(f"Erro ao adicionar clientes: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    print("Iniciando sincronização do banco de dados...")
    success = sync_database()
    
    if success:
        print("Sincronização concluída com sucesso!")
        sys.exit(0)
    else:
        print("Ocorreram erros durante a sincronização. Verifique os logs.")
        sys.exit(1)