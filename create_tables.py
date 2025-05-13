#!/usr/bin/env python3
"""
Script para criação e atualização das tabelas do banco de dados.
Execute este script da raiz do projeto (mesma pasta de main.py/app.py) para garantir que imports funcionem corretamente.
"""
import sys
import os
import logging

# Ajusta o diretório de trabalho e o path para evitar imports duplicados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Garante que o script seja executado a partir da raiz do projeto
os.chdir(BASE_DIR)

# Remove possíveis duplicações no sys.path
if BASE_DIR in sys.path:
    sys.path = [p for p in sys.path if os.path.abspath(p) != BASE_DIR]
# Insere BASE_DIR uma única vez
sys.path.insert(0, BASE_DIR)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Importa a aplicação e o db de app.py (ou main.py se preferir)
try:
    from app import app, db
    logger.debug("Importado app e db de app.py")
except ModuleNotFoundError:
    try:
        from main import app, db
        logger.debug("Importado app e db de main.py")
    except ModuleNotFoundError:
        logger.error("Não foi possível importar 'app' nem 'main'. Verifique se os arquivos existem em %s", BASE_DIR)
        sys.exit(1)


def create_all_tables():
    """Cria todas as tabelas definidas nos modelos e inicializa dados padrão."""
    with app.app_context():
        try:
            logger.debug("Criando tabelas no banco...")
            db.create_all()
            logger.info("Tabelas criadas ou já existentes.")
            initialize_default_data()
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False


def initialize_default_data():
    """Insere categorias, fornecedores e usuário admin padrão se não existirem."""
    # Importa modelos localmente para evitar mapeamentos duplicados
    import models
    Category = models.Category
    Supplier = models.Supplier
    User = models.User

    # Categorias padrão
    if Category.query.count() == 0:
        defaults = [
            ("Microbiológico", "Laudos de análises microbiológicas"),
            ("Físico-Químico", "Laudos de análises físico-químicas"),
            ("Sensorial", "Laudos de análises sensoriais"),
            ("Embalagem", "Laudos de análises de embalagens"),
            ("Shelf-life", "Laudos de testes de vida útil")
        ]
        for name, desc in defaults:
            db.session.add(Category(name=name, description=desc))
        db.session.commit()
        logger.info("Categorias padrão adicionadas.")

    # Fornecedores padrão
    if Supplier.query.count() == 0:
        defaults = [
            ("Fornecedor Interno", "Laboratório Zelopack", "lab@zelopack.com.br"),
            ("Laboratório Externo", "Contato do Laboratório", "contato@labexterno.com.br"),
            ("Consultoria ABC", "Consultor", "contato@consultoriaabc.com.br")
        ]
        for name, contact, email in defaults:
            db.session.add(Supplier(name=name, contact_name=contact, email=email))
        db.session.commit()
        logger.info("Fornecedores padrão adicionados.")

    # Usuário admin padrão
    if User.query.count() == 0:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeThis2024!')
        admin = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        logger.info("Usuário administrador padrão criado.")


def main():
    logger.debug("Iniciando processo de criação/verificação de tabelas...")
    success = create_all_tables()
    if success:
        logger.debug("Processo concluído com sucesso!")
        sys.exit(0)
    else:
        logger.debug("Ocorreram erros durante o processo. Verifique os logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()

