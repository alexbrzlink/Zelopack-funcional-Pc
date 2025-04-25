import os
import logging
from datetime import datetime

from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.orm import DeclarativeBase

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Classe base para modelos SQLAlchemy
class Base(DeclarativeBase):
    pass

# Inicializar SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Criar aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "zelopack-dev-key")

# Configurar banco de dados
database_url = os.environ.get("DATABASE_URL")
# PostgreSQL usa "postgres://" por padrão, mas SQLAlchemy prefere "postgresql://"
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///zelopack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configurações para upload de arquivos
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limite máximo
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "xls", "xlsx"}

# Garantir que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Inicializar o banco de dados
db.init_app(app)

# Configurar o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Adicionar variáveis de contexto para todas as templates
@app.context_processor
def inject_variables():
    return {
        'current_year': datetime.now().year
    }

# Registrar blueprints
from blueprints.reports import reports_bp
from blueprints.dashboard import dashboard_bp
from blueprints.auth import auth_bp

app.register_blueprint(reports_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)

# Criar tabelas do banco de dados
with app.app_context():
    import models
    db.create_all()
    
    # Adicionar categorias e fornecedores iniciais se tabelas estiverem vazias
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
        print("Categorias padrão adicionadas.")
    
    if models.Supplier.query.count() == 0:
        default_suppliers = [
            models.Supplier(name="Fornecedor Interno", contact="Laboratório Zelopack", email="lab@zelopack.com.br"),
            models.Supplier(name="Laboratório Externo", contact="Contato do Laboratório", email="contato@labexterno.com.br"),
            models.Supplier(name="Consultoria ABC", contact="Consultor", email="contato@consultoriaabc.com.br")
        ]
        db.session.add_all(default_suppliers)
        db.session.commit()
        print("Fornecedores padrão adicionados.")
    
    # Criar usuário admin padrão se não existir nenhum usuário
    if models.User.query.count() == 0:
        admin_user = models.User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin'
        )
        admin_user.set_password('admin123')  # Em produção, usar senha mais segura!
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário administrador padrão criado.")
