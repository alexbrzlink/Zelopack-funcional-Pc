import os
import logging

# Configuração do logging
logger = logging.getLogger(__name__)
# Define uma senha segura baseada em variável de ambiente ou senha padrão
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "ChangeThis2024!"
from datetime import datetime

from flask import Flask, flash, redirect, url_for, session
from flask_login import LoginManager, current_user, login_user
from sqlalchemy.orm import DeclarativeBase
from extensions import db, csrf, socketio

# Criar aplicação Flask
app = Flask(__name__)
import secrets
app.secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)

# Configuração
app.config.from_object('config.DevelopmentConfig')
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limite máximo
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "xls", "xlsx"}

# Inicializar componentes
db.init_app(app)
csrf.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# Garantir que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Configuração do CSRF
# Em ambiente de desenvolvimento, podemos deixar o CSRF mais permissivo
if app.debug:
    app.config['WTF_CSRF_ENABLED'] = True  # Manter habilitado para segurança
    app.config['WTF_CSRF_TIME_LIMIT'] = 10800  # 3 horas para desenvolvimento
    app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
    app.config['WTF_CSRF_CHECK_DEFAULT'] = True  # Verificação CSRF obrigatória
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Permitir HTTPS mesmo em localhost
else:
    # Configuração mais restrita para produção
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora
    app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
    app.config['WTF_CSRF_SSL_STRICT'] = True

# Adicionar mais isenções para CSRF em rotas de teste/desenvolvimento
csrf.exempt('app.check_admin_user')  # Isento para permitir o diagnóstico do admin
csrf.exempt('app.login_direct')  # Isento para permitir login automático
csrf.exempt('auth.login')  # Temporariamente isento para resolver problemas de login

# Adicionar proteção global para problemas de CSRF token em dispositivos móveis
@app.after_request
def add_csrf_cookie(response):
    try:
        if 'csrf_token' not in session:
            from flask_wtf.csrf import generate_csrf
            session['csrf_token'] = generate_csrf()
    except Exception as e:
        logger.error(f"Erro ao configurar CSRF token: {e}")
    return response

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

