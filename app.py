import os
import logging
from datetime import datetime

from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user
from flask_wtf.csrf import CSRFProtect
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

# Inicializar proteção CSRF, mas desabilitar para desenvolvimento
csrf = CSRFProtect()
csrf.init_app(app)
# Desabilitamos CSRF para facilitar os testes
app.config['WTF_CSRF_ENABLED'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Criar algumas isenções para CSRF (para rota de login direto)
csrf.exempt('blueprints.auth.login_direct')

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

# Rota para login de teste
@app.route("/user-admin-info")
def check_admin_user():
    """Rota para verificar se o usuário admin existe e mostrar suas informações."""
    from models import User
    
    # Verificar se existe usuário admin
    user = User.query.filter_by(username='admin').first()
    
    if user:
        info = f"""
        <h3>Informações do usuário admin:</h3>
        <ul>
            <li>ID: {user.id}</li>
            <li>Username: {user.username}</li>
            <li>Email: {user.email}</li>
            <li>Nome: {user.name}</li>
            <li>Função: {user.role}</li>
            <li>Ativo: {user.is_active}</li>
            <li>Último login: {user.last_login}</li>
        </ul>
        <p>A senha atual configurada para este usuário é: <strong>Alex</strong></p>
        <p><a href="/login-direct">Entrar com este usuário automaticamente</a></p>
        <p><a href="/auth/login">Ir para tela de login manual</a></p>
        """
    else:
        # Criar usuário admin
        admin_user = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin_user.set_password('Alex')
        db.session.add(admin_user)
        db.session.commit()
        info = f"""
        <h3>Usuário admin não existia e foi criado:</h3>
        <ul>
            <li>Username: admin</li>
            <li>Email: admin@zelopack.com.br</li>
            <li>Nome: Administrador</li>
            <li>Função: admin</li>
            <li>Ativo: True</li>
            <li>Senha: Alex</li>
        </ul>
        <p><a href="/login-direct">Entrar com este usuário automaticamente</a></p>
        <p><a href="/auth/login">Ir para tela de login manual</a></p>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Informações do Usuário Admin</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h2 {{ color: #2c3e50; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin-bottom: 8px; }}
            a {{ display: inline-block; margin-top: 10px; 
                padding: 8px 16px; background-color: #3498db; 
                color: white; text-decoration: none; border-radius: 4px; }}
            a:hover {{ background-color: #2980b9; }}
        </style>
    </head>
    <body>
        <h2>Status do Usuário Administrador</h2>
        {info}
    </body>
    </html>
    """

@app.route("/login-test")
def login_test():
    # Primeiro, precisamos verificar se já existe algum usuário
    from models import User
    
    # Se não existir usuário, criamos um
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin_user.set_password('Alex')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
    
    # Agora buscamos o usuário admin
    user = User.query.filter_by(username='admin').first()
    if user:
        if not user.is_active:
            user.is_active = True
            db.session.commit()
            print("Usuário admin foi ativado")
        
        login_user(user)
        flash('Login realizado com sucesso via rota de teste!', 'success')
        return redirect(url_for('dashboard.index'))
    else:
        flash('Erro no login de teste: usuário não encontrado', 'danger')
        return redirect(url_for('auth.login'))

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
        admin_user.set_password('Alex')  # Em produção, usar senha mais segura!
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário administrador padrão criado.")
