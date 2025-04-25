import os
import logging
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

# Adicionar variáveis de contexto para todas as templates
@app.context_processor
def inject_variables():
    return {
        'current_year': datetime.now().year
    }

# Registrar blueprints
from blueprints.reports import reports_bp
from blueprints.dashboard import dashboard_bp

app.register_blueprint(reports_bp)
app.register_blueprint(dashboard_bp)

# Criar tabelas do banco de dados
with app.app_context():
    import models
    db.create_all()