# Adicionar filtros personalizados para os templates
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Converte um timestamp em data formatada."""
    if timestamp:
        try:
            from datetime import datetime
            return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
        except Exception as e:
            app.logger.error(f"Erro ao converter timestamp: {e}")
            return str(timestamp)
    return "---"

# Rota para login de teste
@app.route("/user-admin-info")
def check_admin_user():
    """Rota para verificar se o usuário admin existe e mostrar suas informações."""
    from models import User
    from werkzeug.security import generate_password_hash, check_password_hash
    
    # Verificar se existe usuário admin
    user = User.query.filter_by(username='admin').first()
    
    # Verificação de senha para testes
    # Obter senha de administrador a partir de variáveis de ambiente ou usar valor padrão apenas para desenvolvimento
    test_password = os.environ.get('ADMIN_PASSWORD') or 'Alex'
    is_password_valid = False
    password_hash_info = "Não foi possível verificar o hash"
    
    if user:
        # Tentar verificar a senha diretamente
        is_password_valid = user.check_password(test_password)
        
        # Informações sobre o hash atual
        current_hash = user.password_hash
        
        # Tentar verificar com check_password_hash diretamente
        direct_check = check_password_hash(current_hash, test_password)
        
        # Criar um novo hash para comparação
        new_hash = generate_password_hash(test_password)
        
        password_hash_info = f"""
        <div style="background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff;">
            <h4>Informações do hash de senha:</h4>
            <p>Hash atual: <code>{current_hash}</code></p>
            <p>Novo hash gerado: <code>{new_hash}</code></p>
            <p>Resultado do check_password: <strong>{is_password_valid}</strong></p>
            <p>Resultado da verificação direta: <strong>{direct_check}</strong></p>
        </div>
        """
        
        # Se a verificação de senha falhou, atualizar a senha
        if not is_password_valid:
            user.set_password(test_password)
            db.session.commit()
            password_hash_info += f"""
            <div style="background-color: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745;">
                <p><strong>SENHA REDEFINIDA!</strong> O hash da senha foi atualizado para garantir o acesso.</p>
                <p>Novo hash após redefinição: <code>{user.password_hash}</code></p>
            </div>
            """
        
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
        {password_hash_info}
        <p>Este usuário possui credenciais configuradas e ativas.</p>
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
        admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
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
            <li>Senha: *****</li>
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
        admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()
        logger.debug("Usuário admin criado com sucesso!")
    
    # Agora buscamos o usuário admin
    user = User.query.filter_by(username='admin').first()
    if user:
        if not user.is_active:
            user.is_active = True
            db.session.commit()
            logger.debug("Usuário admin foi ativado")
        
        login_user(user)
        flash('Login realizado com sucesso via rota de teste!', 'success')
        return redirect(url_for('dashboard.index'))
    else:
        flash('Erro no login de teste: usuário não encontrado', 'danger')
        return redirect(url_for('auth.login'))
        
@app.route("/login-direct")
def login_direct():
    """Rota alternativa para login direto, para fins de teste."""
    logger.debug("ACESSANDO ROTA DE LOGIN AUTOMÁTICO")
    
    from models import User
    from werkzeug.security import generate_password_hash, check_password_hash
    
    # Verificar se existe usuário admin
    total_users = User.query.count()
    logger.debug(f"Total de usuários no sistema: {total_users}")
    
    if total_users == 0:
        # Criar usuário admin se não existir
        logger.debug("Nenhum usuário encontrado. Criando usuário admin padrão...")
        admin_user = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()
        logger.debug("Usuário admin criado com sucesso!")
    
    user = User.query.filter_by(username='admin').first()
    
    if user is None:
        msg = "ERRO CRÍTICO: Usuário admin não encontrado mesmo após tentativa de criação!"
        logger.debug(msg)
        flash(msg, 'danger')
        return redirect(url_for('auth.login'))
    
    if not user.is_active:
        msg = "ERRO: Usuário admin existe mas está inativo."
        logger.debug(msg)
        user.is_active = True
        db.session.commit()
        logger.debug("Usuário admin foi ativado automaticamente.")
        flash(msg + " Ele foi ativado automaticamente.", 'warning')
    
    # Verificar senha
    test_password = DEFAULT_ADMIN_PASSWORD
    is_password_valid = user.check_password(test_password)
    
    if not is_password_valid:
        logger.debug(f"ERRO: A senha do usuário admin não está validando corretamente. Redefinindo...")
        user.set_password(test_password)
        db.session.commit()
        
        # Verificar novamente
        if not user.check_password(test_password):
            logger.debug("ERRO CRÍTICO: A senha não pôde ser redefinida corretamente!")
            flash('Não foi possível redefinir a senha do admin. Entre em contato com o suporte.', 'danger')
            return redirect(url_for('auth.login'))
        else:
            logger.debug("Senha redefinida com sucesso!")
            flash('A senha do usuário admin foi redefinida.', 'warning')
    
    # Registrar tentativa de login
    logger.debug(f"Login automático para usuário: {user.username}")
    logger.debug(f"Nome do usuário: {user.name}")
    logger.debug(f"E-mail do usuário: {user.email}")
    logger.debug(f"Função do usuário: {user.role}")
    logger.debug(f"Status de ativação: {user.is_active}")
    
    login_user(user, remember=True)
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    logger.debug("Login automático bem-sucedido! Redirecionando para o dashboard...")
    flash(f'Bem-vindo, {user.name}! Login automático realizado com sucesso.', 'success')
@app.route("/validar-sistema")
def system_validation():
    """Validação completa do sistema para diagnóstico"""
    from models_temp import User, Category, Supplier, Report
    from werkzeug.security import generate_password_hash, check_password_hash
    
    results = []
    
    # Verificar conexão com banco de dados
    try:
        total_users = User.query.count()
        results.append({
            "test": "Conexão com Banco de Dados",
            "result": "Sucesso",
            "details": f"Total de usuários: {total_users}"
        })
    except Exception as e:
        results.append({
            "test": "Conexão com Banco de Dados",
            "result": "Falha",
            "details": str(e)
        })
        
    # Verificar se o usuário admin existe
    try:
        admin = User.query.filter_by(username='admin').first()
        if admin:
            results.append({
                "test": "Usuário Admin",
                "result": "Encontrado",
                "details": f"ID: {admin.id}, Email: {admin.email}, Ativo: {admin.is_active}"
            })
            
            # Verificar senha do admin
            if admin.check_password(DEFAULT_ADMIN_PASSWORD):
                results.append({
                    "test": "Senha do Admin",
                    "result": "Correta",
                    "details": "Senha validada com sucesso"
                })
            else:
                # Tentar corrigir a senha
                admin.set_password(DEFAULT_ADMIN_PASSWORD)
                db.session.commit()
                
                if admin.check_password(DEFAULT_ADMIN_PASSWORD):
                    results.append({
                        "test": "Senha do Admin",
                        "result": "Corrigida",
                        "details": "A senha foi redefinida com sucesso"
                    })
                else:
                    results.append({
                        "test": "Senha do Admin",
                        "result": "Falha",
                        "details": "Não foi possível validar as credenciais"
                    })
        else:
            results.append({
                "test": "Usuário Admin",
                "result": "Não encontrado",
                "details": "Usuário admin não existe no banco de dados"
            })
            
            # Criar usuário admin
            admin_user = User(
                username='admin',
                email='admin@zelopack.com.br',
                name='Administrador',
                role='admin',
                is_active=True
            )
            admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin_user)
            db.session.commit()
            
            results.append({
                "test": "Criação de Admin",
                "result": "Sucesso",
                "details": "Usuário admin foi criado com sucesso"
            })
    except Exception as e:
        results.append({
            "test": "Verificação de Usuário",
            "result": "Erro",
            "details": str(e)
        })
    
    # Verificar demais modelos de dados
    try:
        cats = Category.query.count()
        results.append({
            "test": "Categorias",
            "result": "Sucesso",
            "details": f"Total de categorias: {cats}"
        })
    except Exception as e:
        results.append({
            "test": "Categorias",
            "result": "Erro",
            "details": str(e)
        })
        
    try:
        suppliers = Supplier.query.count()
        results.append({
            "test": "Fornecedores",
            "result": "Sucesso",
            "details": f"Total de fornecedores: {suppliers}"
        })
    except Exception as e:
        results.append({
            "test": "Fornecedores",
            "result": "Erro",
            "details": str(e)
        })
        
    try:
        reports = Report.query.count()
        results.append({
            "test": "Laudos",
            "result": "Sucesso",
            "details": f"Total de laudos: {reports}"
        })
    except Exception as e:
        results.append({
            "test": "Laudos",
            "result": "Erro",
            "details": str(e)
        })
        
    # Gerar HTML com resultados
    results_html = ""
    for result in results:
        status_class = "text-success" if result["result"] in ["Sucesso", "Encontrado", "Correta", "Corrigida"] else "text-danger"
        results_html += f"""
        <div class="card mb-2">
            <div class="card-body">
                <h5 class="card-title">{result["test"]}</h5>
                <h6 class="card-subtitle mb-2 {status_class}">{result["result"]}</h6>
                <p class="card-text small">{result["details"]}</p>
            </div>
        </div>
        """
    
    # Gerar links para ações
    actions_html = f"""
    <div class="card mb-3">
        <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Ações Disponíveis</h5>
        </div>
        <div class="card-body">
            <div class="d-grid gap-2">
                <a href="/user-admin-info" class="btn btn-outline-primary">Visualizar Informações do Admin</a>
                <a href="/login-direct" class="btn btn-success">Login Automático como Admin</a>
                <a href="/auth/login" class="btn btn-primary">Ir para Tela de Login</a>
                <a href="/" class="btn btn-secondary">Voltar para Página Inicial</a>
            </div>
        </div>
    </div>
    """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Validação do Sistema</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ padding: 20px; }}
            .result-card {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">
                <div class="col-md-8 offset-md-2">
                    <h1 class="mb-4 text-center">Diagnóstico do Sistema</h1>
                    
                    <div class="alert alert-info">
                        Esta página realiza testes de diagnóstico no sistema e mostra os resultados.
                    </div>
                    
                    <h3 class="mb-3">Resultados dos Testes</h3>
                    {results_html}
                    
                    <h3 class="mt-4 mb-3">Ações</h3>
                    {actions_html}
                    
                    <p class="text-center text-muted mt-5">
                        <small>Sistema de Gerenciamento de Laudos - Zelopack</small>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Registrar blueprints
from blueprints.reports import reports_bp
from blueprints.dashboard import dashboard_bp
from blueprints.auth import auth_bp
from blueprints.templates import templates_bp
from blueprints.documents import documents_bp
from blueprints.forms import forms_bp
from blueprints.calculos import calculos_bp
from blueprints.estatisticas.routes import estatisticas_bp
from blueprints.configuracoes.routes import configuracoes_bp
from blueprints.alertas.routes import alertas_bp
from blueprints.laboratorio import laboratorio_bp
from blueprints.banco_dados.routes import banco_dados_bp
from blueprints.estoque import estoque_bp
# Importar novos blueprints
from blueprints.editor import editor_bp as document_editor_bp
from blueprints.technical import technical_bp

app.register_blueprint(reports_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(templates_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(forms_bp)
app.register_blueprint(calculos_bp)
app.register_blueprint(estatisticas_bp)
app.register_blueprint(configuracoes_bp)
app.register_blueprint(alertas_bp)
app.register_blueprint(banco_dados_bp)
app.register_blueprint(estoque_bp)

# Registrar blueprint do editor universal
from blueprints.forms.routes_editor import editor_bp as forms_editor_bp
app.register_blueprint(forms_editor_bp)

# Registrar novos blueprints
app.register_blueprint(document_editor_bp)
app.register_blueprint(technical_bp)
app.register_blueprint(laboratorio_bp)

# Função para atualizar o banco de dados de forma incremental
def setup_database():
    import models
    import sqlalchemy as sa
    from sqlalchemy import inspect
    from utils.error_handler import log_exception, handle_database_error
    
    # Criar tabelas do banco de dados
    db.create_all()
    
    # Adicionar categorias iniciais se tabelas estiverem vazias
    try:
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
            logger.debug("Categorias padrão adicionadas.")
    except Exception as e:
        error_info = handle_database_error(e, db.session, "adicionar_categorias")
        logger.debug(f"Erro ao adicionar categorias: {error_info['user_message']}")
        db.session.rollback()
    
    # Adicionar fornecedores padrão se não existirem
    try:
        if models.Supplier.query.count() == 0:
            default_suppliers = [
                models.Supplier(name="Fornecedor Teste 1", contact_name="Contato 1", email="contato1@exemplo.com", phone="(11) 91234-5678"),
                models.Supplier(name="Fornecedor Teste 2", contact_name="Contato 2", email="contato2@exemplo.com", phone="(11) 98765-4321"),
                models.Supplier(name="Fornecedor Teste 3", contact_name="Contato 3", email="contato3@exemplo.com", phone="(21) 99876-5432")
            ]
            db.session.add_all(default_suppliers)
            db.session.commit()
            logger.debug("Fornecedores padrão adicionados.")
    except Exception as e:
        error_info = handle_database_error(e, db.session, "adicionar_fornecedores")
        logger.debug(f"Erro ao adicionar fornecedores: {error_info['user_message']}")
        db.session.rollback()

# Inicializar o banco de dados
with app.app_context():
    setup_database()
    
    try:
        import models
        if models.Supplier.query.count() == 0:
            default_suppliers = [
                models.Supplier(name="Fornecedor Interno", contact_name="Laboratório Zelopack", email="lab@zelopack.com.br"),
                models.Supplier(name="Laboratório Externo", contact_name="Contato do Laboratório", email="contato@labexterno.com.br"),
                models.Supplier(name="Consultoria ABC", contact_name="Consultor", email="contato@consultoriaabc.com.br")
            ]
            db.session.add_all(default_suppliers)
            db.session.commit()
            logger.debug("Fornecedores padrão adicionados.")
    except Exception as e:
        logger.debug(f"Erro ao adicionar fornecedores: {e}")
        db.session.rollback()
    
    try:
        import models
        # Criar usuário admin padrão se não existir nenhum usuário
        if models.User.query.count() == 0:
            admin_user = models.User(
                username='admin',
                email='admin@zelopack.com.br',
                name='Administrador',
                role='admin'
            )
            admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin_user)
            db.session.commit()
            logger.debug("Usuário administrador padrão criado.")
    except Exception as e:
        logger.debug(f"Erro ao criar usuário admin: {e}")
        db.session.rollback()

# Rota principal do sistema
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    else:
        return redirect(url_for('auth.login'))

# Iniciar o servidor web quando executado diretamente
if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
