import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from extensions import db, csrf
from models import User

# Criar aplicau00e7u00e3o Flask
app = Flask(__name__)

# Configurau00e7u00e3o
app.config.from_object('config.DevelopmentConfig')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'postgresql://postgres:190321@localhost:5432/zelopack_db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limite mu00e1ximo
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "xls", "xlsx"}

# Inicializar o banco de dados
db.init_app(app)

# Inicializar CSRF
csrf.init_app(app)

# Configurar o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, fau00e7a login para acessar esta pu00e1gina.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rota principal
@app.route('/')
def index():
    return render_template('index_simple.html', title="ZeloPack - Sistema Iniciado")

# Rota de testes
@app.route('/teste-db')
def teste_db():
    try:
        # Testar conexu00e3o com o banco de dados
        users_count = User.query.count()
        return f"<h1>Conexu00e3o com o banco de dados OK!</h1><p>Total de usu00e1rios: {users_count}</p>"
    except Exception as e:
        return f"<h1>Erro ao conectar ao banco de dados</h1><p>Erro: {str(e)}</p>"

# Rota para criar tabelas
@app.route('/setup-db')
def setup_db():
    try:
        with app.app_context():
            db.create_all()
            
            # Verificar se existe usu00e1rio admin
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Criar usu00e1rio admin
                admin_password = os.environ.get('ADMIN_PASSWORD', 'Zelopack19')
                admin = User(
                    username='admin',
                    email='admin@zelopack.com',
                    name='Administrador',
                    role='admin'
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                
        return "<h1>Banco de dados configurado com sucesso!</h1><p>Usu00e1rio admin criado.</p>"
    except Exception as e:
        return f"<h1>Erro ao configurar banco de dados</h1><p>Erro: {str(e)}</p>"

# Iniciar aplicau00e7u00e3o
if __name__ == '__main__':
    # Garantir que a pasta de uploads exista
    os.makedirs(os.path.join(os.getcwd(), "uploads"), exist_ok=True)
    
    # Iniciar servidor
    app.run(debug=True)
