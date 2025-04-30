from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from flask_caching import Cache
import os


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# Inicialização do app e das extensões
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "zelopack-dev-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Inicialização do Socket.IO para funcionalidade em tempo real
socketio = SocketIO(app)

# Inicialização do Cache
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///zelopack.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401

    db.create_all()

# Registrar blueprints
from editor import editor_bp
from technical import technical_bp

app.register_blueprint(editor_bp)
app.register_blueprint(technical_bp)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')